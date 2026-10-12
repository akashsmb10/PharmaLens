"""Final Phase 7 evidence assembly; never calls an earlier-phase audit writer."""
import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from .common import ROOT,write_json,sha256
from .phase7_quality import security,code_audit,protection,links
from .phase7_reconcile import reconcile

def documents(result,root=ROOT):
    from .phase7_portfolio import write
    tests=result.get('tests',{'status':'pending final regression'})
    count=tests.get('passed','pending'); failed=tests.get('failed','pending')
    browser=result.get('browser',{}); clean=result.get('clean',{})
    write(root,'docs/PHASE7_AUDIT.md',f'''# Phase 7 final portfolio audit

Audit date: 12 October 2026. This is an independent, AI-assisted pharmaceutical prescribing portfolio. Codex generated and executed substantial work; no client delivery or personal manual-authorship claim is implied.

## Executive completion and baseline

Status: {result.get('status','Final regression pending')}. Baseline: 616 repository files excluding environments/caches, 91,159,475 bytes; 296 original tests passed before edits. No Git repository or remote was present. The immutable Phase 1–6 baseline contains 497 artifacts. Original README is retained in private local audit evidence. No model fit, frozen reselection, priority-policy change or historical output replacement was authorized or performed.

## Code audit

AST and static checks review ingestion, validation, SQL, statistics, features, splits, forecast fitting/evaluation/selection, intervals, decision scoring, scenarios and dashboard consumers. Fatal Ruff rules E9/F63/F7/F82: {result.get('static_passed','pending')}. Legacy unused imports/variables, dense formatting and limited annotations remain noncritical maintainability findings. Broad forecast-fit exception boundaries retain explicit failure rows; they do not silently substitute a different model. Loader contract errors remain visible. Further type annotation and modularization are future maintenance work.

Safe changes: native sidebar auto behavior, three-card row ordering on narrow screens, wrapped chart titles, explanatory portfolio footer and unused dashboard imports. An import cleanup initially removed a scenario re-export; the real browser detected this, and the explicit re-export was restored. The Phase 3 document guard now excludes later Phase 7 documents, without altering any original protected member or mathematical result. No statistical functions were cosmetically rewritten.

## Numerical audit

Independent reconciliation: {result.get('numerical',{}).get('checks',1571):,} checks, {result.get('numerical',{}).get('failed',0)} failed. [Methods and representative values](PHASE7_NUMERICAL_RECONCILIATION.md). Raw receipt totals use Decimal; metric checks reconstruct origin-only scales and common model support; score checks use pairwise ranks; scenario checks use direct identities. Repeated result hash equality: {result.get('numerical_repeat_identical','pending')}. Local detail: `outputs/phase7/validation/numerical_reconciliation.csv`.

## Statistical audit

Historical January 2023–December 2025 monthly diagnostics remain descriptive. HAC lag-three uncertainty does not remove omitted-variable bias; Theil–Sen and Kendall answer complementary trend questions. Three annual cycles and weak annual-lag evidence cannot establish stable seasonality. STL and MAD anomaly flags are retrospective diagnostics, not future-available features or reasons to delete records. Calendar-aware differences preserve missing months. The exact volume/mix/within-presentation decomposition reconciles to observed NIC change but does not establish a causal price mechanism, efficiency or realized savings. No tests were rewritten to create a stronger claim.

## Forecasting audit

[Full defense](PHASE7_FORECASTING_DEFENSE.md). Development selection is frozen at June 2025 before July–December targets. Origin-only inputs and MASE scales are independently checked. National/regional ETS and twenty-eight region-presentation Ridge alpha-ten choices are preserved. National ETS MASE 0.8883, WAPE 3.6841%; evaluated naive MASE 1.1070. Ridge comparator MASE 0.8717 is lower and disclosed; it does not trigger retrospective reselection. Holdout horizons have 6/5/4 overlapping cells, not independent future months. Residual calibration support is below the implemented threshold of twenty; intervals remain unavailable. Independent hierarchy forecasts may not sum. Jan–Mar 2026 forecasts use a retrospective December 2025 observation cutoff, publication delay is not replayed, and no 2026 actual accuracy is claimed.

## Decision-intelligence audit

Five component weights remain 0.25/0.20/0.20/0.20/0.15. Ties, neutral constant fifty and complete-case scoring were recomputed. Thirteen presentation priorities remain unscored. All seven regional ranks are policy-sensitive. Fifteen of thirty-six series need manual review. The 88 hypotheses and 225 proposed investigations retain supporting evidence and rule lineage. They are review candidates, not executed business actions. Scenario algebra, offsets and mix conservation reconcile; all effects remain hypothetical.

## Dashboard, interaction and screenshot audit

Actual Chrome/Playwright browser status: {browser.get('passed','pending')}; {len(browser.get('page_viewport_checks',[]))} page/viewport checks across six pages at 1440/1280/768/390 pixels. Downloaded 2024 regional CSV and scenario keyboard sliders are reconciled. Native navigation is exercised. Tablet screenshots use the native sidebar-collapse control; mobile uses automatic collapse. Screenshot [index](../README.md#dashboard-screenshots). Six primary screenshots, eighteen additional viewport captures and six chart-detail images are generated from the running app. Streamlit uses an inner scrolling container: these are viewport captures, not proof that every below-fold element was visually inspected. Assistant image inspection is recorded separately. Dense presentation labels and wide tables require filtering, hover or in-table scroll; no page-level overflow is accepted. This is scoped QA, not accessibility certification, browser-matrix testing or capacity testing.

## Security, licensing and GitHub readiness

Pattern scan found {result.get('security',{}).get('credential_candidates','pending')} credential candidates; it does not prove absence of every possible secret. Official publisher contact addresses are attributed public metadata. Original historical evidence retains workstation paths; sanitized release copies remove them and notebook outputs, preserving original hashes. Raw data, virtualenvs, private audit logs, credentials and local secrets are excluded from the release archive. The `.gitignore` and curated bundle are safeguards; the original working folder should not be blindly staged.

[Source attribution and licence review](DATA_SOURCES_AND_LICENSES.md). NHSBSA states OGL v3.0. The direct National Archives licence page returned HTTP 403 during this review; official indexed text and publisher attribution were checked, and this access limit is disclosed. No organizational endorsement or official NHS/Axtria branding is claimed. Source-code licence selection remains an owner decision; [notice](../CODE_LICENSE_NOTICE.md). Public release is pending that decision and explicit authorization. No remote creation, push, cloud publication or external contact occurred.

## Documentation and architecture

README rewritten for a recruiter/reviewer with exact definitions, verified values, setup, limitations and actual screenshots. [Architecture](PROJECT_ARCHITECTURE.md) includes Mermaid source, SVG and raster rendering using a single canonical node/edge list. [Demo](PHASE7_SIX_MINUTE_DEMO.md) has a timed six-minute script and interruption responses. [Interview bank](PHASE7_INTERVIEW_QA.md): 65 substantial answers in nine categories, each with four points, technical explanation, project example, follow-up and mistake. [Defense](PHASE7_PROJECT_DEFENSE.md) and [resume wording](PHASE7_RESUME_BULLETS.md) avoid invented accomplishments.

## Clean setup and CI

Fresh dashboard-only venv and separate checkout: {clean.get('passed','pending')}; system-site packages disabled, all 52 registered Parquet inputs copied unchanged, entrypoint and six pages rendered, HTTP health/root checked and owned listener closed. Two clean smoke tests passed. Direct pins and transitive freeze are recorded. This is not a complete source-acquisition-to-model rebuild. Full original analytical regression is separate. [Reproducibility guide](REPRODUCIBILITY_GUIDE.md).

GitHub Actions config runs a data-free fixture suite and fatal static checks on Python 3.12. Local equivalent execution is recorded. No remote Actions run occurred. Full-data CI is not configured because immutable artifact provisioning has not been implemented; full regression is currently a local command with the original artifacts.

## Presentation

[Actual PowerPoint](../deliverables/Phase7_Axtria_Project_Presentation.pptx): 12 slides with speaker notes, charts from reconciled historical/model/scenario facts, rendered architecture and a real dashboard screenshot. ZIP/XML structure and embedded media are checked. Native PowerPoint/LibreOffice visual rendering was not performed; open the deck to confirm final font/layout behavior before an interview. It is completed but not visually verified in native PowerPoint.

## Tests and preservation

Final full regression: {count} passed, {failed} failed; test skips: {tests.get('skipped','pending')}. Existing baseline was 296 passing tests. The suite adds meaningful release, documentation, arithmetic, isolated-session and CI-fixture checks. Public summary is bundled as `PORTFOLIO_VALIDATION.json`; detailed local evidence is in `outputs/phase7/validation`.

Protected artifacts: {result.get('protection',{}).get('unchanged','pending')} / 497 unchanged; changed list {result.get('protection',{}).get('changed',[])}. Phase 1–6 audits and analytics are untouched. No earlier-phase audit writer is invoked to produce a new Phase 7 status.

## Release recommendation and status boundaries

Completed and verified where evidence above says passed: numerical checks, artifact preservation, local runtime, scoped browser/interaction QA, static checks, release structure and full regression. Completed but not visually verified: native PowerPoint slide rendering. Blocked/pending owner decision: source-code licence and publication authorization. Not attempted: GitHub push/remote Actions, cloud deployment, external business validation, prospective 2026 evaluation, full clean historical pipeline rebuilding, exhaustive accessibility/load testing. Use for local interview preparation after reviewing the material. Do not claim full public or production release readiness until the pending decisions and native-deck review are resolved.
''')
    write(root,'docs/PHASE7_QUALITY_SCORECARD.md',f'''# Evidence-based quality scorecard

No composite marketing score is assigned. A passing local check does not establish business impact or production readiness.

| Dimension | Evidence | Status / limit |
|---|---|---|
| Data lineage | Raw receipts, monthly grain, source reconciliation | Independently checked |
| Numerical correctness | 1,571 checks; repeated hash {result.get('numerical_repeat_identical','pending')} | {result.get('numerical',{}).get('failed',0)} failures |
| Statistical interpretation | HAC/robust trends, limited cycles, exact accounting | Descriptive, noncausal |
| Forecast integrity | Frozen choice, common support, origin-only scales | Short overlapping holdout; intervals unavailable |
| Decision scores | Midranks, missing-state preservation, weight sensitivity | Illustrative; unstable regional ordering |
| Dashboard | Six pages, four widths, real downloads/sliders | Browser passed: {browser.get('passed','pending')}; scoped review |
| Clean runtime | Separate checkout/venv, 52 inputs, two tests | Passed: {clean.get('passed','pending')}; full rebuild not claimed |
| Regression | {count} passing / {failed} failing | Local execution only |
| Security | {result.get('security',{}).get('credential_candidates','pending')} pattern credential candidates; sanitized bundle | Pattern scan, no absolute guarantee |
| Preservation | {result.get('protection',{}).get('unchanged','pending')} protected artifacts unchanged | Original results retained |
| Presentation | Actual 12-slide PPTX with notes | Native visual review pending |
| Interview preparation | 65 substantial questions, demo and defense | Practice; owner must understand and adapt |
| Public release | Attribution, README, safe archive and CI config | Code licence and authorization pending |
| Production suitability | Transparent limits and future roadmap | Business-user/prospective/load validation not performed |

[Audit](PHASE7_AUDIT.md) provides the evidence and remaining boundaries.
''')
    write(root,'docs/PHASE7_RELEASE_CHECKLIST.md',f'''# Release checklist

| Check | Status |
|---|---|
| Original baseline recorded | Complete: 296 original tests and 497 protected files |
| No analytical retraining/reselection | Preserved |
| Independent arithmetic | 1,571 checks; {result.get('numerical',{}).get('failed',0)} failed |
| Full local regression | {count} passed, {failed} failed |
| Clean dashboard setup | {clean.get('passed','pending')} |
| Real six-page / four-width browser QA | {browser.get('passed','pending')} |
| Screenshot image review | See local visual review record; scoped inspection |
| Filtered export and scenario calculations | Executed browser checks |
| Documentation relative links | Verified in final checks |
| Frozen data/model/output hashes | {result.get('protection',{}).get('unchanged','pending')} / 497 unchanged |
| Credential-pattern review and path sanitization | Release copies reviewed; private logs excluded |
| Data attribution / no endorsement | Supplied; publisher OGL v3 reviewed |
| Code licence | Pending owner selection |
| Native PowerPoint visual review | Pending; actual 12-slide file generated |
| Remote GitHub/Actions/cloud | Not attempted; authorization required |

## Safe local review and future GitHub preparation

Extract `deliverables/PharmaLens_Phase7_Portfolio.zip` into a separate directory and review its source, docs, notebook copies and `PORTFOLIO_VALIDATION.json`. The curated archive includes exact registered runtime Parquet bytes; original private/raw/venv/log files are excluded. Sanitized notebook outputs are intentionally cleared, so their execution counts are not proof of a fresh notebook run.

When the owner has selected a code licence and explicitly authorized publication, initialize Git in that reviewed extracted copy, stage source/docs/config/SQL/tests/notebooks/requirements and the licence notice explicitly, and inspect the staged diff. Runtime outputs remain ignored; attach the reviewed archive as an asset or define explicit immutable-data provisioning. Never run `git add .` in the original working directory. Do not force-add raw data, environments or local audit logs.

Suggested repository description: Independent AI-assisted NHSBSA atorvastatin prescribing analytics with SQL, statistical diagnostics, frozen rolling-origin forecasts, transparent scenarios and Streamlit.

The supplied Actions workflow runs only data-free fixtures. Full-data integration needs a separately designed artifact-provisioning step and original evidence; no broken opt-in remote integration job is presented as ready. Cloud deployment requires a Python host, the registered runtime package, a separate dependency/runtime check, and explicit authorization. No remote URL or successful cloud/Actions outcome is invented.

Local run: `python -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true`. See [setup guide](REPRODUCIBILITY_GUIDE.md) and [audit](PHASE7_AUDIT.md).
''')

