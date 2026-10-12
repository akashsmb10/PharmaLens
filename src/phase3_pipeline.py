"""Read-only Phase 2 input verification and reproducible Phase 3 execution."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
import duckdb
import numpy as np
import pandas as pd
from .common import ROOT,sha256,write_json
from .sql_analytics import EXPORTS,atomic_csv,snapshot_sources
from .statistical_analysis import summaries,regional_comparisons,safe_ratio
from .trend_analysis import trend_tables
from .seasonality_analysis import seasonality_tables
from .cost_diagnostics import cost_outputs
from .anomaly_diagnostics import diagnostics
from .robustness_analysis import robustness,forecast_diagnostics
from .phase3_visualizations import charts

def protected_snapshot(root=ROOT):
    files=set(root/path for path in snapshot_sources(root))
    files.add(root/'data/processed/pharma.duckdb')
    for directory in ['outputs/tables','outputs/charts/phase2','outputs/validation','sql']:
        files.update(p for p in (root/directory).glob('*') if p.is_file())
    # Reports produced by this or a later phase are not Phase 1–2 inputs.
    files.update(p for p in (root/'docs').glob('*.md') if not p.name.startswith(('PHASE3_','PHASE4_','PHASE5_','PHASE6_','PHASE7_')) and p.name not in {'FORECASTING_READINESS.md','PROJECT_ARCHITECTURE.md','DATA_SOURCES_AND_LICENSES.md','REPRODUCIBILITY_GUIDE.md'})
    return {str(p.relative_to(root)).replace('\\','/'):sha256(p) for p in sorted(files)}

def load_inputs(root=ROOT):
    guard=json.loads((root/'outputs/validation/phase2_source_guard.json').read_text(encoding='utf-8'))
    if snapshot_sources(root)!=guard['protected_sha256']:
        raise AssertionError('Phase 1 source hashes differ from verified Phase 2 baseline')
    audit=json.loads((root/'outputs/validation/phase2_final_audit.json').read_text(encoding='utf-8'))
    if not audit['passed']: raise ValueError('Phase 2 final audit did not pass')
    loaded={}; checked=[]
    with duckdb.connect(str(root/'data/processed/pharma.duckdb'),read_only=True) as con:
        con.execute('SET threads=1')
        schema=con.execute('SELECT table_schema,table_name FROM information_schema.tables ORDER BY 1,2').df()
        for name,view in EXPORTS.items():
            path=root/f'outputs/tables/{name}.parquet'
            saved=pd.read_parquet(path)
            actual=con.execute(f'SELECT * FROM phase2.{view} ORDER BY ALL').df()
            pd.testing.assert_frame_equal(saved.reset_index(drop=True),actual.reset_index(drop=True),check_dtype=False,atol=1e-10,rtol=0)
            expected=audit['exports'][name]
            if sha256(path)!=expected['parquet_sha256']:
                raise AssertionError(f'Phase 2 export hash changed: {name}')
            loaded[name]=saved; checked.append({'table':name,'rows':len(saved),'verified_against_sql':True})
        detail=con.execute('SELECT * FROM phase2.vw_fact_enriched ORDER BY month,region_code,presentation_key').df()
        columns=con.execute('DESCRIBE phase2.fact_monthly_prescribing').df()
    for f in loaded.values():
        if 'month' in f: f['month']=pd.to_datetime(f.month)
    calendar=pd.DatetimeIndex(loaded['national_monthly_trends'].month.sort_values()).as_unit('ns')
    if not calendar.equals(pd.date_range(calendar.min(),calendar.max(),freq='MS')):
        raise ValueError('National calendar incomplete')
    coverage=loaded['series_coverage']
    keys=['region_code','region_name','presentation_key','presentation_name','unit_of_measure']
    grid=coverage[keys].merge(pd.DataFrame({'month':calendar}),how='cross')
    measures=detail[['month','region_code','presentation_key','prescription_items','net_ingredient_cost_gbp','total_quantity']]
    grid=grid.merge(measures,on=['month','region_code','presentation_key'],how='left',validate='one_to_one')
    grid['ingredient_cost_per_item_gbp']=safe_ratio(grid.net_ingredient_cost_gbp,grid.prescription_items)
    populations={'national':(loaded['national_monthly_trends'],[]),
                 'regional':(loaded['regional_monthly_trends'],['region_code','region_name']),
                 'presentation':(loaded['presentation_monthly_trends'],['presentation_key','presentation_name','unit_of_measure']),
                 'region_presentation':(grid,keys)}
    evidence={'database':'data/processed/pharma.duckdb','schemas':sorted(schema.table_schema.unique().tolist()),
              'fact_columns':columns.to_dict('records'),'export_checks':checked,
              'fact_rows':len(detail),'candidate_grid_rows':len(grid),'missing_cells':int(grid.prescription_items.isna().sum()),
              'total_items':int(detail.prescription_items.sum()),'total_nic_gbp':float(detail.net_ingredient_cost_gbp.sum()),
              'settings_yaml':'Absent; existing config/dataset.json and config/phase2.json retained',
              'date_type':'DuckDB DATE; pandas datetime64[ns]',
              'metric_contract':'Items product occurrences, NIC GBP before discounts, weighted NIC/item; no mixed-unit quantity totals'}
    return loaded,populations,calendar,evidence

def run_phase3(root=ROOT,make_charts=True,make_reports=True):
    before=protected_snapshot(root)
    validation=root/'outputs/phase3/validation'; validation.mkdir(parents=True,exist_ok=True)
    source_guard=validation/'source_guard.json'
    if source_guard.exists() and json.loads(source_guard.read_text(encoding='utf-8'))!=before:
        raise AssertionError('Protected inputs changed since Phase 3 baseline')
    if not source_guard.exists(): write_json(source_guard,before)
    loaded,populations,calendar,evidence=load_inputs(root)
    write_json(validation/'input_verification.json',evidence)
    tables={}
    tables['descriptive_statistics'],tables['growth_rate_distributions']=summaries(populations,calendar)
    trends=trend_tables(populations,calendar)
    tables['trend_summary']=trends['national']; tables['regional_trend_summary']=trends['regional']; tables['presentation_trend_summary']=trends['presentation']
    seasonal=seasonality_tables(populations['national'][0],calendar)
    for name,f in zip(['seasonality_summary','monthly_seasonal_indices','autocorrelation_diagnostics','stl_components'],seasonal): tables[name]=f
    tables['regional_statistical_comparisons']=regional_comparisons(populations['regional'][0])
    cost=cost_outputs(populations,loaded['cost_change_decomposition'])
    for name,f in zip(['cost_per_item_trends','presentation_cost_change_contributions','regional_cost_change_contributions','cost_decomposition_diagnostics'],cost): tables[name]=f
    tables['anomaly_diagnostics'],tables['extreme_value_review_phase3']=diagnostics(populations['region_presentation'][0],loaded['extreme_value_review'],calendar)
    tables['robustness_summary'],tables['sensitivity_results'],tables['diagnostic_excluded_rows']=robustness(populations,loaded['extreme_value_review'],loaded['series_coverage'],calendar)
    tables['forecasting_diagnostics']=forecast_diagnostics(populations,calendar,loaded['forecast_candidate_series'])
    files={}
    for name,f in tables.items():
        path=root/f'outputs/phase3/tables/{name}.csv'; atomic_csv(f,path)
        parquet=path.with_suffix('.parquet'); f.to_parquet(parquet,index=False)
        files[name]={'rows':len(f),'columns':f.columns.tolist(),'csv_sha256':sha256(path),'parquet_sha256':sha256(parquet)}
    paths=charts(tables,populations,root) if make_charts else []
    result={'input_verification':evidence,'tables':files,'charts':paths,
            'decomposition_max_residual_gbp':float(tables['cost_decomposition_diagnostics'].reconciliation_residual_gbp.abs().max()),
            'original_extreme_flags_retained':len(tables['extreme_value_review_phase3']),
            'protected_inputs_unchanged':protected_snapshot(root)==before,
            'missing_cells_preserved':int(populations['region_presentation'][0].prescription_items.isna().sum())==evidence['missing_cells'],
            'forecast_models_trained':0}
    if not result['protected_inputs_unchanged'] or not result['missing_cells_preserved'] or result['decomposition_max_residual_gbp']>.01:
        raise AssertionError('Phase 3 validation failed')
    result['passed']=True
    write_json(validation/'pipeline_summary.json',result)
    if make_reports:
        from .phase3_reports import reports
        reports(tables,loaded,result,root)
    print(f"Phase 3: {len(tables)} tables, {len(paths)} charts, {result['original_extreme_flags_retained']} original flags retained",flush=True)
    return result

def final_audit(root=ROOT):
    first=run_phase3(root); second=run_phase3(root)
    if first['tables']!=second['tables']: raise AssertionError('Table rerun differs')
    from .phase3_notebooks import build_and_execute
    notebooks=build_and_execute(root)
    command=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',
             f'--basetemp=outputs/phase3/validation/tests_tmp_{uuid.uuid4().hex[:8]}',
             '--junitxml=outputs/phase3/validation/all_tests.xml']
    tests=subprocess.run(command,cwd=root,text=True,capture_output=True)
    (root/'outputs/phase3/validation/test_execution.log').write_text(tests.stdout+tests.stderr,encoding='utf-8')
    print(tests.stdout,flush=True)
    suites=ET.parse(root/'outputs/phase3/validation/all_tests.xml').getroot().findall('testsuite')
    counts={key:sum(int(s.get(key,0)) for s in suites) for key in ['tests','failures','errors','skipped']}
    result={**second,'notebooks':notebooks,'tests':counts,'test_exit_code':tests.returncode,'repeated_tables_identical':True}
    result['independent_findings_verification']=verify_findings(root)
    result['protected_inputs_unchanged']=protected_snapshot(root)==json.loads((root/'outputs/phase3/validation/source_guard.json').read_text(encoding='utf-8'))
    result['passed']=tests.returncode==0 and result['protected_inputs_unchanged'] and all(n['error_outputs']==0 and n['unexecuted_code_cells']==0 for n in notebooks)
    # Integration tests deliberately omit charts/reports; restore the complete execution summary.
    write_json(root/'outputs/phase3/validation/pipeline_summary.json',second)
    write_json(root/'outputs/phase3/validation/final_audit.json',result)
    from .phase3_reports import audit_report
    audit_report(result,root)
    if not result['passed']: raise AssertionError('Final audit failed; inspect test_execution.log')
    return result

def verify_findings(root=ROOT):
    """Independent fact-based effects and closed-form Shapley verify production/report claims."""
    loaded,pops,calendar,evidence=load_inputs(root)
    detail=pops['region_presentation'][0].dropna(subset=['prescription_items']).copy()
    detail['year']=detail.month.dt.year
    annual=detail.groupby('year')[['prescription_items','net_ingredient_cost_gbp']].sum()
    claims=json.loads((root/'outputs/phase3/validation/business_claims.json').read_text(encoding='utf-8'))
    checks=[]
    def check(name,a,b,tolerance=1e-10):
        if not np.allclose(a,b,atol=tolerance,rtol=0,equal_nan=True): raise AssertionError(f'Independent claim failed: {name}')
        checks.append({'check':name,'passed':True,'absolute_tolerance':tolerance})
    for column,claim in [('prescription_items','items_2025_growth_pct'),('net_ingredient_cost_gbp','nic_2025_growth_pct')]:
        check(claim,100*(annual.loc[2025,column]/annual.loc[2024,column]-1),claims[claim])
    monthly=detail.groupby('month').prescription_items.sum().reindex(calendar)
    t=np.arange(len(calendar),dtype=float)
    slope=np.sum((t-t.mean())*(monthly-monthly.mean()))/np.sum((t-t.mean())**2)
    check('national_item_ols_slope',slope,claims['national_item_ols_slope'],1e-7)
    category=detail.groupby(['year','presentation_key'])[['prescription_items','net_ingredient_cost_gbp']].sum()
    a=category.loc[2024].sort_index(); b=category.loc[2025].sort_index()
    v0=a.prescription_items.sum(); v1=b.prescription_items.sum()
    s0=a.prescription_items/v0; s1=b.prescription_items/v1
    p0=a.net_ingredient_cost_gbp/a.prescription_items; p1=b.net_ingredient_cost_gbp/b.prescription_items
    volume=(v1-v0)*(np.dot(s0,p0)/3+(np.dot(s1,p0)+np.dot(s0,p1))/6+np.dot(s1,p1)/3)
    mix=np.dot(s1-s0,v0*p0/3+(v1*p0+v0*p1)/6+v1*p1/3)
    within=np.dot(p1-p0,v0*s0/3+(v1*s0+v0*s1)/6+v1*s1/3)
    for key,value in [('cost_volume_effect_gbp',volume),('cost_mix_effect_gbp',mix),('cost_within_presentation_effect_gbp',within)]:
        check(key,value,claims[key],.01)
    delta=annual.loc[2025,'net_ingredient_cost_gbp']-annual.loc[2024,'net_ingredient_cost_gbp']
    check('cost_change_gbp',delta,claims['cost_change_gbp'],.01)
    check('closed_form_cost_identity',volume+mix+within,delta,.01)
    totals=detail.groupby('presentation_key').prescription_items.sum().sort_values(ascending=False)
    check('top_four_item_share_pct',100*totals.head(4).sum()/totals.sum(),claims['top_four_item_share_pct'])
    check('regions_growing',(detail.groupby(['region_code','year']).prescription_items.sum().unstack()[2025]>detail.groupby(['region_code','year']).prescription_items.sum().unstack()[2024]).sum(),claims['regions_growing'],0)
    excluded=detail[detail.presentation_key!=totals.index[0]].groupby('year').prescription_items.sum()
    check('item_growth_excluding_largest_presentation_pct',100*(excluded.loc[2025]/excluded.loc[2024]-1),claims['item_growth_excluding_largest_presentation_pct'])
    out=pd.read_parquet(root/'outputs/phase3/tables/extreme_value_review_phase3.parquet')
    old=loaded['extreme_value_review'].sort_values(['month','region_code','presentation_key','metric'])
    new=out.sort_values(['month','region_code','presentation_key','metric'])
    for column in ['month','region_code','presentation_key','metric']:
        if old[column].astype(str).tolist()!=new[column].astype(str).tolist(): raise AssertionError('Original flag key mismatch')
    check('original_flag_values',old.value.to_numpy(),new.observed_value.to_numpy(),1e-10)
    check('original_flag_classifications',out.groupby('classification').size().sort_index().to_numpy(),
          pd.Series(claims['original_flag_classifications']).sort_index().to_numpy(),0)
    for path in (root/'outputs/phase3/tables').glob('*.parquet'):
        f=pd.read_parquet(path)
        if 'total_quantity' in f.columns: raise AssertionError('Quantity aggregate exposed by Phase 3 output')
    result={'checks':checks,'passed_checks':len(checks),'source':'read-only Phase 2 fact; independent closed-form Shapley and covariance slope'}
    write_json(root/'outputs/phase3/validation/independent_findings_verification.json',result)
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--audit',action='store_true'); args=parser.parse_args()
    final_audit() if args.audit else run_phase3()
