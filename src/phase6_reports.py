"""Publish Phase 6 documentation from executed audit evidence."""
import json
from .common import ROOT

def reports(result,root=ROOT):
    docs=root/'docs'; docs.mkdir(exist_ok=True)
    manifest=json.loads((root/'config/dashboard_manifest.json').read_text(encoding='utf-8'))
    architecture='''# Phase 6 dashboard architecture

PharmaLens is a read-only Streamlit executive interface over the validated Phase 1–5 project. `app.py` configures the application, shared header and native `st.navigation` with six callable `st.Page` pages. Page modules render views; pure calculation, filtering, chart, scenario, contract and loader modules keep accounting separate from UI code.

The runtime reads Parquet files registered in `config/dashboard_manifest.json`. Each contract pins business keys, columns, exact dtypes, row counts, valid date ranges and SHA-256 hashes. Loaders reject incompatible, corrupt or missing critical data with a visible message. Optional absent datasets return no replacement values. Reads are cached by contract and file stat, then returned as deep copies. No DuckDB database, network query, model training, family selection or prior-phase pipeline runs on dashboard interactions.

## Pages and scope

| Page | Primary evidence | Scope behavior |
|---|---|---|
| Executive Overview | Observed items, NIC, weighted ratio and accounting decomposition | Month window; full-year growth only with both complete years |
| Regional Intelligence | Region summaries, trends, contribution and growth | Regions/year; shares denominator all regions in that year |
| Presentation Intelligence | Presentations, units, regional distribution and coverage | Presentation/region/year; shares denominator all presentations in selected regions/year |
| Forecasting & Model Evaluation | Frozen families, backtest predictions, selections and operational points | Series/stage/horizon/model display; common five-family support before display filtering |
| Decision Intelligence | Phase 5 priorities, sensitivity and investigation register | Stored cohort ranks; filtered entities do not change baseline ranks |
| Scenario Simulator | Observed baseline or frozen forecast plus historical cost assumption | Explicit user assumptions; no source writes |

## Design and arithmetic

Navy text, teal accents, neutral background and white cards form a shared enterprise theme. Plotly charts use consistent typography, axis units and hover labels. Wide layouts, responsive chart sizing and narrow-screen CSS support resizing; visual accessibility and mobile layout still require browser inspection. Currency is GBP NIC; counts are prescription items. NIC/item equals aggregate NIC divided by aggregate items, never a mean of row ratios. Unknown values are labelled unavailable; missing observations are not zeros. Physical quantities across tablet/liquid units are never summed.

Rolling-origin predictions use markers with origin, target, horizon and status in hover text. Forecast points from separate origins are not joined. Retrospective January–March 2026 operational points share a December 2025 cutoff. No prediction interval bands are shown because calibration support was insufficient. Selected-model cards retain the frozen choice; model display selection affects the comparison charts and tables, as labelled in the UI.

Priority sensitivity uses validated Phase 5 alternatives with all required dimensions retained. Missing forecast evidence remains unscored. Scenario results reuse validated multiplicative accounting and constrained mix algebra; no model or recommendation register is overwritten.

## Verification and maintenance

`src.phase6_audit` records repository inspection, source hashes, manifest and source guard, independent numerical reconciliation, repeated calculation hashes, local server health and pytest XML/logs. AppTest checks every page independently and the callable navigation entry point. Streamlit 1.41 AppTest does not fully support file-based multipage navigation, so callable navigation is used and page interactions are tested directly. Browser navigation and visual inspection are separate outstanding checks.

Official references: [Streamlit navigation](https://docs.streamlit.io/develop/concepts/multipage-apps/page-and-navigation), [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest), [Plotly hover formatting](https://plotly.com/python/hover-text-and-formatting/).
'''
    user='''# Phase 6 user guide

Start `app.py` with the command in the deployment guide. Select a page in the native sidebar navigation. Every page labels its active scope. Source and formula expanders explain definitions; methodology documents are available within the app. Data-version attribution appears in the sidebar.

Executive: adjust the historical month range. Items/NIC/weighted ratio follow that window. Annual growth needs two complete aggregate years; partial windows show unavailable. Accounting decomposition is offered only when both selected complete years fall inside the window.

Regional: choose regions, year and trend metric; optionally index each first selected month to 100. The annual comparison uses the previous year, as captioned. Share percentages still use all reported regions in the year. The detail panel explicitly retains fixed Phase 5 history/holdout evidence.

Presentation: choose presentations, reported regions and year. Read observed activity, concentration, NIC/item, physical unit and coverage separately. Missing presentation-region-month cells are unknown. Fixed Phase 5 evidence status is separately labelled; 13 presentations lack required forecast evidence and are unscored.

Forecasting: choose aggregation, series, development/final holdout, true horizon and displayed model families. Read the frozen operational choice before comparing models. Cards retain this choice; comparison displays follow selected models on common five-family support. Hover prediction markers for origin and horizon. No interval is available. The January–March 2026 panel is an as-of December 2025 retrospective forecast, not a current forecast.

Decision: filter entities, baseline tiers and forecast risk. Scored and unscored entities have separate tables. Filters retain original cohort ranks. Choose a validated alternative policy to inspect sensitivity without changing the baseline. Search proposed investigations, filter investigation evidence/priority separately, and inspect the recommendation's supporting source row. These are proposed analyst investigations, not actions or realized benefits.

Scenario: select an observed baseline year/region/presentation, or a frozen national forecast month converted with a disclosed fixed historical weighted cost assumption. Volume and NIC/item sliders are hypothetical. Inspect the exact accounting offset and two-way sensitivity. Mix-only redistribution uses a donor, receiver and bounded percentage-point transfer, preserves total items, and is separate from the volume/cost simulation. There is no clinical substitution recommendation.

Download buttons export the displayed filtered tables as UTF-8 CSV with ISO dates and full numerical precision. This includes summaries, origin-specific forecasts, priorities, investigations and current scenario assumptions/results. Clearing a selection shows a no-observations message; unknown activity is not replaced with zeros.

Scope: NHS England prescribing records, January 2023–December 2025 fixed vintage. NIC is not manufacturer sales revenue. No patient counts, population adjustment, case mix, clinical effectiveness, causal inference, India demand, profit or realized savings are supported.
'''
    deployment='''# Phase 6 deployment guide

## Local startup (PowerShell, project directory)

```powershell
.venv\\Scripts\\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

Open `http://127.0.0.1:8501`. To create a fresh runtime environment with Python 3.12, run `python -m venv .venv`, then `.venv\\Scripts\\python.exe -m pip install -r requirements-dashboard.txt`. For full analytical regression use `requirements.txt` instead. Stop the foreground server with Ctrl+C.

## Runtime package

Package `app.py`, `dashboard/`, `.streamlit/config.toml`, `config/dashboard_manifest.json`, `config/dataset.json`, `src/__init__.py`, `src/common.py`, `src/forecast_metrics.py`, `src/scenario_engine.py`, the methodology documents under `docs/`, and every Parquet file named by the manifest. The manifest contains all paths, keys, schema, row counts and hashes. Preserve project-relative paths. CSVs, notebooks, DuckDB databases and model retraining are not needed at runtime. No absolute workstation path or credential belongs in a deployment package. This public-data app needs no secret or external service call at runtime.

Use a Python-capable Streamlit host or container. Static web hosting cannot execute this Python runtime. Set the host entry point to `app.py` and install `requirements-dashboard.txt`. Binding to `0.0.0.0` and a host-assigned port is a hosting configuration choice; local verification binds only loopback. Mount runtime data read-only where supported. Check dependency installation and manifest integrity before starting. Provision memory for pandas/Parquet tables and cached copies; concurrency/load capacity has not been measured. Use host-level access control if the app is shared privately.

## Verification and updates

```powershell
.venv\\Scripts\\python.exe -m pytest tests/test_phase6_app.py -q
.venv\\Scripts\\python.exe -m src.phase6_audit
```

The audit requires the complete existing analytical repository. Inspect `outputs/phase6/validation/final_audit.json`, the test XML/log and startup health record. Data updates require a newly validated analytical release and matching contracts/hashes; do not regenerate the manifest merely to conceal a corrupt file. Restart runtime caches after releasing a new data package. Source data is frozen; this phase does not refresh 2026 observations.

Local startup/health results are recorded by the executed audit. No cloud deployment, authentication rollout, browser visual review, mobile review or load test is claimed. Before public release, perform browser navigation/hover/download inspection on desktop and mobile, review accessibility, verify actual CSV retrieval and platform resource/security settings, and run a fresh environment deployment smoke test.
'''
    demo='''# Phase 6 Axtria interview demonstration (6 minutes)

1. **0:00–0:45 — Scope and executive view.** “This is independent NHS prescribing intelligence. Items measure recorded prescriptions and NIC measures ingredient cost, not manufacturer revenue.” Show the source/data-version attribution and weighted ratio definition. Change the month range and explain why incomplete annual comparisons become unavailable.
2. **0:45–1:45 — Regional and presentation evidence.** Select one region and year, inspect contribution versus the disclosed denominator, then show a presentation's trend and coverage. “Missing observations are unknown; tablet and liquid quantities are kept separate.” Download the filtered summary.
3. **1:45–2:45 — Model evaluation.** Show the frozen national model, switch true horizons and inspect origin hover labels. “Development selected the operational model. Holdout results never reselect it; models are compared on common support.” Show the explicit absence of calibrated intervals and the December 2025 forecast cutoff.
4. **2:45–3:45 — Decision intelligence.** Inspect monitoring dimensions and policy sensitivity, then switch to presentations to show the separate unscored table. Open one investigation's source row. “These weights are transparent review assumptions; monitoring priority is not a sales opportunity.”
5. **3:45–4:45 — Hypothetical accounting.** Set +5% items and −5% NIC/item. Explain multiplicative arithmetic and the accounting offset; inspect sensitivity and a separate bounded mix transfer. “No clinical substitution, realized savings or profitability is inferred.” Download the assumptions and results.
6. **4:45–6:00 — Trust and limitations.** Show the executed audit, source hashes, regression evidence and reproducibility. Distinguish local health/AppTest checks from browser/cloud checks. Discuss a next phase for fresh observations, browser/accessibility testing, temporal release availability, calibrated uncertainty and validation with actual business users.

Read displayed values from the active scope during the demonstration; do not memorize unsupported commercial claims. Use the audit for verified counts rather than claiming a deployed service.
'''
    inventory=sorted(str(p.relative_to(root)).replace('\\','/') for folder in ['dashboard','tests'] for p in (root/folder).rglob('*.py') if folder=='dashboard' or 'phase6' in p.name)
    audit=f'''# Phase 6 audit

Executed result: **{'PASSED' if result.get('passed') else 'NOT COMPLETE'}**. Machine evidence: `outputs/phase6/validation/final_audit.json`, `all_tests.xml`, `test_execution.log`, `startup_health.json`, `dashboard_reconciliation.csv`, `reproducibility.json`, `source_guard.json`, and `repository_inspection.json`.

## Architecture, inventory and data

Six Streamlit pages: Executive Overview, Regional Intelligence, Presentation Intelligence, Forecasting & Model Evaluation, Decision Intelligence, Scenario Simulator. Read-only Parquet loader, exact schema/hash contracts, pure scope calculations and Plotly figures. App version {manifest['app_version']}; manifest data version `{manifest['data_version']}`. {len(manifest['datasets'])} registered datasets: all 42 Phase 5 products plus required Phase 2/3/4 supporting products. Paths/schema/keys/row counts/hashes are fully listed in `config/dashboard_manifest.json`.

Code inventory:

{chr(10).join('- `'+p+'`' for p in inventory)}

Additional files: `.streamlit/config.toml`, `dashboard/assets/styles.css`, `app.py`, `requirements-dashboard.txt`, `config/dashboard_manifest.json`, `src/phase6_audit.py`, `src/phase6_reports.py`, five Phase 6 documents and README extension.

## Executed checks

- Tests: {result.get('tests',{})}.
- Independent numerical checks: {result.get('numerical_validation',{})}.
- Local HTTP startup: {result.get('startup',{})}.
- Repeated calculation outputs identical: {result.get('calculations_deterministic',False)}.
- Protected artifacts: {result.get('protected_artifacts',0)}; unchanged: {result.get('protected_artifacts_unchanged',False)}.
- Python: {result.get('python','pending')}; packages: {result.get('versions',{})}.

Contracts are tested across every runtime table plus wrong types, missing columns, duplicate keys, negative items, missing manifest, corrupted bytes, path escape and cache mutation. Reconciliation independently checks historical sums/months, filtered regions, weighted ratios, annual changes, frozen forecast MAE/MASE, multiplicative scenarios, exact offsets and mix conservation. Forecast comparisons retain common successful five-family support; failed points remain missing. Tests verify markers have origin/horizon labels and no cross-origin lines or fabricated interval bands. Frozen model decisions remain unchanged.

Priority tests verify 13 presentations remain unscored and every recommendation points to a real supporting source row. AppTest asserts actual rendered headers, charts, table/download controls, main entry metrics and interactions: regional/presentation empty selections, year changes, forecast level/stage/horizon/model filtering, unscored priorities/search, scenario slider results, bounded donor transfers and retrospective forecast baseline. CSV tests reconcile filtered rows. AppTest does not simulate a real HTTP CSV download or inspect browser pixels.

## Deployment, limitations and next phase

{result.get('browser_inspection','Browser inspection not performed.')}. {result.get('cloud_deployment','Cloud deployment not performed.')}. Local server is terminated by the startup check after HTTP root/health verification. Deployment instructions and runtime packaging are documented; a fresh host deployment has not been executed.

Fixed-vintage NHS England history January 2023–December 2025; unknown undercoverage; no patient/population/case mix adjustment. NIC is not revenue. Retrospective forecasts do not reconstruct release availability or future actuals. Short overlapping holdout and insufficient calibration prohibit defensible prediction intervals. Illustrative monitoring weights and policy-sensitive ranks require analyst review. Scenarios are deterministic hypothetical accounting, not predicted savings, margin, demand or clinical outcomes. Mobile layout, browser hover/download/navigation, accessibility and concurrency require additional verification.

Phase 7: obtain fresh validated data with release dates; perform real browser/accessibility checks and a Python-host deployment; test capacity and user permissions; seek domain-user feedback; assess calibrated uncertainty and temporal availability before operational use. Preserve this historical benchmark and its frozen model selection.
'''
    for name,text in [('DASHBOARD_ARCHITECTURE',architecture),('USER_GUIDE',user),('DEPLOYMENT_GUIDE',deployment),('DEMO_SCRIPT',demo),('AUDIT',audit)]:
        (docs/f'PHASE6_{name}.md').write_text(text,encoding='utf-8')

if __name__=='__main__':
    path=ROOT/'outputs/phase6/validation/final_audit.json'
    reports(json.loads(path.read_text()) if path.exists() else {})
