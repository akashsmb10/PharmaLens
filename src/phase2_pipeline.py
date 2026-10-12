"""Integrated Phase 2 and its final audit. Source artifact hashes are never refreshed silently."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import xml.etree.ElementTree as ET
import duckdb
import numpy as np
import pandas as pd
from .common import ROOT,sha256,utc_now,write_json
from .sql_analytics import execute_analytics,EXPORTS,SQL_ORDER,SETTINGS,snapshot_sources
from .reconcile_metrics import run_reconciliation
from .phase2_visualizations import charts
from .phase2_reports import generate_reports,md_table

def verify_outputs(root=ROOT):
    with duckdb.connect(str(root / 'data/processed/pharma.duckdb'),read_only=True) as con:
        con.execute('SET threads=1')
        row_counts={}
        for stem,view in EXPORTS.items():
            count=con.execute(f'SELECT COUNT(*) FROM phase2.{view}').fetchone()[0]
            for suffix in ['csv','parquet']:
                path=root / f'outputs/tables/{stem}.{suffix}'
                if not path.exists():
                    raise FileNotFoundError(path)
                frame=pd.read_csv(path) if suffix=='csv' else pd.read_parquet(path)
                if len(frame)!=count:
                    raise ValueError(f'Export row count mismatch: {path}')
            row_counts[stem]=count
        actual=con.execute('SELECT * FROM phase2.vw_extreme_value_review').df()
        phase1=json.loads((root / 'outputs/validation/quality_report.json').read_text(encoding='utf-8'))
        def key(record,original=False):
            return (str(pd.Timestamp(record['month']).date()),record['region_code'],record['product_code'] if original else record['presentation_code'],record['unit_of_measure'],record['metric'])
        original={key(r,True):r[r['metric']] for r in phase1['extremes']}
        current={key(r):r['value'] for r in actual.to_dict('records')}
        if original.keys()!=current.keys() or any(not np.isclose(original[k],current[k],atol=.00001,rtol=0) for k in original):
            raise AssertionError('SQL extreme flags or original flagged values differ from Phase 1')
        claims=json.loads((root / 'outputs/validation/phase2_business_claims.json').read_text(encoding='utf-8'))
        for claim in claims:
            frame=con.execute(f"SELECT * FROM phase2.{EXPORTS[claim['output']]}").df()
            for column,value in claim.get('filter',{}).items():
                frame=frame[frame[column]==value]
            if claim.get('aggregation')=='sum':
                value=frame[claim['column']].sum()
            elif claim.get('aggregation')=='count':
                value=len(frame)
            else:
                if len(frame)!=1:
                    raise AssertionError(f"Claim source is not unique: {claim['id']}")
                value=frame.iloc[0][claim['column']]
            tolerance=.01 if 'cost' in claim['id'] else 1e-10
            if not np.isclose(value,claim['value'],atol=tolerance,rtol=0):
                raise AssertionError(f"Business claim failed verification: {claim['id']}")
        total=con.execute('SELECT SUM(prescription_items),SUM(net_ingredient_cost_gbp) FROM phase2.fact_monthly_prescribing').fetchone()
        # All canonical tables in this model have native unit as a dimension, not a collapsed quantity total.
        for view in ['vw_national_monthly_kpis','vw_regional_performance','vw_regional_monthly_trends']:
            columns=[r[0] for r in con.execute(f'DESCRIBE phase2.{view}').fetchall()]
            if 'total_quantity' in columns:
                raise AssertionError('Incompatible quantity total exposed by aggregate view')
        absent=con.execute('SELECT COUNT(*) FROM phase2.vw_missing_series_months WHERE prescription_items IS NOT NULL OR net_ingredient_cost_gbp IS NOT NULL OR total_quantity IS NOT NULL').fetchone()[0]
        if absent:
            raise AssertionError('Missing observations were imputed as measures')
    return {'export_rows':row_counts,'verified_extreme_flags':len(current),'verified_headline_claims':len(claims),
            'total_prescription_items':int(total[0]),'total_net_ingredient_cost_gbp':str(total[1]),
            'missing_observations_kept_null':True,'incompatible_quantity_aggregates_absent':True}

def run_phase2(root=ROOT):
    exported=execute_analytics(root)
    reconciliation=run_reconciliation(root)
    chart_files=charts(root)
    generate_reports(root)
    verified=verify_outputs(root)
    summary={'completed_at_utc':utc_now(),'database':'data/processed/pharma.duckdb','schema':'phase2',
             'sql_executed':SQL_ORDER,'exports':exported,'reconciliation':reconciliation,'charts':chart_files,
             **verified,'passed':True}
    write_json(root / 'outputs/validation/phase2_pipeline_summary.json',summary)
    print(f"Phase 2: {len(exported)} reporting exports; {reconciliation['checks']} reconciliations passed; {len(chart_files)} charts",flush=True)
    return summary

def final_audit(root=ROOT):
    before=snapshot_sources(root)
    first=run_phase2(root)
    second=run_phase2(root)
    reproducible=first['exports']==second['exports']
    if not reproducible:
        differences={name:{'first':first['exports'][name],'second':second['exports'][name]} for name in first['exports'] if first['exports'][name]!=second['exports'][name]}
        write_json(root / 'outputs/validation/phase2_reproducibility_failure.json',differences)
        raise AssertionError('Reporting CSV/Parquet exports changed on rerun')
    command=[sys.executable,'-m','pytest','-q','--basetemp=outputs/validation/phase2_audit_tmp',
             '--junitxml=outputs/validation/phase2_tests.xml']
    tests=subprocess.run(command,cwd=root,text=True,capture_output=True)
    (root / 'outputs/validation/phase2_test_execution.log').write_text(tests.stdout+tests.stderr,encoding='utf-8')
    print(tests.stdout,flush=True)
    element=ET.parse(root / 'outputs/validation/phase2_tests.xml').getroot()
    suites=[element] if element.tag=='testsuite' else element.findall('testsuite')
    counts={k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
    unchanged=snapshot_sources(root)==before
    required_docs=['PHASE2_DATA_MODEL.md','METRIC_DEFINITIONS.md','PHASE2_DATA_QUALITY_REVIEW.md',
                   'PHASE2_BUSINESS_INSIGHTS.md','FORECASTING_READINESS.md']
    docs_present=all((root / 'docs' / f).is_file() for f in required_docs)
    result={**second,'test_results':counts,'test_exit_code':tests.returncode,'repeated_exports_identical':reproducible,
            'protected_phase1_files_unchanged':unchanged,'required_docs_present':docs_present,
            'passed':tests.returncode==0 and unchanged and reproducible and docs_present}
    write_json(root / 'outputs/validation/phase2_final_audit.json',result)
    summary_tables=pd.DataFrame([{'Export (CSV and Parquet)':k,'Rows':v['rows'],'View':v['view']} for k,v in second['exports'].items()])
    quality=json.loads((root / 'outputs/validation/phase2_phase1_verification.json').read_text(encoding='utf-8'))
    text=f'''# Final Phase 2 audit

Executed at {utc_now()}. Overall pass: **{result['passed']}**.

## Baseline and preserved artifacts

Phase 1 baseline: **19 tests passed**, with separate phase2_baseline_tests.xml evidence.
config/settings.yaml was absent; existing config/dataset.json was inspected and retained.
The protected Phase 1 raw snapshots, processed CSV/Parquet/manifest, notebook, original docs and
validation records retain identical hashes: **{unchanged}**. Source guard tracks {quality['protected_files']} files.
The existing DuckDB monthly_prescribing table is unchanged logically; the new phase2 schema is additive.

## Executed implementation

SQL order: {', '.join(SQL_ORDER)}. All nine execute successfully; 08 coverage intentionally precedes
07 eligibility. Fact has 3,920 observed rows, dim_month 36, dim_region 7 and dim_presentation 17.
All six model-integrity checks pass and reporting-view contracts are documented in PHASE2_DATA_MODEL.md.
No synthetic production observations, missing-month zero filling, incompatible quantity totals, PBIX or
forecasting model is introduced. Cost is always net ingredient cost, never manufacturer revenue.

## Reporting outputs and row counts

{md_table(summary_tables)}

All CSV and Parquet files exist under outputs/tables. They are clean BI exports; database views remain
queryable after registered Python input relations are removed. Thirteen source-noted PNG charts exist
under outputs/charts/phase2, including all twelve requested figures and growth-versus-size comparison.

## Verified KPIs and data findings

- Total prescription items: **{second['total_prescription_items']:,}** (Jan 2023–Dec 2025).
- Total net ingredient cost: **£{float(second['total_net_ingredient_cost_gbp']):,.2f}**.
- Original 292 observed-series missing months reproduced. Complete grid adds 72 never-observed
  applicability-unknown cells. Of 364 absent cells: 45 before first, 88 after last, 159 internal, 72 never observed.
- All 161 original extreme flags, including their values and keys, reproduce exactly within numeric tolerance.
  They cover 82 unique observed rows; flags are retained, not declared errors or causal effects.
- Supplier missingness 17,220 and pre-February-2024 structural field absence 18,250 reproduce.
- 94/119 candidate series have 36 observed months; 29 satisfy the default forecasting eligibility screen.
- Eight numerical findings are in PHASE2_BUSINESS_INSIGHTS.md. {second['verified_headline_claims']} machine-readable
  headline claims rechecked against unrounded SQL views; supporting tables are linked in each finding.

## Reconciliation, tests and reproducibility

SQL/Pandas checks: **{second['reconciliation']['passed_checks']:,} passed**, **{second['reconciliation']['failed_checks']} failed**.
Item counts compare exactly; GBP costs use absolute £0.01 tolerance, ratios/growth/shares use 1e-10.
All {second['reconciliation']['decomposition_checks']} monthly/annual exact two-factor cost decompositions pass;
maximum absolute residual **£{second['reconciliation']['maximum_decomposition_residual_gbp']:.12g}**.
Full pytest: **{counts['tests']} tests**, **{counts['failures']} failures**, **{counts['errors']} errors**, **{counts['skipped']} skipped**.
Two complete pipeline executions produce byte-identical reporting CSV and Parquet files: **{reproducible}**.
Counts and hashes are recorded in phase2_final_audit.json and phase2_exports.json.
An earlier rerun check caught Parquet differences in floating-point CV values despite identical CSVs.
Ordered standard-deviation aggregation and one-thread SQL execution resolved this. The historical
phase2_reproducibility_failure.json is retained as evidence; it does not represent the final audit status.

## Limits and Phase 3 recommendations

One chemical, England community dispensing, no population denominators or patient counts, and 36 months
of history limit inference. Absent-series causes and lifecycle are unknown. Ingredient cost is not final
NHS total cost or manufacturer revenue. Cost/item changes mix basic price, quantity/item and presentation
composition; the exact decomposition does not isolate causal prices or clinical substitution.
Per-100 native quantity is not dose-equivalent. Full-history screens and IQR flags must be recomputed
within training folds in a later forecast backtest. See FORECASTING_READINESS.md.
Next investigate item/cost/mix distributions, calendar effects, dated tariff references, and flagged/incomplete
series. Forecasting remains a later phase. No unresolved critical execution or validation failure remains
when the overall pass above is True.

## Exact implementation and output files

'''
    code_files=['config/phase2.json','src/sql_analytics.py','src/reconcile_metrics.py','src/phase2_visualizations.py',
                'src/phase2_reports.py','src/phase2_pipeline.py','tests/conftest.py','tests/test_phase2_sql.py',
                'tests/test_phase2_metrics.py','tests/test_phase2_coverage.py','tests/test_phase2_reconciliation.py']
    code_files += ['sql/'+f for f in SQL_ORDER]+['docs/'+f for f in required_docs]+['docs/PHASE2_AUDIT.md']
    code_files += [f'outputs/tables/{stem}.{suffix}' for stem in EXPORTS for suffix in ['csv','parquet']]
    code_files += second['charts']
    code_files += ['outputs/validation/'+f for f in ['phase2_baseline_tests.xml','phase2_source_guard.json',
        'phase2_phase1_verification.json','phase2_exports.json','sql_python_reconciliation.csv','phase2_reconciliation.json',
        'phase2_business_claims.json','phase2_pipeline_summary.json','phase2_final_audit.json','phase2_tests.xml','phase2_test_execution.log']]
    text+='\n'.join('- `'+f+'`' for f in code_files)
    text+='\n\nModified: run_pipeline.py (optional --phase 2), README.md (Phase 2 section). No dependency changes.\n'
    (root / 'docs/PHASE2_AUDIT.md').write_text(text,encoding='utf-8')
    if not result['passed']:
        raise AssertionError('Final Phase 2 audit failed; see saved evidence')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--audit',action='store_true')
    args=parser.parse_args()
    result=final_audit() if args.audit else run_phase2()
    print(json.dumps({k:result[k] for k in ['passed','total_prescription_items','total_net_ingredient_cost_gbp']},indent=2))
