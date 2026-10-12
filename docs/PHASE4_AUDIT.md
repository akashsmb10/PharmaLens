# Phase 4 final audit

Overall pass: **True**. This is executed retrospective prescribing-activity forecasting,
not manufacturer revenue, clinical advice, patient demand or India-market forecasting.

## Repository baseline and prerequisites

Existing Phase 1–3 suite: **74 tests passed**; baseline_tests.xml records the rerun with authorized
project-local temporary storage after four Windows PermissionError setup errors in the initial run.
Required raw/data/SQL/docs/notebooks and reporting artifacts exist. No packages were installed.
settings.yaml is absent; existing configs were retained. The database remains
data/processed/pharma.duckdb, main/phase2; DATEs and exact twenty-view exports are verified read-only.
Relevant actual totals: 212,022,236 items and
GBP 336,940,603.13 NIC. Fact rows 3920;
364 absent diagnostic cells remain null. Prior full-history inventory and retrospective anomaly flags
are inspected but never used as future-aware training treatments.

## Architecture and implementation inventory

Central configuration → validated series → origin folds → development fits → pooled-level model
selection and frozen choices/calibration → holdout refits → comparison/independent validation →
as-of-December operational refits → exports/charts/notebooks. Earlier pipeline modes remain supported.
The Phase 3 document guard excludes new Phase 4 reports while retaining its original prior-file
hashes; no prior analytical calculations or protected artifacts are changed.

- `README.md`
- `config/forecasting.yaml`
- `config/kernels/pharma-phase4/kernel.json`
- `docs/PHASE4_AUDIT.md`
- `docs/PHASE4_BUSINESS_INSIGHTS.md`
- `docs/PHASE4_FORECASTING_METHODOLOGY.md`
- `docs/PHASE4_MODEL_CARD.md`
- `docs/PHASE4_MODEL_COMPARISON.md`
- `notebooks/04_forecasting_experiments.ipynb`
- `notebooks/05_forecast_evaluation.ipynb`
- `run_pipeline.py`
- `src/forecast_backtesting.py`
- `src/forecast_config.py`
- `src/forecast_data.py`
- `src/forecast_features.py`
- `src/forecast_intervals.py`
- `src/forecast_metrics.py`
- `src/forecast_models.py`
- `src/forecast_reconciliation.py`
- `src/forecast_selection.py`
- `src/forecast_splits.py`
- `src/phase3_pipeline.py`
- `src/phase4_notebooks.py`
- `src/phase4_pipeline.py`
- `src/phase4_reports.py`
- `src/phase4_visualizations.py`
- `tests/conftest.py`
- `tests/test_phase4_backtesting.py`
- `tests/test_phase4_features.py`
- `tests/test_phase4_intervals.py`
- `tests/test_phase4_metrics.py`
- `tests/test_phase4_models.py`
- `tests/test_phase4_reconciliation.py`
- `tests/test_phase4_reproducibility.py`
- `tests/test_phase4_splits.py`

## Eligibility and evaluation support

Evaluated series: **36**, by level **{'national': 1, 'region_presentation': 28, 'regional': 7}**.
Training-only initial-window eligibility is frozen without holdout membership leakage. Series eligibility
and exclusions include all candidate pairs and Phase 2 inventory reconciliation. Development origins
Dec 2024–May 2025 with targets Jan–Jun 2025; holdout origins Jun–Nov 2025 with targets Jul–Dec 2025.
Each stage has 15 origin/horizon cells per series: 6/5/4. Development forecasts:
**4320**, including eight configurations (four Ridge alpha trials).
Holdout forecasts: **2700**, five frozen family configurations per level.
Selected holdout forecasts: **540**. Failed attempts are included in
these counts; successful common-support n is reported separately.

## Model configurations and selection

