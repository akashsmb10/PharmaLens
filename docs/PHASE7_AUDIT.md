# Phase 7 final portfolio audit

Audit date: 12 October 2026. This is an independent, AI-assisted pharmaceutical prescribing portfolio. Codex generated and executed substantial work; no client delivery or personal manual-authorship claim is implied.

## Executive completion and baseline

Status: Local Phase 7 checks complete; public release pending owner decisions. Baseline: 616 repository files excluding environments/caches, 91,159,475 bytes; 296 original tests passed before edits. No Git repository or remote was present. The immutable Phase 1–6 baseline contains 497 artifacts. Original README is retained in private local audit evidence. No model fit, frozen reselection, priority-policy change or historical output replacement was authorized or performed.

## Code audit

AST and static checks review ingestion, validation, SQL, statistics, features, splits, forecast fitting/evaluation/selection, intervals, decision scoring, scenarios and dashboard consumers. Fatal Ruff rules E9/F63/F7/F82: True. Legacy unused imports/variables, dense formatting and limited annotations remain noncritical maintainability findings. Broad forecast-fit exception boundaries retain explicit failure rows; they do not silently substitute a different model. Loader contract errors remain visible. Further type annotation and modularization are future maintenance work.

Safe changes: native collapsed-sidebar default, three-card row ordering on narrow screens, wrapped chart titles, explanatory portfolio footer and unused dashboard imports. An import cleanup initially removed a scenario re-export; the real browser detected this, and the explicit re-export was restored. The Phase 3 document guard now excludes later Phase 7 documents, without altering any original protected member or mathematical result. No statistical functions were cosmetically rewritten.

## Numerical audit

Independent reconciliation: 1,571 checks, 0 failed. [Methods and representative values](PHASE7_NUMERICAL_RECONCILIATION.md). Raw receipt totals use Decimal; metric checks reconstruct origin-only scales and common model support; score checks use pairwise ranks; scenario checks use direct identities. Repeated result hash equality: True. Local detail: `outputs/phase7/validation/numerical_reconciliation.csv`.

## Statistical audit

Historical January 2023–December 2025 monthly diagnostics remain descriptive. HAC lag-three uncertainty does not remove omitted-variable bias; Theil–Sen and Kendall answer complementary trend questions. Three annual cycles and weak annual-lag evidence cannot establish stable seasonality. STL and MAD anomaly flags are retrospective diagnostics, not future-available features or reasons to delete records. Calendar-aware differences preserve missing months. The exact volume/mix/within-presentation decomposition reconciles to observed NIC change but does not establish a causal price mechanism, efficiency or realized savings. No tests were rewritten to create a stronger claim.

## Forecasting audit

[Full defense](PHASE7_FORECASTING_DEFENSE.md). Development selection is frozen at June 2025 before July–December targets. Origin-only inputs and MASE scales are independently checked. National/regional ETS and twenty-eight region-presentation Ridge alpha-ten choices are preserved. National ETS MASE 0.8883, WAPE 3.6841%; evaluated naive MASE 1.1070. Ridge comparator MASE 0.8717 is lower and disclosed; it does not trigger retrospective reselection. Holdout horizons have 6/5/4 overlapping cells, not independent future months. Residual calibration support is below the implemented threshold of twenty; intervals remain unavailable. Independent hierarchy forecasts may not sum. Jan–Mar 2026 forecasts use a retrospective December 2025 observation cutoff, publication delay is not replayed, and no 2026 actual accuracy is claimed.

## Decision-intelligence audit

Five component weights remain 0.25/0.20/0.20/0.20/0.15. Ties, neutral constant fifty and complete-case scoring were recomputed. Thirteen presentation priorities remain unscored. All seven regional ranks are policy-sensitive. Fifteen of thirty-six series need manual review. The 88 hypotheses and 225 proposed investigations retain supporting evidence and rule lineage. They are review candidates, not executed business actions. Scenario algebra, offsets and mix conservation reconcile; all effects remain hypothetical.

## Dashboard, interaction and screenshot audit

