# Project defense and honest limitations

## Purpose, scope and architecture

This educational project was chosen to connect analyst-relevant data engineering, SQL, statistics, forecasting and decision communication using an accessible public source. That rationale does not imply the user's personal career history. The business question is how observed dispensing activity, ingredient cost and model reliability vary, and which analytical questions deserve review. It is not a sales optimization or patient-outcomes model.

NHSBSA atorvastatin PCA data cover England community dispensing, January 2023–December 2025. The fact grain is month × region × presentation, retaining physical unit. Immutable acquisition receipts feed cleaned data, DuckDB reporting, diagnostics, frozen models, decision marts and a read-only Streamlit dashboard. See [architecture](PROJECT_ARCHITECTURE.md), [numerical reconciliation](PHASE7_NUMERICAL_RECONCILIATION.md) and [forecast defense](PHASE7_FORECASTING_DEFENSE.md).

## Findings and analytical approach

Observed totals are 212,022,236 prescription items and £336,940,603.13 NIC. Latest annual items increased 7.58%, while NIC changed -39.93%. Exact decomposition separates accounting contributions; external causal reasons remain unidentified. Calendar-aware OLS/HAC, Theil–Sen, Kendall, STL/ACF and retained anomaly flags support descriptive robustness, not causal inference.

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