| aggregation_level | model | variant | alpha |
|---|---|---|---|
| national | damped_ets | damped_ets | Undefined |
| national | drift | drift | Undefined |
| national | naive | naive | Undefined |
| national | ridge | ridge_alpha_10 | 10.000000 |
| national | seasonal_naive | seasonal_naive | Undefined |
| region_presentation | damped_ets | damped_ets | Undefined |
| region_presentation | drift | drift | Undefined |
| region_presentation | naive | naive | Undefined |
| region_presentation | ridge | ridge_alpha_10 | 10.000000 |
| region_presentation | seasonal_naive | seasonal_naive | Undefined |
| regional | damped_ets | damped_ets | Undefined |
| regional | drift | drift | Undefined |
| regional | naive | naive | Undefined |
| regional | ridge | ridge_alpha_10 | 10.000000 |
| regional | seasonal_naive | seasonal_naive | Undefined |

| aggregation_level | selected_model | selected_variant | selection_metric | development_score | runner_up | eligible_models | selection_sample_size | series_sample_size | selection_scope | tie_threshold_relative | tie_breaking_reason | frozen_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| national | damped_ets | damped_ets | MASE | 0.652526 | ridge_alpha_10 | damped_ets;drift;naive;ridge_alpha_0.1;ridge_alpha_1;ridge_alpha_10;ridge_alpha_100;seasonal_naive | 15 | 15 | Shared by aggregation level; pooled mean scaled absolute error | 0.020000 | Simplicity preference within relative MASE tolerance; deterministic alpha tie break | 2025-06-01 00:00:00 |
| region_presentation | ridge | ridge_alpha_10 | MASE | 0.897394 | ridge_alpha_1 | drift;naive;ridge_alpha_0.1;ridge_alpha_1;ridge_alpha_10;ridge_alpha_100;seasonal_naive | 420 | 15 | Shared by aggregation level; pooled mean scaled absolute error | 0.020000 | Simplicity preference within relative MASE tolerance; deterministic alpha tie break | 2025-06-01 00:00:00 |
| regional | damped_ets | damped_ets | MASE | 0.650488 | ridge_alpha_10 | damped_ets;drift;naive;ridge_alpha_0.1;ridge_alpha_1;ridge_alpha_10;ridge_alpha_100;seasonal_naive | 105 | 15 | Shared by aggregation level; pooled mean scaled absolute error | 0.020000 | Simplicity preference within relative MASE tolerance; deterministic alpha tie break | 2025-06-01 00:00:00 |

Selected choices/config hash are persisted before the first holdout fit. Their SHA-256 remains
a874f30f9e21dd32fd74ef75eafeacc2ed848c5cca72478c36b168dc1fcb2561 afterward. Model parameters, warnings, optimizer status,
cutoffs, data/config/model versions and package versions are saved. There are **6**
failed main forecast rows; no fallback is relabeled as the failed family.

## Final holdout comparison and horizon results

| aggregation_level | model | variant | n | MAE | RMSE | WAPE | sMAPE | MASE | Bias | mase_defined_rows |
|---|---|---|---|---|---|---|---|---|---|---|
| national | damped_ets | damped_ets | 15 | 242,210.509664 | 263,898.125872 | 3.684100 | 3.694201 | 0.888323 | -66,774.101742 | 15 |
| national | drift | drift | 15 | 304,846.146525 | 353,818.767287 | 4.636808 | 4.651418 | 1.118348 | -14,172.723371 | 15 |
| national | naive | naive | 15 | 302,008.666667 | 360,899.119551 | 4.593649 | 4.621575 | 1.107000 | -98,475.733333 | 15 |
| national | ridge | ridge_alpha_10 | 15 | 237,672.337558 | 265,741.190491 | 3.615072 | 3.623867 | 0.871695 | -95,573.745229 | 15 |
| national | seasonal_naive | seasonal_naive | 15 | 445,901.666667 | 486,838.833631 | 6.782307 | 6.968013 | 1.640422 | -445,901.666667 | 15 |
| region_presentation | damped_ets | damped_ets | 417 | 8,799.546039 | 12,119.015662 | 3.746997 | 3.773084 | 0.885641 | -2,754.687413 | 417 |
| region_presentation | drift | drift | 417 | 10,914.442648 | 16,226.851476 | 4.647557 | 4.617762 | 1.075119 | -528.511383 | 417 |
| region_presentation | naive | naive | 417 | 11,042.609113 | 16,527.207460 | 4.702132 | 4.709791 | 1.097024 | -3,522.829736 | 417 |
| region_presentation | ridge | ridge_alpha_10 | 417 | 8,705.099318 | 12,018.693522 | 3.706780 | 3.828928 | 0.893876 | -2,693.838607 | 417 |
| region_presentation | seasonal_naive | seasonal_naive | 417 | 17,452.093525 | 24,933.343004 | 7.431400 | 7.303474 | 1.700044 | -15,784.050360 | 417 |
| regional | damped_ets | damped_ets | 105 | 35,399.647805 | 40,625.700926 | 3.769080 | 3.766715 | 0.914208 | -12,045.747643 | 105 |
| regional | drift | drift | 105 | 43,651.034143 | 53,928.667758 | 4.647624 | 4.609686 | 1.117376 | -2,024.674767 | 105 |
| regional | naive | naive | 105 | 43,689.180952 | 54,868.869716 | 4.651685 | 4.638976 | 1.120797 | -14,067.961905 | 105 |
| regional | ridge | ridge_alpha_10 | 105 | 34,211.975906 | 40,166.077492 | 3.642626 | 3.643738 | 0.885645 | -13,593.125966 | 105 |
| regional | seasonal_naive | seasonal_naive | 105 | 63,700.238095 | 77,230.137138 | 6.782307 | 6.660722 | 1.584009 | -63,700.238095 | 105 |

