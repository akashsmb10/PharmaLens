"""Phase 2 SQL execution, guarded source artifacts, transactional refresh and deterministic exports."""
import itertools
import json
import os
from pathlib import Path
import duckdb
import numpy as np
import pandas as pd
from .common import ROOT, CONFIG, sha256, utc_now, write_json
from .validate import audit

SETTINGS = json.loads((ROOT / 'config/phase2.json').read_text(encoding='utf-8'))
SQL_ORDER = ['01_schema.sql','02_data_quality.sql','03_national_trends.sql','04_regional_performance.sql',
             '05_presentation_performance.sql','06_cost_analytics.sql','08_series_coverage.sql',
             '07_region_presentation_intelligence.sql','09_reporting_views.sql']
EXPORTS = {
 'national_monthly_trends': 'vw_national_monthly_kpis', 'national_annual_trends': 'vw_national_annual_kpis',
 'regional_performance': 'vw_regional_performance', 'regional_monthly_trends': 'vw_regional_monthly_trends',
 'regional_annual_trends': 'vw_regional_annual_trends', 'presentation_performance': 'vw_presentation_performance',
 'presentation_monthly_trends': 'vw_presentation_monthly_trends', 'presentation_annual_trends': 'vw_presentation_annual_trends',
 'presentation_concentration': 'vw_presentation_concentration', 'cost_analytics': 'vw_cost_analytics',
 'cost_change_decomposition': 'vw_cost_change_decomposition', 'region_presentation_summary': 'vw_region_presentation_summary',
 'region_presentation_mix': 'vw_region_presentation_mix', 'forecast_candidate_series': 'vw_forecast_candidates',
 'series_coverage': 'vw_series_coverage', 'missing_series_months': 'vw_missing_series_months',
 'extreme_value_review': 'vw_extreme_value_review', 'threshold_sensitivity': 'vw_threshold_sensitivity',
 'presentation_regional_costs': 'vw_presentation_regional_costs', 'model_quality_checks': 'vw_model_quality'
}

def atomic_csv(df, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + '.tmp')
    df.to_csv(tmp, index=False, float_format='%.12g', date_format='%Y-%m-%d', lineterminator='\n')
    os.replace(tmp, path)

def protected_paths(root=ROOT):
    required = ['data/processed/monthly_prescribing.csv','data/processed/monthly_prescribing.parquet',
                'data/processed/source_rows.parquet','data/processed/acquisition_manifest.json','data/processed/pharma.duckdb',
                'outputs/validation/quality_report.json','outputs/validation/extreme_observations.csv',
                'outputs/validation/final_audit.json','outputs/validation/pytest_results.xml',
                'docs/DATA_DICTIONARY.md','docs/DATA_SOURCE_EVALUATION.md','docs/INITIAL_DATA_ASSESSMENT.md',
                'docs/PHASE1_AUDIT.md','notebooks/01_data_understanding.ipynb','config/dataset.json']
    missing = [name for name in required if not (root / name).is_file()]
    if missing:
        raise FileNotFoundError(f'Required Phase 1 artifacts missing: {missing}')
    paths = [root / name for name in required if not name.endswith('.duckdb')]
    paths += sorted((root / 'data/raw').glob('*.json'))
    paths += [root / 'outputs/tables' / name for name in ['descriptive_statistics.csv','geographic_coverage.csv','monthly_totals.csv','product_distribution.csv']]
    return paths

def snapshot_sources(root=ROOT):
    return {str(p.relative_to(root)).replace('\\','/'): sha256(p) for p in protected_paths(root)}

def verify_phase1(root=ROOT):
    hashes = snapshot_sources(root)
    guard = root / 'outputs/validation/phase2_source_guard.json'
    if guard.exists():
        expected = json.loads(guard.read_text(encoding='utf-8'))['protected_sha256']
        if hashes != expected:
            raise ValueError('Protected Phase 1 artifacts changed since the Phase 2 baseline')
    else:
        write_json(guard, {'created_at_utc': utc_now(), 'protected_sha256': hashes,
                          'baseline_phase1_tests': '19 passed; phase2_baseline_tests.xml',
                          'settings_yaml': 'Not present; existing configuration is config/dataset.json'})
    manifest = json.loads((root / 'data/processed/acquisition_manifest.json').read_text(encoding='utf-8'))
    if manifest['mode'] != 'observed':
        raise ValueError('Phase 2 requires observed NHSBSA data, not the synthetic fallback')
    if manifest['processed_sha256'] != sha256(root / 'data/processed/monthly_prescribing.csv'):
        raise ValueError('Phase 1 processed CSV provenance checksum failed')
    for evidence in manifest['files']:
        if sha256(root / evidence['file']) != evidence['sha256']:
            raise ValueError(f"Raw provenance checksum failed: {evidence['file']}")
    df = pd.read_parquet(root / 'data/processed/monthly_prescribing.parquet')
    detailed = pd.read_parquet(root / 'data/processed/source_rows.parquet')
    recomputed = audit(detailed, df)
    if not recomputed['passed']:
        raise ValueError('Recomputed Phase 1 quality gate failed')
    expected_quality = json.loads((root / 'outputs/validation/quality_report.json').read_text(encoding='utf-8'))
    actual_counts = {c['check']: c['count'] for c in recomputed['checks']}
    previous_counts = {c['check']: c['count'] for c in expected_quality['checks']}
    if actual_counts != previous_counts:
        raise ValueError('Phase 1 quality findings no longer match its validated report')
    if not df.data_origin.eq('observed_nhsbsa').all():
        raise ValueError('Unexpected data lineage')
    if not np.allclose(df.nic_gbp * 100, np.round(df.nic_gbp * 100), atol=.0001, rtol=0):
        raise ValueError('NIC cannot safely be represented as source GBP cents')
    write_json(root / 'outputs/validation/phase2_phase1_verification.json', {
        'verified_at_utc': utc_now(), 'source_shape': list(detailed.shape), 'monthly_shape': list(df.shape),
        'monthly_dtypes': df.dtypes.astype(str).to_dict(), 'source_schema_columns': manifest['source_columns'],
        'findings': actual_counts, 'protected_files': len(hashes), 'all_phase1_checks_match': True})
    return df, hashes

