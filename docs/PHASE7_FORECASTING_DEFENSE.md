# Forecasting and statistical defense

## Forecasting design

The primary target is monthly prescription items. A contiguous monthly calendar and 24-month initial training window define expanding origins. Development targets are January–June 2025. Final holdout targets are July–December 2025, with origins constrained to June 2025 or later. True horizons are 1, 2 and 3 months. Each series contributes at most 6, 5 and 4 holdout cells respectively; these 15 errors overlap targets and are not 15 independent months.

Five real model families are fitted: last-value naive, seasonal naive lag 12, drift, damped additive nonseasonal ETS, and direct-horizon StandardScaler plus Ridge. Ridge features use origin-known lags and rolling history plus known target-month sine/cosine. Supervised labels end within each origin's training cutoff. Scalers fit inside each origin/horizon pipeline. Alpha candidates 0.1/1/10/100 and family choices use development only. ETS scale is the training mean; optimization failures are retained as failures, not relabelled fallback predictions.

Selection pools scaled errors by aggregation level, with a 2% near-tie simplicity rule and deterministic alpha tie behavior. Frozen national and regional choices are damped ETS; eligible region/presentation series use Ridge alpha 10. Frozen decisions are persisted before holdout evaluation. Later origins may refit parameters on newly observed outcomes, but architecture, alpha and operational choice remain frozen. Phase 5/6 display and diagnose errors without reselecting the model.

## Independent review and metrics

Phase 7 independently recomputes origin-target alignment, origin-only naive scaling and pooled metrics using stored records and Python reductions. Five-family comparisons use exactly common successful cells; failures are not zero errors. National ETS holdout MASE is 0.888323, MAE 242,210.51 items, RMSE 263,898.13 and WAPE 3.684100%. Naive MASE is 1.107000; observed ETS improvement is 19.75%. Ridge MASE is 0.871695. Ridge's lower observed holdout value does not authorize retrospective selection; doing so would consume the evaluation set as tuning evidence.

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