| split_type | aggregation_level | horizon | n | MAE | RMSE | WAPE | sMAPE | MASE | Bias | mase_defined_rows |
|---|---|---|---|---|---|---|---|---|---|---|
| holdout | national | 1 | 6 | 274,536.059637 | 293,105.666325 | 4.175892 | 4.194346 | 1.007852 | -78,754.087158 | 6 |
| holdout | national | 2 | 5 | 207,187.641873 | 233,248.519833 | 3.167205 | 3.163615 | 0.758500 | -26,982.634102 | 5 |
| holdout | national | 3 | 4 | 237,500.769444 | 253,546.525695 | 3.589913 | 3.607215 | 0.871309 | -98,543.458169 | 4 |
| holdout | region_presentation | 1 | 168 | 9,630.040842 | 13,148.177791 | 4.116841 | 4.147316 | 0.970975 | -2,883.058733 | 168 |
| holdout | region_presentation | 2 | 140 | 8,044.591401 | 11,324.674374 | 3.456280 | 3.637964 | 0.841549 | -1,592.807425 | 140 |
| holdout | region_presentation | 3 | 112 | 7,981.779315 | 10,884.743280 | 3.390919 | 3.555415 | 0.838056 | -3,702.450571 | 112 |
| holdout | regional | 1 | 42 | 38,738.613144 | 43,930.880480 | 4.124696 | 4.121547 | 0.998690 | -13,526.452435 | 42 |
| holdout | regional | 2 | 35 | 31,230.801503 | 36,648.805283 | 3.341900 | 3.327422 | 0.805800 | -6,604.612120 | 35 |
| holdout | regional | 3 | 28 | 35,602.257675 | 40,191.744908 | 3.766991 | 3.783583 | 0.922997 | -16,626.109859 | 28 |

Regional and per-series comparisons, bias, alpha development scores and robustness are separate
exports. National ETS is the development choice; a lower holdout Ridge score is disclosed without
changing selection. Presentation-level ETS failures prevent its shared-level selection even where
successful-row scores are lower. No iid significance or artificial confidence interval for metrics is claimed.

## Interval and hierarchy diagnostics

| aggregation_level | horizon | nominal_level | forecast_rows | interval_rows | empirical_coverage_pct | mean_width | status |
|---|---|---|---|---|---|---|---|
| national | 1 | 80 | 6 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| national | 1 | 95 | 6 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| national | 2 | 80 | 5 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| national | 2 | 95 | 5 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| national | 3 | 80 | 4 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| national | 3 | 95 | 4 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| region_presentation | 1 | 80 | 168 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| region_presentation | 1 | 95 | 168 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| region_presentation | 2 | 80 | 140 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| region_presentation | 2 | 95 | 140 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| region_presentation | 3 | 80 | 112 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| region_presentation | 3 | 95 | 112 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| regional | 1 | 80 | 42 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| regional | 1 | 95 | 42 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| regional | 2 | 80 | 35 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| regional | 2 | 95 | 35 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| regional | 3 | 80 | 28 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |
| regional | 3 | 95 | 28 | 0 | Undefined | Undefined | unavailable: insufficient development calibration |