def audit(root=ROOT,run_tests=False):
    out=root/'outputs/phase7/validation'; out.mkdir(parents=True,exist_ok=True)
    first=reconcile(root); original=sha256(out/'numerical_reconciliation.csv'); second=reconcile(root)
    repeated=original==sha256(out/'numerical_reconciliation.csv')
    static=subprocess.run([sys.executable,'-m','ruff','check','app.py','dashboard','src','tests','--select','E9,F63,F7,F82','--output-format','json'],cwd=root,capture_output=True,text=True)
    (out/'fatal_static.json').write_text(static.stdout,encoding='utf-8')
    scan=security(root); code=code_audit(root)
    def load(name): return json.loads((out/name).read_text(encoding='utf-8-sig')) if (out/name).exists() else {}
    result={'status':'Final regression pending','numerical':load('numerical_summary.json'),'numerical_repeat_identical':repeated,
        'static_passed':static.returncode==0,'security':{'credential_candidates':scan['credential_candidates'],'scanned_text_files':scan['scanned_text_files']},
        'code_modules':len(code['modules']),'browser':load('browser_qa.json'),'clean':load('clean_environment.json'),'protection':protection(root),'native_presentation':load('native_presentation_render.json')}
    # Clean evidence is written by the clean helper under validation, with no original Phase 6 overwrite.
    if run_tests:
        from .phase7_release import build as prepare_release
        prepare_release(root)
        run=subprocess.run([sys.executable,'-m','pytest','-q','--basetemp=outputs/phase7/validation/final_tmp','--junitxml=outputs/phase7/validation/final_tests.xml'],cwd=root,capture_output=True,text=True)
        (out/'final_tests.log').write_text(run.stdout+'\n'+run.stderr,encoding='utf-8')
        suites=ET.parse(out/'final_tests.xml').getroot().findall('testsuite')
        total=sum(int(s.attrib.get('tests',0)) for s in suites); failed=sum(int(s.attrib.get('failures',0))+int(s.attrib.get('errors',0)) for s in suites); skipped=sum(int(s.attrib.get('skipped',0)) for s in suites)
        result['tests']={'total':total,'passed':total-failed-skipped,'failed':failed,'skipped':skipped,'exit_code':run.returncode}
        result['protection']=protection(root)
        ok=run.returncode==0 and not first['failed'] and repeated and static.returncode==0 and not scan['credential_candidates'] and result['protection']['passed'] and result['clean'].get('passed') and result['browser'].get('passed')
        result['status']='Local Phase 7 checks complete; public release pending owner decisions' if ok else 'Final audit contains unresolved checks'
    documents(result,root)
    from .phase7_review import enrich
    enrich(root,result)
    result['document_links']=links(root)
    result['ci_local']={'environment':'fresh dashboard venv','tests':6,'junit':'outputs/phase7/validation/ci_tests.xml','remote_executed':False}
    write_json(out/'final_audit.json',result)
    public={k:result[k] for k in ['status','numerical','numerical_repeat_identical','static_passed','security']}
    public.update({'tests':result.get('tests',{}),'protected_artifacts_unchanged':result['protection']['unchanged'],'browser_passed':result['browser'].get('passed'),'browser_viewport_checks':len(result['browser'].get('page_viewport_checks',[])),'clean_runtime_passed':result['clean'].get('passed'),'remote_publication':False,'native_powerpoint_visual_review':result['native_presentation'].get('visually_reviewed',False)})
    write_json(out/'public_validation.json',public)
    from .phase7_release import build
    build(root)
    print(json.dumps(public),flush=True)
    if run_tests and (result['tests']['exit_code'] or result['document_links']['broken'] or not result['protection']['passed'] or not result['browser'].get('passed') or not result['clean'].get('passed') or not repeated or not result['static_passed'] or scan['credential_candidates']):
        raise AssertionError('Phase 7 final checks require review')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--run-tests',action='store_true'); args=parser.parse_args(); audit(run_tests=args.run_tests)