def build_model(con, monthly, start_month=CONFIG['start_month'], end_month=CONFIG['end_month'], settings=SETTINGS, sql_root=ROOT / 'sql'):
    # Stable floating-point accumulation and byte-identical exports across repeated executions.
    con.execute('SET threads=1')
    if monthly.duplicated(['month','product_code','region_code','unit_of_measure']).any():
        raise ValueError('Duplicate source fact business keys')
    if not monthly['items'].notna().all() or not monthly['items'].mod(1).eq(0).all():
        raise ValueError('Prescription items must be populated integer counts before BIGINT conversion')
    for code, label in [('product_code','product_name'),('region_code','region_name')]:
        if monthly.groupby(code)[label].nunique().gt(1).any():
            raise ValueError(f'Ambiguous dimension mapping for {code}')
    parameters = pd.DataFrame([{'start_month': pd.Timestamp(start_month), 'end_month': pd.Timestamp(end_month),
                               **{k:settings[k] for k in ['minimum_history_months','minimum_total_items','minimum_coverage_pct','maximum_internal_gaps']}}])
    sensitivity = pd.DataFrame(list(itertools.product(settings['sensitivity_minimum_history'], settings['sensitivity_minimum_total_items'], settings['sensitivity_coverage_pct'])),
                               columns=['minimum_history_months','minimum_total_items','minimum_coverage_pct'])
    con.register('input_monthly', monthly)
    con.register('input_parameters', parameters)
    con.register('input_sensitivity', sensitivity)
    con.execute('BEGIN TRANSACTION')
    try:
        for filename in SQL_ORDER:
            try:
                con.execute((Path(sql_root) / filename).read_text(encoding='utf-8'))
            except Exception as exc:
                raise RuntimeError(f'SQL script failed: {filename}: {exc}') from exc
        failures = con.execute('SELECT * FROM phase2.vw_model_quality WHERE failure_count<>0').fetchall()
        if failures:
            raise ValueError(f'Model quality checks failed: {failures}')
        con.execute('COMMIT')
    except Exception:
        con.execute('ROLLBACK')
        raise
    finally:
        for relation in ['input_monthly','input_parameters','input_sensitivity']:
            con.unregister(relation)

def execute_analytics(root=ROOT):
    df, hashes = verify_phase1(root)
    exports = {}
    database = root / 'data/processed/pharma.duckdb'
    with duckdb.connect(str(database)) as con:
        con.execute('SET threads=1')
        phase1 = con.execute('SELECT * FROM monthly_prescribing ORDER BY month,product_code,region_code,unit_of_measure').df()
        expected = df.sort_values(['month','product_code','region_code','unit_of_measure']).reset_index(drop=True)
        pd.testing.assert_frame_equal(phase1[expected.columns], expected, check_dtype=False)
        build_model(con, df)
        for filename, view in EXPORTS.items():
            result = con.execute(f'SELECT * FROM phase2.{view} ORDER BY ALL').df()
            atomic_csv(result, root / f'outputs/tables/{filename}.csv')
            path = root / f'outputs/tables/{filename}.parquet'
            temp = path.with_suffix('.parquet.tmp')
            result.to_parquet(temp, index=False)
            os.replace(temp, path)
            exports[filename] = {'view': f'phase2.{view}', 'rows': len(result), 'columns': len(result.columns),
                                 'csv_sha256': sha256(root / f'outputs/tables/{filename}.csv'),
                                 'parquet_sha256': sha256(path)}
        preserved = con.execute('SELECT * FROM monthly_prescribing ORDER BY month,product_code,region_code,unit_of_measure').df()
        pd.testing.assert_frame_equal(preserved, phase1)
    if snapshot_sources(root) != hashes:
        raise ValueError('Phase 2 changed protected Phase 1 artifacts')
    write_json(root / 'outputs/validation/phase2_exports.json', {'sql_order': SQL_ORDER, 'exports': exports, 'phase1_preserved': True})
    return exports

if __name__ == '__main__':
    print(json.dumps(execute_analytics(), indent=2))
