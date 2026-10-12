# Reproducibility guide

## Dashboard-only setup

Use Python 3.12 in a new directory. Extract the reviewed `PharmaLens_Phase7_Portfolio.zip` package; it contains the application, relative-path source, all registered Parquet datasets and methodology. The working repository ignores bulky raw data and generated outputs, so a code-only clone does not automatically contain analytical inputs.

The archive also includes `requirements-dashboard-lock.txt`, captured from the successfully tested fresh environment. Use `python -m pip install -r requirements-dashboard-lock.txt` to reproduce those transitive versions on the same Python/runtime platform. `requirements-dashboard.txt` retains the portable direct dependency pins; dependency resolution on another platform is a separate check.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dashboard.txt
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true
```

Linux/macOS use `.venv/bin/python` instead. Open `http://127.0.0.1:8501`; Ctrl+C stops the foreground server. Restore the matching manifest and data if hashes do not match; never regenerate hashes to conceal a defect. Raw snapshots, DuckDB and model fitting are unnecessary for dashboard-only execution.

## Clean execution evidence

`src.phase7_clean` creates a separate environment with **no system site packages** and a minimal copied runtime checkout. Pinned direct dependencies plus pytest are installed there. It validates every registered contract, exercises all pages and the app entry through AppTest, then launches and closes a real HTTP server. Result and full transitive dependency freeze are recorded in `outputs/phase7/validation/clean_environment.json` and `clean_requirements_lock.txt`. Consult the final audit for executed status; this guide does not infer success from environment creation alone.

## Full historical analytical reproduction

The original raw API snapshots, acquisition receipts, processed artifacts and earlier source guards are needed for exact historical reproduction. Current online data may have revisions. The source code has explicit observed and synthetic modes; synthetic data is never a substitute for portfolio results. Existing complete artifacts are verified read-only in Phase 7; models are not retrained.

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pytest -q
```

Original phase commands are documented below as historical reproduction instructions, **not executed by Phase 7**:

```powershell
.venv\Scripts\python.exe run_pipeline.py --phase 1
.venv\Scripts\python.exe run_pipeline.py --phase 2
.venv\Scripts\python.exe run_pipeline.py --phase 3
.venv\Scripts\python.exe run_pipeline.py --phase 4
.venv\Scripts\python.exe run_pipeline.py --phase 5
```

Use an isolated copy for those commands; they can write outputs. A fresh download is a new vintage and requires a separately versioned release. Frozen historical scores must not be overwritten. The full-data regression suite includes controlled pipeline integration tests whose deterministic artifacts are checked against protection hashes; this is distinct from rebuilding every historical phase in a clean environment.

## Audit and CI

Install `requirements-portfolio.txt` for Ruff, Playwright and python-pptx. Browser QA uses an installed Chrome/Edge on this Windows workstation. `python -m src.phase7_audit --run-tests` executes independent reconciliation, static/security checks, regression, clean-runtime evidence checks and preservation. The data-free GitHub Actions job runs `pytest tests/ci --confcutdir=tests/ci`; full-data integration remains local until immutable-artifact provisioning is implemented. No remote Actions result is claimed.

The release archive excludes raw snapshots, credentials, environment files, caches and private logs. Sanitized release copies are distinct from protected originals. All package entries have a hash inventory. Validate package hashes before running it; a public release still requires owner licence review and authorization.
