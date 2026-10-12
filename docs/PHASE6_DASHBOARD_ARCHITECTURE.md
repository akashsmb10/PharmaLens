# Phase 6 dashboard architecture

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