Actual Chrome/Playwright browser status: True; 24 page/viewport checks across six pages at 1440/1280/768/390 pixels. Downloaded 2024 regional CSV and scenario keyboard sliders are reconciled. Native navigation is exercised. Tablet/mobile use the collapsed default; desktop screenshots explicitly expand native navigation. Screenshot [index](../README.md#dashboard-preview). Six primary screenshots, eighteen additional viewport captures and six chart-detail images are generated from the running app. Streamlit uses an inner scrolling container: these are viewport captures, not proof that every below-fold element was visually inspected. Assistant image inspection is recorded separately. Dense presentation labels and wide tables require filtering, hover or in-table scroll; no page-level overflow is accepted. This is scoped QA, not accessibility certification, browser-matrix testing or capacity testing.

## Security, licensing and GitHub readiness

Pattern scan found 0 credential candidates; it does not prove absence of every possible secret. Official publisher contact addresses are attributed public metadata. Original historical evidence retains workstation paths; sanitized release copies remove them and notebook outputs, preserving original hashes. Raw data, virtualenvs, private audit logs, credentials and local secrets are excluded from the release archive. The `.gitignore` and curated bundle are safeguards; the original working folder should not be blindly staged.

[Source attribution and licence review](DATA_SOURCES_AND_LICENSES.md). NHSBSA states OGL v3.0. The direct National Archives licence page returned HTTP 403 during this review; official indexed text and publisher attribution were checked, and this access limit is disclosed. No organizational endorsement or official NHS/Axtria branding is claimed. Source-code licence selection remains an owner decision; [notice](../CODE_LICENSE_NOTICE.md). Public release is pending that decision and explicit authorization. No remote creation, push, cloud publication or external contact occurred.

## Documentation and architecture

README rewritten for a recruiter/reviewer with exact definitions, verified values, setup, limitations and actual screenshots. [Architecture](PROJECT_ARCHITECTURE.md) includes Mermaid source, SVG and raster rendering using a single canonical node/edge list. [Demo](PHASE7_SIX_MINUTE_DEMO.md) has a timed six-minute script and interruption responses. [Interview bank](PHASE7_INTERVIEW_QA.md): 65 substantial answers in nine categories, each with four points, technical explanation, project example, follow-up and mistake. [Defense](PHASE7_PROJECT_DEFENSE.md) and [resume wording](PHASE7_RESUME_BULLETS.md) avoid invented accomplishments.

## Clean setup and CI

Fresh dashboard-only venv and separate checkout: True; system-site packages disabled, all 52 registered Parquet inputs copied unchanged, entrypoint and six pages rendered, HTTP health/root checked and owned listener closed. Two clean smoke tests passed. Direct pins and transitive freeze are recorded. This is not a complete source-acquisition-to-model rebuild. Full original analytical regression is separate. [Reproducibility guide](REPRODUCIBILITY_GUIDE.md).

GitHub Actions config runs a data-free fixture suite and fatal static checks on Python 3.12. Local equivalent execution is recorded. No remote Actions run occurred. Full-data CI is not configured because immutable artifact provisioning has not been implemented; full regression is currently a local command with the original artifacts.

## Presentation

[Actual PowerPoint](../deliverables/Phase7_Axtria_Project_Presentation.pptx): 12 slides with speaker notes, charts from reconciled historical/model/scenario facts, rendered architecture and a real dashboard screenshot. ZIP/XML structure and embedded media are checked. Microsoft PowerPoint exported all twelve slides and a PDF; the assistant inspected every native slide image. No clipping or overlap was observed. [PDF copy](../deliverables/Phase7_Axtria_Project_Presentation.pdf). This is native visual verification, not a claim that the user rehearsed or reviewed the deck.

## Tests and preservation

Final full regression: 324 passed, 0 failed; test skips: 0. Existing baseline was 296 passing tests. The suite adds meaningful release, documentation, arithmetic, isolated-session and CI-fixture checks. Public summary is bundled as `PORTFOLIO_VALIDATION.json`; detailed local evidence is in `outputs/phase7/validation`.

Protected artifacts: 497 / 497 unchanged; changed list []. Phase 1–6 audits and analytics are untouched. No earlier-phase audit writer is invoked to produce a new Phase 7 status.

## Release recommendation and status boundaries

Completed and verified where evidence above says passed: numerical checks, artifact preservation, local runtime, scoped browser/interaction QA, static checks, release structure and full regression. Completed but not visually verified: no remaining generated presentation asset in the reviewed scope; broader dashboard inspection remains scoped. Blocked/pending owner decision: source-code licence and publication authorization. Not attempted: GitHub push/remote Actions, cloud deployment, external business validation, prospective 2026 evaluation, full clean historical pipeline rebuilding, exhaustive accessibility/load testing. Use for local interview preparation after reviewing the material. Do not claim full public or production release readiness until the pending decisions are resolved.
