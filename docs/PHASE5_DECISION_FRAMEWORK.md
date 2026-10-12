# Phase 5 decision framework

## Objective and scope

Allocate analytical monitoring and investigation effort using verified NHSBSA atorvastatin activity
in England. The evidence concerns prescription items and NIC, not patients, manufacturer revenue,
healthcare quality or India demand. NIC is an accounting measure, not final NHS expenditure.
No interactive dashboard or PBIX is created; Phase 6 consumes the stable exported datasets.

## Features, joins and missingness

Historical source: Phase 2 cost_analytics (observed region/presentation/month), annual and monthly
reporting views, the absence-only missing_series_months export and series_coverage. Union observed
and absent cells to reconstruct the existing diagnostic grid, without manufacturing activity.
At region/presentation, region, presentation and national grains, sum observed prescription items
and GBP NIC. NIC/item is sum NIC divided by sum items, never mean of row ratios. Historical shares
use the full observed national total. Recent annual change compares 2025 with 2024, requiring twelve
observed aggregate months in both years and a positive baseline; otherwise change is null.
Aggregate completeness does not imply constituent-cell completeness; both exposures are exported.
Absence can reflect unknown applicability; a never-observed cell is not known zero activity.
Monthly variability is sample SD/mean, includes trend, and is not forecast error. Concentration HHI
sums squared presentation item shares for regions/national and squared regional shares for presentations.
Contribution percentages divide component change by national net change; negative/>100% values are valid.
All 17 presentation identifiers include native unit; physical quantities are not combined.

Original Phase 2 extreme flags and unique flagged cells remain descriptive review exposure. Phase 3
union flags and classifications are separate, retrospective heuristics, not confirmed errors. A flag count
can count several metrics for the same cell. Nothing is deleted or treated as proven structural causation.
All joins validate right-side uniqueness and preserve left row counts. Frozen Phase 4 selections identify
selected-model rows, aggregated explicitly by series/split/horizon. Pooled Phase 4 family metrics are
not silently substituted for individual selected-series metrics. Missing forecasts stay null.
Presentation forecast features are equal-series means over the eligible regional subset, not national
presentation forecasts; their subset scope is explicit. Future presentation totals are not fabricated.

Field-level definitions, sources, units, null behavior and business keys are exported in
decision_feature_dictionary and dashboard_data_dictionary. Dates are typed in Parquet and ISO in CSV.
Percent metrics use 0–100; share fractions/HHI use 0–1. Ratios and item expectations retain precision.

## Monitoring policy

Five dimensions: activity = recent annual items; historical change = absolute annual item growth;
cost-pattern change = absolute annual weighted NIC/item change; forecast risk = selected-series
holdout MASE (presentation uses the disclosed eligible-subset mean); quality concern = missing-cell
percentage plus original extreme flags per 1,000 observed cells. Combining those two quality indicators
is an illustrative policy choice with no empirical calibration. Greater values mean more review relevance.
Higher data-quality concern does not mean commercial opportunity. Each raw feature remains exported.

Normalize each dimension separately within its aggregation-level cohort: 100*(average rank−1)/(n−1)
over finite values, where n is the finite count; tied values use midranks. A constant or singleton
dimension scores 50, a neutral ranking convention rather than measured risk. Missing values remain null.
Initial weights: activity 25%, change 20%, cost 20%, forecast 20%, quality 15%; validate nonnegative
finite weights summing to one. Composite = weighted sum of component scores. Every positive-weight
component must exist; otherwise status is Insufficient evidence and composite/rank are null. Missing
components are not zero risk and remaining weights are not silently redistributed.

Rank descending with equal scores sharing minimum rank; entity IDs deterministically order display
ties. Initial tiers: >=70 High review priority, >=40 Moderate review priority, otherwise Routine monitoring.
Actions: investigate drivers/risk, review next cycle, standard tracking, or improve evidence before scoring.
These labels are policy-dependent; a top-ranked entity need not meet the high-review threshold.

## Sensitivity and forecast reliability

Compare equal weighting; activity/forecast/quality-heavy weights (50% primary, 12.5% others); each
leave-one-component-out policy with remaining original weights rescaled; min-max normalization
(100*(x−min)/(max−min), constant=50); tiers 60/30, 70/40 and 80/50. Export individual rank changes,
newly scored entities, tier changes, paired Spearman correlations and top-three overlap restricted to
the baseline-scored universe (ties can admit more than three). Unscored baseline entities have no
invented rank movement. Flag maximum rank change >= max(1,25% of baseline scored cohort size).
This is a sensitivity diagnostic, not a robustness guarantee or probabilistic confidence interval.

Forecast risk consumes frozen Phase 4 outputs only, with no fitting/reselection. MAE/RMSE describe
absolute errors, MASE scales by origin-training naive change, WAPE is aggregate absolute error/actual
volume, bias=forecast−actual, and bias_pct=mean error/mean actual. Compare naive on identical successful
origin/horizon cells. Error classes are relative within aggregation level: normalized MASE percentile
<=1/3 Lower, <=2/3 Moderate, otherwise Higher; fewer than 12 valid total holdout forecasts is Insufficient
evaluation evidence. Singleton national percentile=0.5 is a neutral convention, not a comparative finding.
Manual review triggers: Higher/Insufficient class, MASE>=1, absolute bias>=2%, or missing forecasts.
Even lower observed error only supports routine point tracking; consequential planning needs manual validation.
Horizon samples are 6/5/4 overlapping forecasts, too short for precise reliability claims. All calibrated
intervals remain unavailable. Historical errors are never relabeled probabilistic prediction intervals.
Selected-model failures and all-family failures are distinct; the latter include nonselected comparators.

Hierarchy compares direct national with all seven regional forecasts, without reconciliation. Signed
gap=sum regions−direct; absolute/relative gaps are explicit. Absolute gap>=1% prompts policy review.
Coherence is not accuracy, and the 28 eligible presentation series do not form a complete hierarchy.

## Evidence and limits

Verified descriptive finding: source-backed historical arithmetic. Validated historical model result:
frozen-model evaluation or retrospective point forecasts. Hypothetical scenario: accounting assumptions.
Exploratory signal: policy priorities/sensitivity. Insufficient evidence: explicitly unavailable support.
No confidence label carries a probability. Output-row labels and decision_evidence_register preserve
these distinctions. Rule-based recommendations point to unique source rows/metrics, list limitations
and propose investigations, without estimating savings or asserting that any action occurred.
Priority rows labeled exploratory retain explicit Insufficient evidence tiers where unscored.

Only 36 historical months; observed-sum undercoverage unknown; sparse eligible forecast subset;
correlated regions/overlapping errors; nonblind retrospective analysis; no population, case-mix,
manufacturer margin or intervention data. Analytical observation cutoffs do not reconstruct historical
release availability or revisions. No clinical appropriateness, causal, sales-force or investment conclusion.