Calibration is development-only with minimum 20 residuals per series/horizon;
short samples give null bounds/coverage, not fabricated uncertainty. All
**288** historical hierarchy checks pass. Direct national and
all-seven-region sums are evaluated separately; no screened-presentation sum becomes a national total.

| split_type | horizon | n | MAE | RMSE | WAPE | sMAPE | MASE | Bias | mase_defined_rows | approach |
|---|---|---|---|---|---|---|---|---|---|---|
| development | 1 | 6 | 177,130.113211 | 248,013.612787 | 2.840518 | 2.862044 | 0.692050 | 50,370.985455 | 6 | direct_national |
| development | 2 | 5 | 188,441.705923 | 261,458.244771 | 3.038994 | 3.055202 | 0.729139 | 103,127.783564 | 5 | direct_national |
| development | 3 | 4 | 128,960.658672 | 141,433.858387 | 2.045053 | 2.036059 | 0.497473 | 29,692.315357 | 4 | direct_national |
| holdout | 1 | 6 | 274,536.059637 | 293,105.666325 | 4.175892 | 4.194346 | 1.007852 | -78,754.087158 | 6 | direct_national |
| holdout | 2 | 5 | 207,187.641873 | 233,248.519833 | 3.167205 | 3.163615 | 0.758500 | -26,982.634102 | 5 | direct_national |
| holdout | 3 | 4 | 237,500.769444 | 253,546.525695 | 3.589913 | 3.607215 | 0.871309 | -98,543.458169 | 4 | direct_national |
| development | 1 | 6 | 175,239.393851 | 242,812.473450 | 2.810197 | 2.832724 | 0.684555 | 41,100.260255 | 6 | sum_all_seven_regions |
| development | 2 | 5 | 179,515.218298 | 250,612.040439 | 2.895037 | 2.914093 | 0.693894 | 92,657.089084 | 5 | sum_all_seven_regions |
| development | 3 | 4 | 117,996.908406 | 131,880.700548 | 1.871190 | 1.863795 | 0.453893 | 16,334.372657 | 4 | sum_all_seven_regions |
| holdout | 1 | 6 | 271,170.292007 | 289,263.985406 | 4.124696 | 4.143279 | 0.995085 | -94,685.167046 | 6 | sum_all_seven_regions |
| holdout | 2 | 5 | 218,615.610522 | 241,022.241784 | 3.341900 | 3.337873 | 0.800588 | -46,232.284842 | 5 | sum_all_seven_regions |
| holdout | 3 | 4 | 249,215.803725 | 264,623.915950 | 3.766991 | 3.786290 | 0.914915 | -116,382.769014 | 4 | sum_all_seven_regions |

## Retrospective operational forecasts

| forecast_month | horizon | model | point_forecast | interval_status |
|---|---|---|---|---|
| 2026-01-01 00:00:00 | 1 | damped_ets | 6,650,151.108177 | unavailable: insufficient development residuals |
| 2026-02-01 00:00:00 | 2 | damped_ets | 6,681,492.745562 | unavailable: insufficient development residuals |
| 2026-03-01 00:00:00 | 3 | damped_ets | 6,712,207.550199 | unavailable: insufficient development residuals |

All selected series have three as-of-Dec-2025 future rows. Operational regional-sum comparison is
separate. No external Jan–Mar 2026 actuals are fabricated or evaluated.

## Export inventory

