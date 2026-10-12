# Phase 4 business insights

## Executive summary and objective

Forecast recorded monthly NHS atorvastatin item activity one to three months ahead. **36**
series are evaluated: one national, seven regional and training-eligible region/presentation series.
The development-selected national model is **damped_ets**, with final holdout
**MASE 0.888323**, **MAE 242,210.51 items**, **RMSE 263,898.13 items**,
and **WAPE 3.684100%**, over **15** overlapping forecasts.
Relative MASE improvement against naive is **19.753991%** on identical support.
This is a measured retrospective forecast comparison, not an observed business revenue benefit.

## Models and validation design

Naive, seasonal naive (period 12), drift, nonseasonal damped additive ETS, and direct Ridge with
training-only StandardScaler. Ridge alpha candidates 0.1/1/10/100 are evaluated in development;
family choices and hyperparameters are frozen before holdout. Development: Jan 2023–Jun 2025,
initial training Jan 2023–Dec 2024. Final targets: Jul–Dec 2025, origins Jun–Nov 2025.
There are 6/5/4 forecasts per horizon, not six at every horizon. Shared model selection by level
reduces per-series tuning on very short histories. Earlier descriptive data were visible, so this
is retrospective chronological evaluation rather than a blinded external study.

## Eight evidence-based findings

1. **Selected national model beats naive in this window.** damped_ets, horizons 1–3,
Jul–Dec 2025: MASE **0.888323** versus naive **1.107000**, an improvement
of **19.753991%**, n=15 paired forecast cells. It could support activity planning,
subject to ongoing monitoring; six target months and overlapping errors limit generalization.
Evidence: holdout_model_metrics.csv; charts 04–06.

2. **Holdout winner differs from frozen national selection.** Lowest observed national MASE is
**ridge (0.871695)**, n=15, versus selected
**damped_ets (0.888323)**. This comparison is reported honestly and does
not change the operational family. Development choices are not retuned on holdout rankings.
Evidence: model_selection_decisions.csv and holdout_model_metrics.csv; charts 03 and 12.

3. **Horizon accuracy is uneven.** The selected national model's horizon-specific errors are below.
Each h=3 forecast genuinely originates three months earlier. Different target-month support and
small n mean these results cannot establish monotonic reliability or independent error distributions.
Evidence: horizon_metrics.csv; charts 06 and 11.

4. **Regional variation remains.** Selected regional MASE spans **0.866515–1.027080**,
Jul–Dec 2025, n=15 cells per region. Compare against each region's naive rows
before adopting a uniform service target. Regions are unadjusted fixed aggregates and share shocks.
Evidence: regional_forecast_metrics.csv; charts 07–08.

5. **Presentation-level reliability includes failure risk.** The selected model distribution below
uses shared development decisions. **6** attempted ETS forecast rows failed
optimization, with dates and warnings retained. Selection excludes configs with development failures,
rather than silently replacing their predictions. Eligible products are not the full prescribing population.
Evidence: model_failures.csv and model_selection_decisions.csv; chart 17.

6. **Uncertainty intervals are unsupported.** National development calibration counts are only
6/5/4, below the frozen minimum 20; 80%/95% bounds and empirical
coverage are null. Point forecasts should be shown with this limitation, not narrow bands suggesting
calibrated confidence. Evidence: interval_calibration.csv and interval_coverage_summary.csv; chart 15.

7. **Hierarchy requires explicit checks.** All **288** historical
national/regional/presentation consistency checks pass. The mean absolute final holdout difference
between direct national and regional-sum forecasts is **17,546.13 items**,
n=15 origin/horizon cells. They remain separately evaluated, without post-hoc rescaling.
Evidence: forecast_hierarchy_checks.csv and aggregate_forecast_comparison.csv; chart 16.

8. **Operational outputs are historical as-of forecasts.** Refit frozen choices through December
2025 to issue January–March 2026 expectations below. They are not live current-market forecasts
and are not compared with separately uncollected 2026 actuals. Source data stay intact; development
sensitivities cover trailing windows, training-only anomaly treatment, constraints and tie policies.
Evidence: operational_forecasts.csv and forecast_robustness_results.csv; chart 18.

