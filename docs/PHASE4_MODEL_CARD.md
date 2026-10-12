# Phase 4 model card

**Version:** phase4-v1. **Target:** monthly prescription_items. **Intended use:**
reproducible retrospective activity forecasting and analyst-interview demonstration of honest evaluation.
Source: NHSBSA PCA atorvastatin community dispensing, England, Jan 2023–Dec 2025; read-only validated
Phase 2 views and protected monthly Parquet. Data/config hashes and exact environment are in
outputs/phase4/validation/run_metadata.json.

These forecasts represent historical NHS atorvastatin prescribing activity, not pharmaceutical
manufacturer revenue or actual patient demand. Forecasts are not clinical prescribing recommendations.
Forecasts should not be extrapolated directly to India.

## Training, families and selection

24-month initial contiguous training, expanding development origins, shared by aggregation-level
MASE selection with 2.0% simplicity preference. Five families:
naive; seasonal naive 12; drift; damped additive nonseasonal ETS; direct StandardScaler+Ridge.
Effective first-origin Ridge rows 21/20/19; alpha grid 0.1/1/10/100. Failed development configurations
are ineligible for selection. Choices and calibration are persisted before holdout evaluation.

| aggregation_level | selected_model | selected_variant | series |
|---|---|---|---|
| national | damped_ets | damped_ets | 1 |
| region_presentation | ridge | ridge_alpha_10 | 28 |
| regional | damped_ets | damped_ets | 7 |

## Evaluation

Development Jan 2023–Jun 2025, final holdout Jul–Dec 2025, origin-sliced 1–3 month forecasts,
6/5/4 targets per horizon per series. Holdout models may refit on newly observed months but cannot
change architecture or alpha. MASE uses training-only adjacent naive error; MAE/RMSE/WAPE/sMAPE/Bias
are computed from stored predictions. Common-support family comparison accounts for model failures.
National selected model holdout MASE 0.888323, MAE 242,210.51, RMSE 263,898.13,
WAPE 3.684100%, n=15. Full results: PHASE4_MODEL_COMPARISON.md.

## Uncertainty and operational behavior

Development residual empirical intervals require 20 observations per series/horizon;
only 6/5/4 exist, so bounds and coverage are unavailable. No coverage guarantee. Nonnegative forecasts
retain raw values. Frozen models refit through December 2025 to predict January–March 2026; these
are retrospective as-of forecasts, not current predictions. No 2026 actuals are incorporated.

## Limitations and inappropriate uses

Short overlapping evaluation, retrospective nonblind context, only one chemical/geography,
unknown absent-cell mechanisms, failure exclusions, no patient or population denominators, no
intervention/clinical evidence. No guaranteed accuracy, clinical dosing, price/revenue forecast,
India-market transfer or demonstrated business gain. Continuous point expectations are not observed counts.
Screened presentation sums are not national forecasts. Direct and regional-sum forecasts are not
forced coherent; gaps are disclosed. Additional future evaluation is needed before production adoption.

## Reproduce

```powershell
.\.venv\Scripts\python.exe run_pipeline.py --phase 4
.\.venv\Scripts\python.exe -m src.phase4_pipeline --audit
```

Saved selected_model_parameters.json contains refit parameters and provenance; deterministic fitting
with the pinned environment recreates models. No executable pickle is required. Source hashes, model
decisions, dates, predicted rows and failure reasons are available for independent review.
