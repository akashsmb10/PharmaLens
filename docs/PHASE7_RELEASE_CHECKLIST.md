# Release checklist

| Check | Status |
|---|---|
| Original baseline recorded | PASS: Complete: 296 original tests and 497 protected files |
| No analytical retraining/reselection | PASS: Preserved |
| Independent arithmetic | PASS: 1,571 checks; 0 failed |
| Full local regression | PASS: 324 passed, 0 failed |
| Clean dashboard setup | PASS: True |
| Real six-page / four-width browser QA | PASS: True |
| Screenshot image review | PASS: See local visual review record; scoped inspection |
| Filtered export and scenario calculations | PASS: Executed browser checks |
| Documentation relative links | PASS: Verified in final checks |
| Frozen data/model/output hashes | PASS: 497 / 497 unchanged |
| Credential-pattern review and path sanitization | PASS: Release copies reviewed; private logs excluded |
| Data attribution / no endorsement | PASS: Supplied; publisher OGL v3 reviewed |
| Code licence | BLOCKED: Pending owner selection |
| Native PowerPoint visual review | PASS: All twelve native slide renders inspected; PDF exported |
| Remote GitHub/Actions/cloud | NOT TESTED: Not attempted; authorization required |

## Safe local review and future GitHub preparation

Extract `deliverables/PharmaLens_Phase7_Portfolio.zip` into a separate directory and review its source, docs, notebook copies and `PORTFOLIO_VALIDATION.json`. The curated archive includes exact registered runtime Parquet bytes; original private/raw/venv/log files are excluded. Sanitized notebook outputs are intentionally cleared, so their execution counts are not proof of a fresh notebook run.

When the owner has selected a code licence and explicitly authorized publication, initialize Git in that reviewed extracted copy, stage source/docs/config/SQL/tests/notebooks/requirements and the licence notice explicitly, and inspect the staged diff. Runtime outputs remain ignored; attach the reviewed archive as an asset or define explicit immutable-data provisioning. Never run `git add .` in the original working directory. Do not force-add raw data, environments or local audit logs.

Suggested repository description: Independent AI-assisted NHSBSA atorvastatin prescribing analytics with SQL, statistical diagnostics, frozen rolling-origin forecasts, transparent scenarios and Streamlit.

The supplied Actions workflow runs only data-free fixtures. Full-data integration needs a separately designed artifact-provisioning step and original evidence; no broken opt-in remote integration job is presented as ready. Cloud deployment requires a Python host, the registered runtime package, a separate dependency/runtime check, and explicit authorization. No remote URL or successful cloud/Actions outcome is invented.

Local run: `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true`. See [setup guide](REPRODUCIBILITY_GUIDE.md) and [audit](PHASE7_AUDIT.md).
