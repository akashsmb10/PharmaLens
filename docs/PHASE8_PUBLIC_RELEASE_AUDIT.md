# Phase 8 public release audit

**Status: Prepared for release — awaiting authorization.** This report records local preparation on 12 October 2026. No Phase 8 files have been pushed and no Streamlit Cloud app has been deployed.

| Requirement | Status | Evidence / next step |
|---|---|---|
| GitHub publication | BLOCKED | Owner approval for pushing the staged files is pending. Existing `akashsmb10/PharmaLens` has one initial MIT licence commit; local release checkout preserves its history. |
| GitHub URL | PASS | [Existing repository](https://github.com/akashsmb10/PharmaLens), read-only cloned at commit `5481a1ce373b2ca9bd8d0d05d6e1ca530a022939`. This URL does not yet contain the project. |
| Repository visibility | PASS | GitHub API reports `public`, `private: false`, default branch `main` for `akashsmb10/PharmaLens`. |
| Code licence | PASS | Owner selected MIT. The staged release uses the repository's existing `LICENSE`, copyright (c) 2026 Akash Bailwad. Project code licence is distinct from source-data terms. |
| Data licensing review | PASS | NHSBSA PCA monthly dataset identifies Open Government Licence v3.0. The staged release contains 52 derived, attributed Parquet products and excludes raw source snapshots. See [data sources and licences](DATA_SOURCES_AND_LICENSES.md). Publisher asks planned public-data publishers to contact its data service; no contact was sent. |
| Security scan | PASS | Staged paths and bytes reviewed for private paths, common token/private-key markers, secrets files, raw data, environments, logs, and files above 50 MiB; no findings. Seven notebook copies have cleared outputs. This pattern scan cannot guarantee absence of every secret. |
| Published file inventory | BLOCKED | 304 tracked files in the reviewed checkout (303 staged additions and the existing licence), about 8.54 MB uncompressed, are prepared locally. Source, six-page dashboard, SQL, tests, seven notebooks, documentation, PDF/PPTX, MIT licence and 52 runtime Parquets are included. Exact inventory is `git diff --cached --name-only` in the local release checkout. Publication awaits approval. |
| Deployment data strategy | PASS | The 52 exact dashboard-manifest Parquets are force-staged despite the general `outputs/` ignore. All 52 SHA-256 hashes match the manifest; all load with their contracts (16,963 rows summed across products). Data version `44223b1622b280ada588e40bbcd564ec38ec7053b41fff330cf01d4c836cfe06`. No runtime downloads or retraining. |
| Runtime dependencies | PASS | Root `requirements.txt` is pinned to Streamlit 1.41.1, Plotly 5.24.1, pandas 2.2.3, NumPy 2.1.3 and PyArrow 18.1.0. Full analytical dependencies are retained as `requirements-analytics.txt`. |
| Clean deployment test | PASS | A new isolated Python 3.12.10 environment installed the exact five pinned root requirements and loaded all 52 datasets. Clean startup returned health and root HTTP 200 with listener cleanup. The six data-free CI tests passed in the earlier independently installed clean environment. |
| Local six-page browser test | PASS | Installed Chrome rendered all six pages from the new isolated Python 3.12 environment at 1280 px with charts and zero Streamlit exceptions. Observed page waits: 9.73, 3.80, 3.67, 2.73, 3.11 and 2.22 seconds. Prior Phase 7 four-width browser and interaction audit remains unchanged. |
| Remote CI | NOT TESTED | Workflow is staged and locally passed 6 data-free tests; no Phase 8 push has triggered GitHub Actions. |
| Streamlit deployment | BLOCKED | Owner deployment authorization and GitHub/Streamlit authentication pending. Entry point: `app.py`, branch `main`, project root. |
| Public dashboard URL | NOT TESTED | No live URL exists from this work. |
| Live application test | NOT TESTED | Six public pages, filters, downloads and scenario controls require deployment before verification. |
| Performance observation | PASS | Local Chrome timings above only; cloud cold start, memory and availability remain unmeasured. |
| Protected artifacts | PASS | Original Phase 8 baseline: 604/604 unchanged, 0 changed, 0 missing. Phase 7 manifest: 497/497 unchanged, 0 changed, 0 missing. Frozen forecasts, model choices, Phase 5 scores, original scenarios, historical datasets and earlier audits are preserved. |

The release checkout is `outputs/phase8/existing_github`, an isolated clone of the existing repository. The project source tree remains outside Git. The candidate was prepared from the reviewed Phase 7 portfolio archive. The local clone has no commit or push for the new files. After explicit approval, check the exact staged diff, confirm repository visibility and authenticated account, commit and push to `main`, observe GitHub Actions, deploy through Streamlit Community Cloud, verify all six public pages and interactions, and then add verified live links to the README.

**Remaining limitations and recommendation:** GitHub authentication, public visibility, remote CI and cloud behavior remain unverified. The data publisher's public-publication contact request should be reviewed by the owner. Publish only after explicit approval of this exact existing repository and public deployment, then replace blocked/not-tested rows with measured remote evidence. Phase 8 is not complete.
