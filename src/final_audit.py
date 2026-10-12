"""Execute the requested final Phase 1 checks and persist actual completion evidence."""
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from .common import ROOT, sha256, utc_now, write_json
from .ingest import ingest
from .validate import validate
from .inspect_data import inspect_data
from .documentation import dictionary
from .notebook_tools import build_notebook, execute_notebook

def main():
    out = ROOT / 'outputs/validation'
    _, monthly, manifest = ingest()
    quality = validate()
    inspect_data()
    dictionary()
    if not quality['passed']:
        raise RuntimeError('Observed data quality gate failed; review outputs/validation/quality_report.json')
    first_hash = manifest['processed_sha256']
    _, _, second_manifest = ingest()
    if second_manifest['processed_sha256'] != first_hash:
        raise RuntimeError('Repeated ingestion changed the processed CSV hash')
    build_notebook()
    execute_notebook()
    test_command = [sys.executable, '-m', 'pytest', '-q', '--basetemp=outputs/validation/pytest_audit_tmp',
                    '--junitxml=outputs/validation/pytest_results.xml']
    tests = subprocess.run(test_command, cwd=ROOT, text=True, capture_output=True)
    (out / 'pytest_execution.log').write_text(tests.stdout + tests.stderr, encoding='utf-8')
    print(tests.stdout, flush=True)
    pip = subprocess.run([sys.executable, '-m', 'pip', 'check'], cwd=ROOT, text=True, capture_output=True)
    (out / 'dependency_check.log').write_text(pip.stdout + pip.stderr, encoding='utf-8')
    junit = ET.parse(out / 'pytest_results.xml').getroot()
    suites = [junit] if junit.tag == 'testsuite' else list(junit.findall('testsuite'))
    counts = {name: sum(int(s.attrib.get(name, 0)) for s in suites) for name in ['tests','failures','errors','skipped']}
    pages_verified = all(sha256(ROOT / entry['file']) == entry['sha256'] for entry in manifest['files'])
    meta = json.loads((ROOT / 'data/raw/source_metadata.json').read_text(encoding='utf-8'))['result']
    assert meta['license_id'] == 'OGL-UK-3.0'
    assert meta['name'] == manifest['dataset']['dataset_id']
    assert sha256(ROOT / 'data/raw/source_metadata.json') == manifest['source_metadata_sha256']
    required = ['README.md', 'requirements.txt', 'requirements-lock.txt', '.gitignore', 'config/dataset.json',
                'src/ingest.py', 'src/validate.py', 'run_pipeline.py', 'docs/DATA_SOURCE_EVALUATION.md',
                'docs/DATA_DICTIONARY.md', 'docs/INITIAL_DATA_ASSESSMENT.md', 'notebooks/01_data_understanding.ipynb',
                'data/processed/acquisition_manifest.json', 'data/processed/monthly_prescribing.csv',
                'data/processed/monthly_prescribing.parquet', 'data/processed/source_rows.parquet',
                'data/processed/pharma.duckdb', 'outputs/validation/quality_report.json',
                'outputs/validation/column_profile.csv', 'outputs/validation/notebook_execution.json',
                'outputs/charts/monthly_items.png', 'outputs/tables/product_distribution.csv',
                'outputs/tables/geographic_coverage.csv', 'outputs/validation/pytest_results.xml']
    directories = ['config', 'data/raw', 'data/synthetic', 'data/processed', 'sql', 'src', 'notebooks', 'dashboard',
                   'outputs/charts', 'outputs/tables', 'outputs/forecasts', 'outputs/validation', 'tests', 'docs']
    missing = [p for p in required + directories if not (ROOT / p).exists()]
    nb_execution = json.loads((out / 'notebook_execution.json').read_text(encoding='utf-8'))
    result = {'finished_at_utc': utc_now(), 'mode': manifest['mode'], 'raw_rows': manifest['raw_rows'],
              'source_column_count': len(manifest['source_columns']), 'monthly_rows': len(monthly),
              'monthly_columns': len(monthly.columns), 'first_month': str(monthly.month.min().date()),
              'last_month': str(monthly.month.max().date()), 'months': int(monthly.month.nunique()),
              'presentations': int(monthly.product_code.nunique()), 'regions': int(monthly.region_code.nunique()),
              'quality_gate_passed': quality['passed'], 'tests': counts, 'test_process_exit_code': tests.returncode,
              'notebook': nb_execution, 'pip_check_exit_code': pip.returncode, 'raw_pages_verified': pages_verified,
              'repeated_ingestion_identical_csv': True, 'missing_required_paths': missing,
              'processed_csv_sha256': first_hash, 'verified_raw_pages': len(manifest['files'])}
    result['passed'] = not missing and pages_verified and quality['passed'] and tests.returncode == 0 and pip.returncode == 0 and nb_execution['error_outputs'] == 0
    write_json(out / 'final_audit.json', result)
    lines = ['# Final Phase 1 audit', '', f"Executed at {result['finished_at_utc']}. Mode: {result['mode']}.", '',
             f"Overall pass: **{result['passed']}**. Source: NHSBSA PCA monthly administrative data, OGL v3.0.",
             f"Source shape: {result['raw_rows']:,} × {result['source_column_count']}. Monthly shape: {len(monthly):,} × {len(monthly.columns)}.",
             f"Coverage: {result['first_month']} to {result['last_month']} ({result['months']} months), {result['presentations']} presentations, {result['regions']} regions.", '',
             f"Tests: {counts['tests']} executed; {counts['failures']} failures; {counts['errors']} errors; {counts['skipped']} skipped.",
             f"Notebook: {nb_execution['code_cells_executed']} code cells executed, {nb_execution['error_outputs']} error outputs.",
             f"Verified raw pages: {result['verified_raw_pages']}. Repeated processed CSV SHA-256: `{first_hash}`.",
             f"Dependency consistency exit code: {pip.returncode}. Missing required paths: {missing}.", '',
             '## Data findings', '']
    lines += [f"- {c['check']}: {c['count']:,} ({c['severity']}). {c['explanation']}" for c in quality['checks']]
    lines += ['', '## Remaining interpretation work', '',
              'Review incomplete presentation-region series, extreme observations and any name/geography changes before',
              'forecasting. Warnings are retained business-review findings, not automatically removed records.',
              'One chemical, England community dispensing and NHS ingredient cost do not establish manufacturer revenue',
              'or India market demand. Raw preparation-class codes have not been decoded without source reference.',
              'OpenPrescribing acquisition was blocked (403); the official NHSBSA dataset was acquired instead.',
              'The initial metadata access date is known, but its exact download time was not recorded. Individual',
              'pipeline-acquired pages have exact UTC receipts. No forecasting, synthetic revenue or final dashboard',
              'was implemented. See the source evaluation and initial assessment for analytical limits.', '',
              '## Created files', '']
    files = sorted(str(p.relative_to(ROOT)).replace('\\','/') for p in ROOT.rglob('*') if p.is_file()
                   and '.venv' not in p.parts and '__pycache__' not in p.parts and '.pytest_cache' not in p.parts
                   and not any(part.startswith('pytest_') or part == 'jupyter_runtime' for part in p.parts))
    lines += [f'- `{p}`' for p in files if not p.startswith('data/raw/')]
    lines += [f'- `data/raw/`: {len(list((ROOT / "data/raw").glob("*.json")))} original API, receipt and research JSON files.']
    (ROOT / 'docs/PHASE1_AUDIT.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2), flush=True)
    raise SystemExit(0 if result['passed'] else 1)

if __name__ == '__main__':
    main()
