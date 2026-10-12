"""Build recruiter-facing documents from reconciled facts and executed evidence."""
import json
from pathlib import Path
from .common import ROOT,write_json

FLOW=[('source','NHSBSA monthly PCA','Source'),('ingest','Immutable API snapshots','Processing'),('quality','Quality and provenance checks','Processing'),
      ('clean','Monthly analytical data','Processing'),('sql','DuckDB fact and SQL views','Analytical'),('stats','Statistical diagnostics','Analytical'),
      ('forecast','Frozen rolling-origin forecasts','Forecasting'),('decision','Monitoring and scenarios','Decision'),('marts','Validated reporting marts','Decision'),('dashboard','Streamlit and Plotly','Presentation')]

def write(root,name,text):
    p=root/name; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text.strip()+'\n',encoding='utf-8')

def build(root=ROOT):
    v=root/'outputs/phase7/validation'; f=json.loads((v/'verified_facts.json').read_text())
    national={r['model']:r for r in f['national_holdout_models']}; ets=national['damped_ets']; naive=national['naive']; ridge=national['ridge']
    d=f['decomposition_2025']; checks=json.loads((v/'numerical_summary.json').read_text())
    startup='.venv\\Scripts\\python.exe -m streamlit run app.py --server.address 127.0.0.1 --server.port 8501 --server.headless true'
    money=lambda x:f'£{x:,.2f}'
    mermaid='flowchart TD\n'+ '\n'.join(f'    {key}["{label}"]' for key,label,_ in FLOW)+'\n'+ '\n'.join(f'    {a[0]} --> {b[0]}' for a,b in zip(FLOW,FLOW[1:]))+'\n    validation["Hashes, contracts, reconciliation, tests and browser QA"]\n    validation -.-> quality\n    validation -.-> forecast\n    validation -.-> marts\n    validation -.-> dashboard\n'
    write(root,'docs/assets/architecture.mmd',mermaid)
    write_json(v/'architecture_flow.json',{'nodes':FLOW,'edges':[[a[0],b[0]] for a,b in zip(FLOW,FLOW[1:])],'cross_cutting_validation':True})
    colors={'Source':'#176B87','Processing':'#286E57','Analytical':'#4A578F','Forecasting':'#925C22','Decision':'#914966','Presentation':'#176B87'}
    svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="650" viewBox="0 0 1200 650" role="img" aria-labelledby="title desc">',
        '<title id="title">PharmaLens architecture</title><desc id="desc">Immutable public data through quality, SQL, statistics, frozen forecasts, decisions and dashboard, with cross-cutting validation.</desc>',
        '<rect width="1200" height="650" fill="#F6F8FB"/>','<text x="50" y="55" font-family="Arial" font-size="30" fill="#142B45">PharmaLens · evidence from source to screen</text>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8 Z" fill="#36516D"/></marker></defs>']
    positions=[]
    for i,(key,label,layer) in enumerate(FLOW):
        row=i//5; col=i%5 if row==0 else 4-i%5; x=40+col*235; y=115+row*220; positions.append((x,y))
        words=label.split(); lines=[''];
        for word in words:
            if len(lines[-1]+' '+word)>22: lines.append(word)
            else: lines[-1]=(lines[-1]+' '+word).strip()
        svg.append(f'<rect x="{x}" y="{y}" width="210" height="140" rx="12" fill="white" stroke="#D8E1EB"/><rect x="{x}" y="{y}" width="210" height="8" rx="4" fill="{colors[layer]}"/>')
        svg.append(f'<text x="{x+15}" y="{y+38}" font-family="Arial" font-size="13" fill="{colors[layer]}">{i+1:02d} · {layer}</text>')
        for j,line in enumerate(lines): svg.append(f'<text x="{x+15}" y="{y+68+24*j}" font-family="Arial" font-size="17" fill="#142B45">{line}</text>')
    for i,((x,y),(xx,yy)) in enumerate(zip(positions,positions[1:])):
        a=(x+210,y+90) if i<4 else (x+105,y+140) if i==4 else (x,y+90)
        b=(xx,yy+90) if i<4 else (xx+105,yy) if i==4 else (xx+210,yy+90)
        svg.append(f'<line x1="{a[0]}" y1="{a[1]}" x2="{b[0]}" y2="{b[1]}" stroke="#36516D" stroke-width="2" marker-end="url(#arrow)"/>')
    svg+=['<rect x="40" y="545" width="1150" height="65" rx="10" fill="#142B45"/>','<text x="60" y="584" font-family="Arial" font-size="20" fill="white">Validation across layers: source hashes · contracts · independent checks · tests · browser QA</text>','</svg>']
    write(root,'docs/assets/architecture.svg',''.join(svg))
    write(root,'docs/PROJECT_ARCHITECTURE.md',f'''# Project architecture

![System architecture](assets/architecture.svg)

## Reproducible diagram source

```mermaid
{mermaid}```

The [Mermaid source](assets/architecture.mmd) and SVG are generated from the same ordered flow in `src/phase7_portfolio.py`; the SVG is a reproducible vector diagram, not a screenshot. Source records retain immutable acquisition receipts. Monthly rows are keyed by month, BNF presentation and region with physical unit retained. SQL uses explicit grains, calendar joins and weighted ratios. Phase 3 describes observations; it does not create causal features. Phase 4 accepts origin-sliced training, freezes development choices and evaluates holdout. Phase 5 exposes illustrative monitoring policies and accounting assumptions. Phase 6 consumes hash-checked Parquet marts read-only.

## KPI lineage

| Display | Input columns / transformation | Period and unit | Screen |
|---|---|---|---|
| Total items | `cost_analytics.prescription_items`, observed sum | Active month window; prescription items | Executive |
| NIC | `cost_analytics.net_ingredient_cost_gbp`, observed sum | Active window; GBP | Executive |
| Weighted NIC/item | sum NIC / sum items, positive denominator | Same scope; GBP/item | Executive, regional, presentation |
| Annual change | current complete year / preceding complete year − 1 | Two complete years; percent | Executive, regional, presentation |
| Region/presentation count | distinct keys in filtered observed fact | Active window; entities | Executive |
| Contributions | filtered group sum / disclosed observed denominator | Year/window; percent | Regional/presentation |
| Forecast accuracy | stored successful paired origins; train-only scale | Development or final holdout; explicit horizon | Forecasting |
| Monitoring | stored normalized components and configured weights | Fixed Phase 5 cohort; score and tier | Decision |
| Scenario NIC | baseline items × (1+v) × baseline NIC/item × (1+c) | Stated historical/retrospective baseline; hypothetical GBP | Scenario |

The complete dataset paths, schemas, keys and hashes are in `config/dashboard_manifest.json`. Machine inventory and lineage evidence remain in `outputs/phase7/validation`. Physical quantities are not aggregated across incompatible units. Missing cells remain unknown. Presentation aggregates with partial regional coverage are explicitly limited.
''')
    write(root,'docs/DATA_SOURCES_AND_LICENSES.md','''# Data sources, attribution and licences

Verified on 12 October 2026 against the [official NHSBSA PCA dataset page](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data). Publisher: NHS Business Services Authority. Dataset: Prescription Cost Analysis (PCA) Monthly Administrative Data. The project selects atorvastatin, chemical code `0212000B0`, England community dispensing, January 2023–December 2025. Acquisition uses the linked CKAN API and preserves response hashes and download receipts.

The publisher identifies **Open Government Licence 3.0** and requires source attribution. Suggested citation: NHS Business Services Authority, “Prescription Cost Analysis (PCA) Monthly Administrative Data”, NHSBSA Open Data Portal, accessed 12 October 2026, with the dataset link above. Contains public sector information licensed under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). The direct licence page returned HTTP 403 during this session; its indexed official text was reviewed, while applicable licence identity and attribution were directly verified on the dataset page. [The National Archives explains non-endorsement and third-party/logo exclusions](https://www.nationalarchives.gov.uk/freedom-of-information/requests/cas-282114/).

Transformations include cleaning, aggregation, weighted ratios, diagnostics, forecasts and derived monitoring/scenario outputs; these are project calculations, not NHSBSA publications. Dataset licensing does not automatically license source code, dependency code, trademarks, logos, personal data or third-party material. No NHS/Axtria logos are used. Source-code ownership/licence selection remains a release decision for the owner; this phase does not grant unverified rights over contributors' work. Dependency licences should accompany distribution where their terms require it.

PCA reflects reimbursed community dispensing, excludes several non-community/unsubmitted categories, and is published retrospectively. It is not manufacturer revenue, unique patients, adherence or all pharmaceutical demand. The project uses a fixed downloaded vintage and does not reconstruct historical release availability. The publisher asks planned public-data publications to contact its data service to prevent misrepresentation; no contact was sent in this session. Recheck publisher guidance before public distribution. This is an independent educational portfolio without NHSBSA, NHS or Axtria endorsement.
''')
    write(root,'docs/REPRODUCIBILITY_GUIDE.md',f'''# Reproducibility guide

## Dashboard-only setup

Use Python 3.12 in a new directory. Extract the reviewed `PharmaLens_Phase7_Portfolio.zip` package; it contains the application, relative-path source, all registered Parquet datasets and methodology. The working repository ignores bulky raw data and generated outputs, so a code-only clone does not automatically contain analytical inputs.

The archive also includes `requirements-dashboard-lock.txt`, captured from the successfully tested fresh environment. Use `python -m pip install -r requirements-dashboard-lock.txt` to reproduce those transitive versions on the same Python/runtime platform. `requirements-dashboard.txt` retains the portable direct dependency pins; dependency resolution on another platform is a separate check.

```powershell
python -m venv .venv
.venv\\Scripts\\python.exe -m pip install -r requirements-dashboard.txt
{startup}
```

Linux/macOS use `.venv/bin/python` instead. Open `http://127.0.0.1:8501`; Ctrl+C stops the foreground server. Restore the matching manifest and data if hashes do not match; never regenerate hashes to conceal a defect. Raw snapshots, DuckDB and model fitting are unnecessary for dashboard-only execution.

## Clean execution evidence

`src.phase7_clean` creates a separate environment with **no system site packages** and a minimal copied runtime checkout. Pinned direct dependencies plus pytest are installed there. It validates every registered contract, exercises all pages and the app entry through AppTest, then launches and closes a real HTTP server. Result and full transitive dependency freeze are recorded in `outputs/phase7/validation/clean_environment.json` and `clean_requirements_lock.txt`. Consult the final audit for executed status; this guide does not infer success from environment creation alone.

## Full historical analytical reproduction

The original raw API snapshots, acquisition receipts, processed artifacts and earlier source guards are needed for exact historical reproduction. Current online data may have revisions. The source code has explicit observed and synthetic modes; synthetic data is never a substitute for portfolio results. Existing complete artifacts are verified read-only in Phase 7; models are not retrained.

```powershell
python -m venv .venv
.venv\\Scripts\\python.exe -m pip install -r requirements.txt
.venv\\Scripts\\python.exe -m pytest -q
```

Original phase commands are documented below as historical reproduction instructions, **not executed by Phase 7**:

```powershell
.venv\\Scripts\\python.exe run_pipeline.py --phase 1
.venv\\Scripts\\python.exe run_pipeline.py --phase 2
.venv\\Scripts\\python.exe run_pipeline.py --phase 3
.venv\\Scripts\\python.exe run_pipeline.py --phase 4
.venv\\Scripts\\python.exe run_pipeline.py --phase 5
```

Use an isolated copy for those commands; they can write outputs. A fresh download is a new vintage and requires a separately versioned release. Frozen historical scores must not be overwritten. The full-data regression suite includes controlled pipeline integration tests whose deterministic artifacts are checked against protection hashes; this is distinct from rebuilding every historical phase in a clean environment.

## Audit and CI

Install `requirements-portfolio.txt` for Ruff, Playwright and python-pptx. Browser QA uses an installed Chrome/Edge on this Windows workstation. `python -m src.phase7_audit --run-tests` executes independent reconciliation, static/security checks, regression, clean-runtime evidence checks and preservation. The data-free GitHub Actions job runs `pytest tests/ci --confcutdir=tests/ci`; full-data integration remains local until immutable-artifact provisioning is implemented. No remote Actions result is claimed.

The release archive excludes raw snapshots, credentials, environment files, caches and private logs. Sanitized release copies are distinct from protected originals. All package entries have a hash inventory. Validate package hashes before running it; a public release still requires owner licence review and authorization.
''')
    write(root,'docs/PHASE7_FORECASTING_DEFENSE.md',f'''# Forecasting and statistical defense

## Forecasting design

The primary target is monthly prescription items. A contiguous monthly calendar and 24-month initial training window define expanding origins. Development targets are January–June 2025. Final holdout targets are July–December 2025, with origins constrained to June 2025 or later. True horizons are 1, 2 and 3 months. Each series contributes at most 6, 5 and 4 holdout cells respectively; these 15 errors overlap targets and are not 15 independent months.

Five real model families are fitted: last-value naive, seasonal naive lag 12, drift, damped additive nonseasonal ETS, and direct-horizon StandardScaler plus Ridge. Ridge features use origin-known lags and rolling history plus known target-month sine/cosine. Supervised labels end within each origin's training cutoff. Scalers fit inside each origin/horizon pipeline. Alpha candidates 0.1/1/10/100 and family choices use development only. ETS scale is the training mean; optimization failures are retained as failures, not relabelled fallback predictions.

Selection pools scaled errors by aggregation level, with a 2% near-tie simplicity rule and deterministic alpha tie behavior. Frozen national and regional choices are damped ETS; eligible region/presentation series use Ridge alpha 10. Frozen decisions are persisted before holdout evaluation. Later origins may refit parameters on newly observed outcomes, but architecture, alpha and operational choice remain frozen. Phase 5/6 display and diagnose errors without reselecting the model.

## Independent review and metrics

Phase 7 independently recomputes origin-target alignment, origin-only naive scaling and pooled metrics using stored records and Python reductions. Five-family comparisons use exactly common successful cells; failures are not zero errors. National ETS holdout MASE is {ets['MASE']:.6f}, MAE {ets['MAE']:,.2f} items, RMSE {ets['RMSE']:,.2f} and WAPE {ets['WAPE']:.6f}%. Naive MASE is {naive['MASE']:.6f}; observed ETS improvement is {100*(1-ets['MASE']/naive['MASE']):.2f}%. Ridge MASE is {ridge['MASE']:.6f}. Ridge's lower observed holdout value does not authorize retrospective selection; doing so would consume the evaluation set as tuning evidence.

MASE averages absolute forecast error divided by that origin's training-only adjacent naive error. WAPE is total absolute error divided by total absolute actuals, multiplied by 100. Bias is mean prediction minus actual. MAE and RMSE preserve target units. A zero/undefined naive scale leaves MASE unavailable; failed predictions remain missing. Pooling and equal-series means are distinguished in the decision dictionaries; presentation forecasts cannot be inferred by relabelling an eligible regional subset.

Only 28 eligible region/presentation histories are forecast, alongside seven regions and one national series. They are not the complete pharmaceutical market. Direct national and sums of seven regional forecasts are not forced coherent; signed/absolute hierarchy gaps are disclosed. Empirical interval calibration requires 20 development residuals per series/horizon, but only 6/5/4 exist; intervals and coverage remain unavailable. January–March 2026 outputs are retrospective with a December 2025 **observation** cutoff, not real-time December-issued operational forecasts.

## Statistical audit

Phase 3 calendar indexing preserves elapsed months across gaps. OLS slopes describe associations; HAC lag 3 uncertainty is conditional on a short time-series specification, not confidence around fixed aggregate totals. Incomplete histories withhold HAC intervals rather than compressing calendar gaps. Theil–Sen and descriptive Kendall assess direction robustness, not causal or independent-sample significance. Robust STL period 12, raw/detrended ACF and day-adjusted indices are diagnostics; three annual cycles cannot establish stable seasonality. Original IQR flags remain; MAD, MoM and prior rolling-median flags are review signals, not confirmed errors. Some anomaly classifications look forward and are labelled retrospective; they are not model-training interventions.

The exact symmetric NIC decomposition allocates an accounting identity across volume, presentation mix and within-presentation NIC/item. Phase 7 checks it with closed-form interaction allocation independently of the production permutation implementation. It cannot identify causal price changes, negotiations, patent expiry, clinical shifts or realized savings.

## Likely objections and defensible responses

| Objection | Defensible response |
|---|---|
| “Is this leakage free?” | Origin-sliced features, labels/scalers and tuning were reviewed and checked. The fixed vintage does not reconstruct when revised records were actually published; this is retrospective observation-cutoff validation, not a historical release-time simulation. |
| “Why ETS over better holdout Ridge?” | Development froze ETS. Preserve the holdout as evaluation; reassess in a new prospective experiment. |
| “Does MASE below one prove superiority?” | It describes average error relative to training naive scale. Short overlapping errors do not establish universal or statistically proven superiority. |
| “Why no confidence bands?” | Calibration support fails the documented threshold; drawing unsupported bands would misrepresent uncertainty. |
| “Why not deep learning?” | Short histories favor disciplined simple benchmarks. More complexity needs more data and a fresh validation plan. |
| “Can this transfer to India?” | No. Geography, reimbursement and patient/business contexts differ. Rebuild the data definition and validate locally. |
| “Are the forecast hierarchy gaps an error?” | They are disclosed differences between independently fitted levels. Reconciliation would require a separately evaluated design. |

Next validation should use fresh release-dated observations, more annual cycles, broader medicines and prospectively locked models. No model was retrained or reselected in Phase 7.
''')
    previews='\n'.join(f'- [{title}](assets/screenshots/{name}.png)' for _,title,name in __import__('src.phase7_browser',fromlist=['PAGES']).PAGES)
    write(root,'docs/PHASE7_SIX_MINUTE_DEMO.md',f'''# Six-minute interview demonstration

Practice script; describe the project as AI-assisted and adapt ownership claims to work you actually reviewed. Open the local app before the interview. Avoid live dependency installation or model fitting.

| Time | Page / exact action | Metric and spoken explanation | Transition |
|---|---|---|---|
| 0:00–0:40 | Executive Overview, default full window | “This independent project turns NHSBSA atorvastatin community-dispensing records into traceable prescribing intelligence. It covers {f['months']} months, {f['regions']} regions and {f['presentations']} presentations. Items are recorded prescription occurrences; NIC is ingredient cost, not manufacturer revenue.” | “I first made the grain and provenance explicit.” |
| 0:40–1:25 | Open architecture diagram and SQL grain; return Executive | “{f['source_records']:,} source rows become {f['analytical_rows']:,} monthly rows without losing item or NIC totals. DuckDB separates dimensions, facts, calendar coverage and reporting views. Missing activity remains unknown, and quantities in different units stay separate.” | “That foundation makes the aggregate story defensible.” |
| 1:25–2:15 | Executive annual growth; complete-year decomposition choose 2025 vs 2024 | “2025 item volume increased {f['item_growth_2025_pct']:.2f}%, while NIC changed {f['nic_growth_2025_pct']:.2f}%. Volume and mix contributions were positive; the within-presentation ratio contribution was negative. This reconciles an accounting identity rather than explaining a causal price mechanism.” | “I then tested whether the activity could be forecast.” |
| 2:15–3:20 | Forecasting, national/holdout; change horizon 1→3 and inspect hover | “The operational model was frozen using development only. Final holdout errors use true horizons and origin-only scales. ETS MASE pooled over horizons is {ets['MASE']:.4f}; this screen's selected-horizon cards may differ. Ridge's lower final observed error never changes the frozen selection. Short calibration support means no interval bands.” | “Forecast uncertainty feeds analyst review, not an opportunity claim.” |
| 3:20–4:25 | Decision Intelligence, regional then presentation; inspect evidence and alternate policy | “All seven regional ranks are policy-sensitive. Thirteen presentations lack required forecast evidence and remain unscored, rather than receiving a bad rank. Weights prioritize investigation, and each recommendation links to a source row.” | “The last page makes planning assumptions explicit.” |
| 4:25–5:20 | Scenario Simulator, observed 2025/all regions/all presentations; set +5 and −5 sliders | “NIC is baseline items times the volume multiplier times baseline NIC/item times its multiplier. These changes yield {money(f['nic_2025_gbp']*1.05*.95)} hypothetical NIC. A 5% volume increase requires −4.761905% unit-cost change for accounting equality. No realized savings, causality or clinical substitution is implied.” | “The useful outcome is transparent analysis with testable boundaries.” |
| 5:20–6:00 | Open Phase 7 audit and limitations | “The project is reproducible from preserved evidence, with independent arithmetic, UI tests and real-browser checks. It is not company deployment or patient-level analysis. I would first add release-aware fresh data and business-user validation before operational decisions.” | Invite a question about SQL, leakage, weights or accounting. |

## Interruptions and recovery

- **“Why no manufacturer sales?”** Explain public data availability and the distinction between dispensing and commercial sales. Return to the displayed scope, not a hypothetical revenue estimate.
- **“Why isn't Ridge selected?”** Point to development freeze; clarify holdout must remain evaluation. Resume with horizon support.
- **“Did you write all of this manually?”** State that Codex generated and executed substantial implementation and audit work. Explain only the parts you personally reviewed and can reproduce; never imply independent manual authorship.
- **“Where is the deployed app?”** State actual local/browser status. A release package and guide are not cloud deployment.
- **Technical delay:** Use the actual captured screenshots and presentation; say that the fallback is a captured view, not a live interaction. Do not fabricate a successful control response.

{previews}
''')
    write(root,'docs/PHASE7_RESUME_BULLETS.md',f'''# Resume, LinkedIn and repository wording

Use only after reviewing and being able to explain the work. Codex implemented and executed substantial parts; these are project-level evidence statements, not proof of independent manual authorship or professional client experience.

**Title:** PharmaLens — Pharmaceutical Prescribing Intelligence and Forecast Validation.

**One line:** AI-assisted educational portfolio combining public NHSBSA atorvastatin data, DuckDB SQL, statistical diagnostics, frozen forecasting, decision analytics and Streamlit.

## Three concise evidence bullets

- AI-assisted portfolio processes {f['source_records']:,} NHSBSA records into {f['analytical_rows']:,} validated monthly rows covering {f['months']} months and seven reported regions.
- Implements DuckDB reporting and rolling-origin evaluation of five forecasting families across 36 series, preserving development-only model choices and explicit uncertainty limits.
- Provides a six-page Streamlit dashboard with traceable monitoring evidence, hypothetical accounting scenarios, filtered CSV exports and independently reconciled metrics.

## Four technical bullets

- Explicit monthly fact grain, dimension joins and calendar missingness prevent duplicate aggregation and false zero imputation.
- Origin-sliced Ridge features/scalers, damped ETS and naive benchmarks use 1–3 month horizons with frozen selections before final holdout.
- Monitoring components, policy sensitivity and evidence-linked investigations retain 13 unscored presentations instead of manufacturing rankings.
- Hash protection, independent numerical reductions, AppTest, browser screenshots and a separate runtime environment support reproducibility; use the final audit for current passing counts.

## Business analytics version

- Investigates divergence between observed prescribing activity and ingredient cost without claiming revenue, patients or realized savings.
- Separates descriptive evidence, historical model results, review policy and hypothetical planning assumptions.
- Connects executive filters and proposed investigations to source definitions and disclosed reporting denominators.

## Data science version

- Evaluates five actual model families with time-ordered development/holdout evidence and training-only preprocessing.
- Reports scaled and unit-based errors, failures, overlapping-target limits and absent calibrated intervals.
- Uses robust descriptive diagnostics and score/scenario sensitivity while preserving frozen historical outputs.

**LinkedIn:** “An AI-assisted public-data portfolio exploring atorvastatin community dispensing in England. The project combines provenance, SQL marts, statistical diagnostics, retrospective forecasting, monitoring-priority sensitivity and an interactive dashboard. It emphasizes traceability and limitations; it does not represent company work or demonstrated commercial impact.”

**GitHub description:** End-to-end pharmaceutical prescribing intelligence using NHSBSA data, SQL, statistical analysis, forecasting, decision analytics and Streamlit.

Never claim increased sales, reduced actual expenditure, improved patient outcomes, proprietary Axtria data, client delivery, company deployment or independent authorship of Codex-generated work. If discussing personal contributions, name the actual review, modification or explanation you performed.
''')
    write(root,'docs/PHASE7_PROJECT_DEFENSE.md',f'''# Project defense and honest limitations

## Purpose, scope and architecture

This educational project was chosen to connect analyst-relevant data engineering, SQL, statistics, forecasting and decision communication using an accessible public source. That rationale does not imply the user's personal career history. The business question is how observed dispensing activity, ingredient cost and model reliability vary, and which analytical questions deserve review. It is not a sales optimization or patient-outcomes model.

NHSBSA atorvastatin PCA data cover England community dispensing, January 2023–December 2025. The fact grain is month × region × presentation, retaining physical unit. Immutable acquisition receipts feed cleaned data, DuckDB reporting, diagnostics, frozen models, decision marts and a read-only Streamlit dashboard. See [architecture](PROJECT_ARCHITECTURE.md), [numerical reconciliation](PHASE7_NUMERICAL_RECONCILIATION.md) and [forecast defense](PHASE7_FORECASTING_DEFENSE.md).

## Findings and analytical approach

Observed totals are {f['historical_items']:,} prescription items and {money(f['historical_nic_gbp'])} NIC. Latest annual items increased {f['item_growth_2025_pct']:.2f}%, while NIC changed {f['nic_growth_2025_pct']:.2f}%. Exact decomposition separates accounting contributions; external causal reasons remain unidentified. Calendar-aware OLS/HAC, Theil–Sen, Kendall, STL/ACF and retained anomaly flags support descriptive robustness, not causal inference.

Forecasting uses expanding origins and a development-only freeze. ETS remains operational nationally even though final observed Ridge MASE is lower. Monitoring combines transparent components under illustrative weights; all seven regional ranks are policy-sensitive and 13 presentations remain unscored. Scenario NIC multiplies explicit volume and unit-cost assumptions, with constrained mix redistribution as a separate simulation. Dashboard filters preserve declared denominators, cached data are copied, and source rows are accessible.

## Validation strategy

Phase 7 preserves prior artifacts and independently verifies raw totals, group identities, ratios, decomposition, forecast metrics/scales, scores and scenarios. Static and redacted secret checks complement meaningful tests. Real Chrome captures and checks rendered pages and selected journeys. The clean runtime is separate from the working environment; full analytical rebuilding is deliberately not performed. The final audit separates executed checks from remote Actions/cloud deployment.

## Questions that could expose weaknesses

| Interview question | Actual limitation | Defensible answer | Do not claim |
|---|---|---|---|
| Is this demand? | Reimbursed dispensing records are a partial activity proxy | Define the recorded item and excluded settings before using demand language | Total market or unmet patient demand |
| Could December data be known in December? | Publication lag and revisions are not replayed | The cutoff is an observation month; this is fixed-vintage retrospective evaluation | Real-time December decision simulation |
| Are regional differences performance differences? | No population/case-mix denominator | Compare observed totals and conditional shares, then request suitable denominators | Efficiency or clinical superiority |
| Does short holdout prove ETS best? | Six months, overlapping cells, retrospectively available source | State observed metrics and frozen selection discipline; seek prospective evidence | Proven universal superiority |
| Are weights objective? | Illustrative policy, sensitivity changes ranks | Show assumptions and stable/unscored distinctions; validate with domain users | Commercial opportunity ranking |
| Why no intervals? | Calibration count below documented threshold | Leave bounds unavailable and explain the evidence required | Guaranteed coverage or probability bands |
| Did AI do the work? | Codex wrote and executed substantial implementation | Explain AI assistance explicitly, demonstrate understanding and independent evidence | Personal manual implementation history |
| Did the project save money? | Deterministic hypothetical accounting | Show formula and assumptions; no actual intervention occurred | Realized savings or business impact |
| Is this production ready? | No cloud rollout, business-user acceptance or capacity/security operations | Demonstrate local QA/package readiness and list operational prerequisites | Company deployment or SLA |

## Next improvements

Fresh release-dated data and longer prospective evaluation come first. Add business-user feedback and aligned real commercial data if authorized; reassess medicine/geography scope, patient/population denominators, calibrated uncertainty, coherent hierarchies, accessibility and operational access/load controls in separate versioned work.
''')
    readme=f'''# PharmaLens — Pharmaceutical Prescribing Intelligence

## Executive summary

An independent, AI-assisted analytics portfolio that turns public NHSBSA atorvastatin records into traceable prescribing insights, retrospective forecast evaluation and an interactive dashboard. Prepared for an Axtria Analyst interview discussion; no NHSBSA or Axtria endorsement, client work or deployment is implied.

## Problem statement

How do recorded prescription items and ingredient cost change across months, regions and presentations? How reliable are simple forecasts, and which analytical uncertainties deserve review? The project separates observed findings, model evidence, policy assumptions and hypothetical accounting.

## Dataset and scope

| Scope | Verified value |
|---|---|
| Publisher / medicine / geography | NHSBSA monthly PCA / atorvastatin / England community dispensing |
| Historical window | January 2023–December 2025; {f['months']} months |
| Source / analytical records | {f['source_records']:,} / {f['analytical_rows']:,} |
| Reported regions / presentations | {f['regions']} / {f['presentations']} |
| Fact grain | Month × region × BNF presentation, retaining unit |

## Key verified findings

- Historical activity: **{f['historical_items']:,} prescription items** and **{money(f['historical_nic_gbp'])} NIC**.
- 2025 versus 2024: items **+{f['item_growth_2025_pct']:.2f}%**, NIC **{f['nic_growth_2025_pct']:.2f}%**.
- NIC accounting change: volume **{money(d['item_volume_effect_gbp'])}**, presentation mix **{money(d['presentation_mix_effect_gbp'])}**, within-presentation NIC/item **{money(d['within_presentation_cost_per_item_effect_gbp'])}**; total **{money(d['observed_cost_change_gbp'])}**. This identity is not a causal explanation.
- National ETS holdout MASE **{ets['MASE']:.4f}**, WAPE **{ets['WAPE']:.3f}%**. Ridge's lower final observed error does not replace the development-frozen ETS choice.
- **{f['unscored_presentations']} presentations remain unscored**; all **{f['regional_unstable_ranks']} regional ranks** are policy-sensitive. Proposed investigations are not observed business actions.

## Dashboard preview

![Real local Chrome capture — Executive Overview](docs/assets/screenshots/01_executive_overview.png)

These are actual local browser captures, not generated mockups. [All six screenshots](docs/PHASE7_SIX_MINUTE_DEMO.md) accompany the demo; desktop, laptop, tablet and mobile checks are recorded in the final audit. Screenshot views are historical defaults, not current forecasts.

## Features

Interactive scope filters, weighted KPIs, source/formula explanations, origin-labelled forecast markers, scored/unscored monitoring views, validated policy sensitivity, searchable investigation evidence, bounded accounting scenarios and filtered CSV downloads. The runtime reads registered hash-checked Parquet datasets without retraining models.

## Architecture

![Architecture](docs/assets/architecture.svg)

[Detailed architecture and KPI lineage](docs/PROJECT_ARCHITECTURE.md).

## Data pipeline

Immutable API responses and receipts → quality checks → normalized monthly data → analytical SQL → diagnostics → frozen forecasts → decision marts → dashboard. Unknown missing activity stays unknown; physical quantities across incompatible units are not summed.

## SQL analytics

DuckDB uses explicit fact/dimension grains, a calendar, controlled join cardinality and reporting views. Month-on-month changes use adjacent calendar months. Shares disclose their denominator; weighted cost uses ratio of sums. [Metric definitions](docs/METRIC_DEFINITIONS.md).

## Statistical analysis

Calendar-aware OLS with conditional HAC uncertainty, Theil–Sen and descriptive Kendall assess trend robustness. STL, ACF and day-adjusted indices are exploratory with only three cycles. Retained IQR/MAD/change flags are investigation signals. The NIC decomposition is an exact symmetric accounting identity. [Methodology review](docs/PHASE7_FORECASTING_DEFENSE.md).

## Forecasting methodology

Expanding origins, initial 24-month history, 1–3 month horizons, training-only features/scalers, development alpha/family selection and frozen choices precede final holdout evaluation. Evaluation is retrospective fixed-vintage, not a reconstruction of record publication availability. Failed forecasts remain missing. No defensible intervals are supplied.

## Model comparison

| National family | Final holdout MASE | Role |
|---|---:|---|
{chr(10).join('| '+r['model']+' | '+format(r['MASE'],'.4f')+' | '+('Frozen operational choice' if r['model']=='damped_ets' else 'Evaluation benchmark; not selected by holdout')+' |' for r in f['national_holdout_models'])}

Common successful origin/horizon support; overlapping errors limit inference. [Forecasting defense](docs/PHASE7_FORECASTING_DEFENSE.md).

## Decision intelligence

Five normalized review dimensions use configured weights and retain missing evidence. Monitoring scores are policy, not commercial opportunity. {f['manual_review_series']} of 36 selected series require manual review; {f['investigations']} entries are proposed analyst investigations with source traceability.

## Scenario simulator

Hypothetical NIC = baseline items × (1 + volume change) × baseline NIC/item × (1 + unit-cost change). Separate mix transfer preserves total items and nonnegative shares. +5% items and −5% NIC/item imply {money(f['nic_2025_gbp']*1.05*.95)} hypothetical NIC on the observed 2025 baseline. These are not probabilities, causal interventions, savings or clinical substitution advice.

## Dashboard pages

| Page | Purpose |
|---|---|
| Executive Overview | Active-window totals, trends and full-year accounting |
| Regional Intelligence | Scoped comparisons, shares, growth and profile caveats |
| Presentation Intelligence | Concentration, unit-aware presentation evidence and coverage |
| Forecasting & Model Evaluation | Frozen choices, origins/horizons, errors and hierarchy gaps |
| Decision Intelligence | Components, sensitivity, unscored status and proposed investigations |
| Scenario Simulator | Explicit hypothetical volume, cost and mix assumptions |

## Tech stack

Python 3.12, pandas, NumPy, DuckDB, SciPy/statsmodels, scikit-learn, Parquet/PyArrow, Plotly, Streamlit, pytest/AppTest. Phase 7 adds Ruff, Playwright with installed Chrome, and python-pptx for QA/portfolio deliverables.

## Installation

```powershell
python -m venv .venv
.venv\\Scripts\\python.exe -m pip install -r requirements-dashboard.txt
```

Dashboard data must come from the matching validated package; a code-only clone lacks ignored reporting files. Use `requirements.txt` for the full analytical/test environment and `requirements-portfolio.txt` for Phase 7 tooling.

## Running the pipeline

Phase commands are `python run_pipeline.py --phase 1` through `--phase 5`. They are for an isolated historical reproduction with matching source snapshots. Phase 7 verifies existing results without retraining/reselecting or replacing validated data. [Exact reproducibility instructions](docs/REPRODUCIBILITY_GUIDE.md).

## Running the dashboard

```powershell
{startup}
```

Open `http://127.0.0.1:8501`; use `.venv/bin/python` on Linux/macOS. No cloud deployment is claimed.

## Tests

```powershell
.venv\\Scripts\\python.exe -m pytest tests/ci -q --confcutdir=tests/ci
.venv\\Scripts\\python.exe -m pytest -q
.venv\\Scripts\\python.exe -m src.phase7_audit
```

The first command uses deterministic data-free fixtures. Full regression needs original validated artifacts. Phase 7 independently reconciles {checks['checks']:,} calculations; see the [final audit](docs/PHASE7_AUDIT.md) for executed tests, clean setup, browser evidence and protection counts. GitHub Actions is configured; no remote workflow run is claimed.

## Reproducibility

Pinned direct dependencies, recorded transitive environment, source/data hashes, exact contracts and immutable outputs support local reproduction. A separate fresh runtime checkout/venv is exercised. Full original-pipeline rebuilding in that environment is not claimed. [Guide](docs/REPRODUCIBILITY_GUIDE.md).

## Limitations

No manufacturer revenue, unique patients, population/case-mix rates, India transfer, causal NIC mechanism, realized savings or clinical recommendations. Missing activity has unknown mechanisms. Publication lag/revisions are not replayed. Short overlapping holdout, insufficient interval calibration and illustrative review weights limit operational use. Browser checks are scoped, not full accessibility certification or capacity testing.

## Data source and licence

[NHSBSA monthly PCA](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data), accessed 12 October 2026. Contains public sector information licensed under [OGL v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/). [Attribution, exclusions and code-licence status](docs/DATA_SOURCES_AND_LICENSES.md). Source-code licence selection and publication authorization remain owner decisions.

## Future improvements

Fresh release-aware observations, prospective locked evaluation, user-reviewed policies, calibrated uncertainty when supported, hierarchical reconciliation trials, browser/accessibility expansion and a controlled Python-host deployment.

## Portfolio and interview materials

[Rendered PDF](deliverables/Phase7_Axtria_Project_Presentation.pdf). The separate local bundle is `deliverables/PharmaLens_Phase7_Portfolio.zip`; it is not nested inside itself. The deck was rendered by installed Microsoft PowerPoint and all twelve slides were visually inspected by the assistant.

[Presentation](deliverables/Phase7_Axtria_Project_Presentation.pptx) · [Six-minute demo](docs/PHASE7_SIX_MINUTE_DEMO.md) · [Question bank](docs/PHASE7_INTERVIEW_QA.md) · [Defense notes](docs/PHASE7_PROJECT_DEFENSE.md) · [Resume wording](docs/PHASE7_RESUME_BULLETS.md) · [Quality scorecard](docs/PHASE7_QUALITY_SCORECARD.md) · [Release checklist](docs/PHASE7_RELEASE_CHECKLIST.md).

AI assistance: Codex generated and executed substantial implementation/audit work. Project results are supported by reproducible evidence; personal contribution claims should reflect what the owner actually reviewed and understands. GitHub publication, remote Actions and cloud deployment were not performed.
'''
    write(root,'README.md',readme)
    import pandas as pd
    records=pd.read_csv(v/'numerical_reconciliation.csv')
    selected=records[records.metric.str.contains('historical|2025 item annual|2025 NIC annual|2025 vs 2024|national/|accounting offset 5|dashboard',regex=True)]
    lines=['| Metric | Expected | Recomputed | Difference | Tolerance | Status | Source |','|---|---:|---:|---:|---:|---|---|']
    for r in selected.itertuples(): lines.append(f'| {r.metric} | {r.expected:.10g} | {r.recomputed:.10g} | {r.difference:.4g} | {r.tolerance:.4g} | {r.status} | {r.source} |')
    write(root,'docs/PHASE7_NUMERICAL_RECONCILIATION.md',f'''# Independent numerical reconciliation

{checks['checks']:,} checks executed; {checks['failed']} failed. Full machine evidence: `outputs/phase7/validation/numerical_reconciliation.csv`; its SHA-256 is `{checks['sha256']}`. A public copy is packaged with release validation evidence.

Independent here means a separate mathematical reduction, not merely calling a production function. Raw API item/NIC totals use Decimal sums, then reconcile source/clean/fact rows. Group identities and disclosed share denominators reconcile separately. A closed-form allocation of main, pairwise and triple interactions checks the production permutation-based cost decomposition. Forecast metrics use independent reductions on common five-family successful cells; origin-only scales are recomputed from historical observations. Pairwise less/equal counts check percentile midranks independently of pandas.rank. Explicit multiplicative algebra checks scenarios and reciprocal offsets. Dashboard functions are the observed side of comparisons against independently grouped facts.

{chr(10).join(lines)}

Unknown comparisons pass only when both sides are unavailable; no missing value is turned into zero. Integer sums have zero tolerance, GBP accounting uses £0.01, ratios/scores use explicit small floating tolerances. Repeated execution hashes are tested. No protected result is edited when a check fails; the discrepancy is investigated first. The earlier failed draft of this checker compared all successful model rows against paired-support metrics; it was corrected to match the documented denominator, with no analytical output changes.
''')

if __name__=='__main__': build()