## Selected national horizon performance

| split_type | aggregation_level | horizon | n | MAE | RMSE | WAPE | sMAPE | MASE | Bias | mase_defined_rows |
|---|---|---|---|---|---|---|---|---|---|---|
| holdout | national | 1 | 6 | 274,536.059637 | 293,105.666325 | 4.175892 | 4.194346 | 1.007852 | -78,754.087158 | 6 |
| holdout | national | 2 | 5 | 207,187.641873 | 233,248.519833 | 3.167205 | 3.163615 | 0.758500 | -26,982.634102 | 5 |
| holdout | national | 3 | 4 | 237,500.769444 | 253,546.525695 | 3.589913 | 3.607215 | 0.871309 | -98,543.458169 | 4 |

## Selected model distribution

| aggregation_level | selected_model | selected_variant | series |
|---|---|---|---|
| national | damped_ets | damped_ets | 1 |
| region_presentation | ridge | ridge_alpha_10 | 28 |
| regional | damped_ets | damped_ets | 7 |

## Regional selected-model errors

| region_name | model | n | MASE | MAE | RMSE | WAPE | Bias |
|---|---|---|---|---|---|---|---|
| LONDON | damped_ets | 15 | 0.902890 | 31,471.902746 | 35,627.339785 | 3.687662 | -21,713.342601 |
| SOUTH WEST | damped_ets | 15 | 0.916923 | 21,800.882933 | 23,984.267833 | 3.643091 | -6,316.624845 |
| SOUTH EAST | damped_ets | 15 | 1.027080 | 30,132.669040 | 33,208.513704 | 3.863861 | -10,646.514166 |
| MIDLANDS | damped_ets | 15 | 0.889676 | 49,344.811800 | 53,421.475968 | 3.866114 | -13,145.282519 |
| EAST OF ENGLAND | damped_ets | 15 | 0.866515 | 25,807.123375 | 28,140.649736 | 3.423911 | -8,727.364699 |
| NORTH WEST | damped_ets | 15 | 0.928264 | 34,610.538881 | 37,631.853685 | 4.072453 | -8,786.275103 |
| NORTH EAST AND YORKSHIRE | damped_ets | 15 | 0.868110 | 54,629.605862 | 59,530.400052 | 3.734525 | -14,984.829570 |

## Eligibility reconciliation with Phase 2

Full-history inventory reports 29 region/presentation
candidates, but the initial training-only screen excludes:

| series_id | presentation_name | initial_training_items | reason |
|---|---|---|---|
| Y60::0212000B0BBABAB\|tablet | Lipitor 20mg tablets | 28,393.000000 | Training-only item volume below threshold |

The exclusion prevents future volume from influencing series membership; no missing record is fabricated.

## Retrospective national operational forecasts

| forecast_month | horizon | model | point_forecast | interval_status |
|---|---|---|---|---|
| 2026-01-01 00:00:00 | 1 | damped_ets | 6,650,151.108177 | unavailable: insufficient development residuals |
| 2026-02-01 00:00:00 | 2 | damped_ets | 6,681,492.745562 | unavailable: insufficient development residuals |
| 2026-03-01 00:00:00 | 3 | damped_ets | 6,712,207.550199 | unavailable: insufficient development residuals |

## Recommendations and limits

For Phase 5, build a dashboard that distinguishes observed history, origin-specific holdout predictions
and retrospective operational forecasts. Show model, horizon, cutoff, error metrics, sample support,
failure status and unavailable uncertainty prominently. Monitor drift and missingness before live use.
Evaluate more chronological origins and additional genuinely future observations before claiming stable
accuracy or calibrated intervals. Do not select a regional-sum approach merely because it wins this
holdout; assess it in a fresh period. Keep naive as the ongoing benchmark.

Only 36 months, short overlapping holdout, nonblind historical context, selected high-activity series,
unknown gaps and correlated geography. No clinical recommendation, patient-demand claim,
manufacturer revenue estimate, measured profit impact or direct India-market extrapolation is supported.
