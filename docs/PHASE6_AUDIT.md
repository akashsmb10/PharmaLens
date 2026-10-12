# Phase 6 audit

Executed result: **PASSED**. Machine evidence: `outputs/phase6/validation/final_audit.json`, `all_tests.xml`, `test_execution.log`, `startup_health.json`, `dashboard_reconciliation.csv`, `reproducibility.json`, `source_guard.json`, and `repository_inspection.json`.

## Architecture, inventory and data

Six Streamlit pages: Executive Overview, Regional Intelligence, Presentation Intelligence, Forecasting & Model Evaluation, Decision Intelligence, Scenario Simulator. Read-only Parquet loader, exact schema/hash contracts, pure scope calculations and Plotly figures. App version 1.0.0; manifest data version `44223b1622b280ada588e40bbcd564ec38ec7053b41fff330cf01d4c836cfe06`. 52 registered datasets: all 42 Phase 5 products plus required Phase 2/3/4 supporting products. Paths/schema/keys/row counts/hashes are fully listed in `config/dashboard_manifest.json`.

Code inventory:

- `dashboard/__init__.py`
- `dashboard/chart_factory.py`
- `dashboard/components.py`
- `dashboard/data_contracts.py`
- `dashboard/data_loader.py`
- `dashboard/evidence.py`
- `dashboard/filters.py`
- `dashboard/formatting.py`
- `dashboard/metrics.py`
- `dashboard/navigation.py`
- `dashboard/pages/__init__.py`
- `dashboard/pages/decision_intelligence.py`
- `dashboard/pages/executive.py`
- `dashboard/pages/forecasting.py`
- `dashboard/pages/presentations.py`
- `dashboard/pages/regional.py`
- `dashboard/pages/scenario_simulator.py`
- `dashboard/scenarios.py`
- `dashboard/theme.py`
- `tests/test_phase6_app.py`
- `tests/test_phase6_charts.py`
- `tests/test_phase6_data_loader.py`
- `tests/test_phase6_filters.py`
- `tests/test_phase6_forecasting.py`
- `tests/test_phase6_metrics.py`
- `tests/test_phase6_priorities.py`
- `tests/test_phase6_reproducibility.py`
- `tests/test_phase6_scenarios.py`

Additional files: `.streamlit/config.toml`, `dashboard/assets/styles.css`, `app.py`, `requirements-dashboard.txt`, `config/dashboard_manifest.json`, `src/phase6_audit.py`, `src/phase6_reports.py`, five Phase 6 documents and README extension.

## Executed checks

- Tests: {'tests': 296, 'failures': 0, 'errors': 0, 'skipped': 0}.
- Independent numerical checks: {'checks': 1294, 'failed_checks': 0, 'calculation_sha256': 'fc4bb59ab1a90f1b43a05b6580d44922053cc119047bc4d2830eccb2b21cfb55'}.
- Local HTTP startup: {'passed': True, 'health_status': 200, 'root_status': 200, 'server_stopped': True, 'health_body': 'ok', 'listener_closed': True}.
- Repeated calculation outputs identical: True.
- Protected artifacts: 467; unchanged: True.
- Python: 3.12.10; packages: {'streamlit': '1.41.1', 'plotly': '5.24.1', 'pandas': '2.2.3', 'numpy': '2.1.3', 'pyarrow': '18.1.0'}.

Contracts are tested across every runtime table plus wrong types, missing columns, duplicate keys, negative items, missing manifest, corrupted bytes, path escape and cache mutation. Reconciliation independently checks historical sums/months, filtered regions, weighted ratios, annual changes, frozen forecast MAE/MASE, multiplicative scenarios, exact offsets and mix conservation. Forecast comparisons retain common successful five-family support; failed points remain missing. Tests verify markers have origin/horizon labels and no cross-origin lines or fabricated interval bands. Frozen model decisions remain unchanged.

Priority tests verify 13 presentations remain unscored and every recommendation points to a real supporting source row. AppTest asserts actual rendered headers, charts, table/download controls, main entry metrics and interactions: regional/presentation empty selections, year changes, forecast level/stage/horizon/model filtering, unscored priorities/search, scenario slider results, bounded donor transfers and retrospective forecast baseline. CSV tests reconcile filtered rows. AppTest does not simulate a real HTTP CSV download or inspect browser pixels.

## Deployment, limitations and next phase

Not performed: no browser automation tool available; AppTest used instead. Not performed; local startup and deployment packaging only. Local server is terminated by the startup check after HTTP root/health verification. Deployment instructions and runtime packaging are documented; a fresh host deployment has not been executed.

Fixed-vintage NHS England history January 2023–December 2025; unknown undercoverage; no patient/population/case mix adjustment. NIC is not revenue. Retrospective forecasts do not reconstruct release availability or future actuals. Short overlapping holdout and insufficient calibration prohibit defensible prediction intervals. Illustrative monitoring weights and policy-sensitive ranks require analyst review. Scenarios are deterministic hypothetical accounting, not predicted savings, margin, demand or clinical outcomes. Mobile layout, browser hover/download/navigation, accessibility and concurrency require additional verification.

Phase 7: obtain fresh validated data with release dates; perform real browser/accessibility checks and a Python-host deployment; test capacity and user permissions; seek domain-user feedback; assess calibrated uncertainty and temporal availability before operational use. Preserve this historical benchmark and its frozen model selection.