| output (CSV and Parquet) | rows | columns |
|---|---|---|
| series_eligibility | 127 | 16 |
| development_folds | 15 | 6 |
| holdout_folds | 15 | 6 |
| backtest_predictions | 7020 | 28 |
| development_model_metrics | 15 | 11 |
| development_configuration_metrics | 24 | 11 |
| holdout_model_metrics | 15 | 11 |
| horizon_metrics | 90 | 13 |
| regional_forecast_metrics | 70 | 13 |
| series_forecast_metrics | 360 | 13 |
| forecast_bias_summary | 30 | 11 |
| model_selection_decisions | 36 | 14 |
| frozen_family_configurations | 15 | 4 |
| interval_calibration | 108 | 7 |
| forecast_intervals | 540 | 37 |
| interval_coverage_summary | 18 | 8 |
| forecast_hierarchy_checks | 288 | 7 |
| aggregate_forecast_comparison | 30 | 13 |
| aggregate_forecast_metrics | 12 | 11 |
| operational_forecasts | 108 | 22 |
| operational_aggregate_comparison | 3 | 8 |
| ets_fitted_states | 288 | 6 |
| ridge_coefficients | 522 | 4 |
| selected_forecast_metrics | 18 | 11 |
| model_failures | 6 | 28 |
| forecast_robustness_results | 159 | 20 |

Each output is under outputs/phase4/tables. Independent forecast_validation.csv is under validation.
Selected refit parameter metadata is under outputs/phase4/models. Dataset/config/choices hashes,
environment and sample provenance are in run_metadata.json and frozen_development_decisions.json.

## Chart inventory

- `outputs/phase4/charts/01_national_history_origins.png`
- `outputs/phase4/charts/02_holdout_actual_prediction.png`
- `outputs/phase4/charts/03_national_models.png`
- `outputs/phase4/charts/04_mae_by_model.png`
- `outputs/phase4/charts/05_mase_by_model.png`
- `outputs/phase4/charts/06_accuracy_horizon.png`
- `outputs/phase4/charts/07_regional_models.png`
- `outputs/phase4/charts/08_regional_error_heatmap.png`
- `outputs/phase4/charts/09_bias_by_model.png`
- `outputs/phase4/charts/10_residual_distribution.png`
- `outputs/phase4/charts/11_error_horizon.png`
- `outputs/phase4/charts/12_development_holdout.png`
- `outputs/phase4/charts/13_ets_fitted_trend.png`
- `outputs/phase4/charts/14_ridge_coefficients.png`
- `outputs/phase4/charts/15_interval_support.png`
- `outputs/phase4/charts/16_direct_regional_sum.png`
- `outputs/phase4/charts/17_selected_models.png`
- `outputs/phase4/charts/18_operational_forecasts.png`

Charts explicitly distinguish single-origin paths, rolling h=1 predictions from different origins,
development/holdout and retrospective operational dates. No different-origin forecast path is spliced silently.

## Notebook execution

| notebook | code_cells | unexecuted_code_cells | error_outputs |
|---|---|---|---|
| notebooks/04_forecasting_experiments.ipynb | 6 | 0 | 0 |
| notebooks/05_forecast_evaluation.ipynb | 6 | 0 | 0 |

## Tests, independent validation and reproducibility

Full suite: **124 tests**, **0 failures**,
**0 errors**, **0 skipped**. Tests include analytical
fixtures, target dates, direct supervised label bounds, scaler isolation, adversarial future-value changes,
holdout-isolated selection, failure logging, undefined ratios, common support, hierarchy, intervals,
metadata and operational dates. Audit rerun evidence is asserted against actual hashes by pytest.

Independent Python/math checks: **36127 passed**,
**0 failed**. These independently recompute baselines, dates,
actuals, MASE scales, row counts, metrics and pooled development selections. Historical hierarchy is
independently summed. Numerical business claims derive from these checked prediction-based tables.

All 26 CSV/Parquet pairs byte-identical across two full pipeline executions:
**True**. Frozen selection/calibration hashes also match. Notebook runtime
metadata is not claimed byte-identical. Protected previous artifacts: **257**,
unchanged: **True**. Test-only restoration of the Phase 3 summary
prevents its integration-test side effect; no prior calculation or source observation is modified.

## Limits and Phase 5

Short overlapping samples, retrospective nonblind context, one chemical/geography, unknown gaps,
failed models and unsupported intervals limit confidence. Holdout rankings are not operational retuning.
Build a dashboard that exposes origin, horizon, selected model, baseline/error sample, failure status,
coherence and missing interval support. Seek longer and genuinely future evaluation before live use.
No critical validation remains unresolved when overall pass above is True.

## Reproduce

```powershell
.\.venv\Scripts\python.exe run_pipeline.py --phase 4
.\.venv\Scripts\python.exe -m src.phase4_pipeline --audit
```
