# Phase 6 deployment guide

## Local startup (PowerShell, project directory)

```powershell
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

Open `http://127.0.0.1:8501`. To create a fresh runtime environment with Python 3.12, run `python -m venv .venv`, then `.venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt`. For full analytical regression use `requirements.txt` instead. Stop the foreground server with Ctrl+C.

## Runtime package

Package `app.py`, `dashboard/`, `.streamlit/config.toml`, `config/dashboard_manifest.json`, `config/dataset.json`, `src/__init__.py`, `src/common.py`, `src/forecast_metrics.py`, `src/scenario_engine.py`, the methodology documents under `docs/`, and every Parquet file named by the manifest. The manifest contains all paths, keys, schema, row counts and hashes. Preserve project-relative paths. CSVs, notebooks, DuckDB databases and model retraining are not needed at runtime. No absolute workstation path or credential belongs in a deployment package. This public-data app needs no secret or external service call at runtime.

Use a Python-capable Streamlit host or container. Static web hosting cannot execute this Python runtime. Set the host entry point to `app.py` and install `requirements-dashboard.txt`. Binding to `0.0.0.0` and a host-assigned port is a hosting configuration choice; local verification binds only loopback. Mount runtime data read-only where supported. Check dependency installation and manifest integrity before starting. Provision memory for pandas/Parquet tables and cached copies; concurrency/load capacity has not been measured. Use host-level access control if the app is shared privately.

## Verification and updates

```powershell
.venv\Scripts\python.exe -m pytest tests/test_phase6_app.py -q
.venv\Scripts\python.exe -m src.phase6_audit
```

The audit requires the complete existing analytical repository. Inspect `outputs/phase6/validation/final_audit.json`, the test XML/log and startup health record. Data updates require a newly validated analytical release and matching contracts/hashes; do not regenerate the manifest merely to conceal a corrupt file. Restart runtime caches after releasing a new data package. Source data is frozen; this phase does not refresh 2026 observations.

Local startup/health results are recorded by the executed audit. No cloud deployment, authentication rollout, browser visual review, mobile review or load test is claimed. Before public release, perform browser navigation/hover/download inspection on desktop and mobile, review accessibility, verify actual CSV retrieval and platform resource/security settings, and run a fresh environment deployment smoke test.
