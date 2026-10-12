# Forecasting readiness (assessment only)

Primary target: monthly **prescription-item count**. Secondary target: monthly **net ingredient cost**.
No company revenue target exists and no forecasting model is trained in Phase 2.

National activity has 36 observed calendar months (January 2023–December 2025), with no aggregate
monthly gaps. Each of seven regional aggregates also has 36 observed months. All 17 national
presentation/unit aggregates have 36 observed months, but rare products have very low/intermittent
regional activity; 10 national presentations
meet the default total-item activity screen.

## Descriptive eligibility and prioritization

Default regional/presentation eligibility requires at least **24 observed months**,
**100% full-window coverage**, **0 internal missing months**
and **36,000 total items**. This yields **29 candidates** out of
119 possible pairs; 94 pairs are complete before the volume screen.
At 36 months, 36,000 items means at least 1,000 per month on average; it reduces unstable growth on
tiny denominators, not a claim about clinical importance. Coverage 100% makes observed missingness
irrelevant for primary candidates. The nominal 24-month threshold is a minimum-history guard; with
this strict full-window rule it effectively requires all 36 months in the present dataset.

Rank eligible activity by total items and recent growth separately. Report monthly CV, regional mix,
national cost contribution and coverage alongside the ranks; no arbitrary composite score or untapped
market-potential estimate is created. These full-history screens are descriptive; recompute selection
using the training window only for honest forecast evaluation.

Sensitivity uses history thresholds 24/36, total items 3,600/36,000/360,000 and coverage 90/100%,
always requiring zero internal gaps. Results:

| minimum_history_months | minimum_total_items | minimum_coverage_pct | eligible_series_count |
|---|---|---|---|
| 24 | 3600 | 90 | 79 |
| 24 | 3600 | 100 | 79 |
| 24 | 36000 | 90 | 29 |
| 24 | 36000 | 100 | 29 |
| 24 | 360000 | 90 | 28 |
| 24 | 360000 | 100 | 28 |
| 36 | 3600 | 90 | 79 |
| 36 | 3600 | 100 | 79 |
| 36 | 36000 | 90 | 29 |
| 36 | 36000 | 100 | 29 |
| 36 | 360000 | 90 | 28 |
| 36 | 360000 | 100 | 28 |

History/coverage alternatives do not change counts in this extract under the internal-gap rule; volume
thresholds change the selected set. Eligibility does not establish forecast accuracy. See
forecast_candidate_series.csv and threshold_sensitivity.csv for exact selections and exclusions.

## Suggested modeling order and practical horizons

1. National aggregate: strongest observed activity, complete history. Start with naive and seasonal-naive
   baselines, then simple interpretable models assessed on rolling chronological holdouts.
2. Seven regional aggregates: complete history with geographic caveats; evaluate separately and check
   reconciliation with national forecasts in a later phase.
3. Dominant national presentations and sufficiently covered regional/presentation series: retain unit
   distinction and inspect cost/item shifts and extreme flags. Rare liquid/brand series need intermittent
   count treatment or carefully justified aggregation, not default zero imputation of absent months.

Initial evaluation horizons of 1–3 months are pragmatic given 36 observations; 6–12 month horizons have
few independent historical origins and wider uncertainty. Three annual cycles weakly constrain seasonality
and leave little room for complex model tuning. Monthly plots show variation, but no formal seasonal
claim is made. Test calendar length and working-day effects before calling variation seasonal.

## Structural changes and leakage risks

NIC fell while items grew; ingredient-cost forecasts may be less stable than item forecasts. Dated tariff
references, quantity/item ratios and presentation shares should be investigated before modeling breaks.
Geographic classifications and product attribution can change even when labels remain stable.
Confirmed reporting gaps versus nonactivity cannot be distinguished from the extract. Internal missing
series are not automatically zero-valued or discontinued. Extreme flags remain observed values.

Do not use contemporaneous future cost/quantity to predict unknown future item counts. Fit transforms,
selection thresholds, imputation policies and hyperparameters within training folds only; IQR flags and
full-window coverage computed here use all history and must not be carried into a backtest as if known
at its origin. Preserve December 2025 or another defined chronological holdout and avoid random splits.
No population-adjusted, patient-level, causal or India-market forecasting interpretation is supported.

<!-- PHASE3 DIAGNOSTICS -->

## Phase 3 executed diagnostics

National item OLS slope **46,650.04/month**, HAC 95% interval
**[41,844.58, 51,455.49]**; detrended residual CV **0.034103**.
Exploratory item seasonal strength **0.802226**, detrended lag-12 ACF
**0.220321**, year-profile correlation **0.668679**.
Three cycles and calendar length restrict seasonal confidence. NIC trends have substantial residual
dependence and uncertain smooth slopes; the annual cost decline is observed, but extrapolation is unsafe.

Forecast diagnostics contain **94 series-target records**: national,
seven regions, ten volume-screened national presentations, and 29 Phase 2 eligible region/presentation
series, each for items and NIC. Zero fractions describe only observed months; missing cells stay unknown.
The >=20% annual mean shift flag is a transparent review heuristic, not a break test.

Phase 4 shortlist: naive, seasonal naive (benchmark only), drift, damped ETS, regularized lag regression.
Use initial 1–3 month horizons, chronological rolling origins, forecast-error comparisons and reconciliation
across aggregation levels. Cost shifts may require separate scenarios and origin-specific refitting;
avoid asserting a permanent new regime from this extract. Recompute candidate screens and anomaly
thresholds within each training fold. Preserve an honest holdout. No forecast model/backtest trained.
Detailed output: outputs/phase3/tables/forecasting_diagnostics.csv. See PHASE3_METHODOLOGY.md.
