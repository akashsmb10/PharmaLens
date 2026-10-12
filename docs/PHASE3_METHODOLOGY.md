# Phase 3 methodology

## Objectives, population and provenance

Describe observed atorvastatin community dispensing in England, January 2023–December 2025,
and diagnose trends, costs, seasonality, anomalies and future forecast suitability. This is a fixed
administrative extract, not an independent random sample of patients or regions. Read-only Phase 2
DuckDB views are compared to all twenty Parquet exports, including original hashes. All source,
database, SQL and earlier reporting artifacts are hashed before and after execution.

Source meanings follow [the official NHSBSA resource dictionary](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data/resource/7a543ac0-923f-4ea0-91c7-13c8a719398b)
and the previously verified METRIC_DEFINITIONS.md. Items count product occurrences, not patients.
NIC is ingredient cost before discounts, not manufacturer revenue or final total NHS cost.

The fact grain is month × region × presentation × native unit. EDA populations are: one national
monthly series; one monthly series per region; one monthly series per presentation/unit; and
one series per candidate region/presentation/unit. The complete candidate grid does not assert
that every combination should occur. National and regional aggregates sum observed records;
aggregate completeness does not establish underlying-cell completeness.

## Descriptive statistics and missingness

Summaries use observed monthly values: mean, median, sample standard deviation (ddof=1), quartiles,
extrema, CV=sample SD/positive mean, observed months, missing months and coverage. Growth is
100(current/baseline−1), using calendar lags 1 and 12; zero or missing baseline is undefined.
In growth-distribution tables, observed_months counts defined growth values; missing_months also
includes lag warm-up periods and undefined zero-baseline ratios, not just absent source observations.
Weighted NIC/item equals sum(NIC)/sum(items). Quantities are never summed across presentations;
quantity anomalies are evaluated only inside one presentation and native unit. Calendar reindexing
preserves missing values, including before/after activity and never-observed pairs. No imputation,
deletion or winsorization occurs. A complete three-month rolling window is required in charts.

## Trend models

OLS fits y_t=alpha+beta*t+epsilon_t with elapsed calendar month, at least 24 observed months.
Beta is units per month; 12 beta is the fitted change in the monthly level across one year,
**not** a change in annual cumulative totals. Annual normalized effect is 1200 beta/mean(y).
For positive series, log OLS gives 100(exp(12 beta_log)−1) fitted annual proportional change.
These smooth trends can misrepresent structural shifts, nonlinear paths or seasonal behavior.

For complete histories, 95% model-conditional intervals use Bartlett HAC covariance, maxlags=3,
small-sample correction and t reference with residual degrees of freedom. These accommodate some
heteroskedasticity/autocorrelation but rely on approximate short-memory error behavior and an
adequate mean specification. With n=36, uncertainty is fragile. HAC lags 1/6/12 and eleven
month indicators are sensitivity analyses; they do not prove a model is correct. Residual lag-1
correlation and SD/mean expose remaining dependence and variability. No sampling intervals are
attached to deterministic totals. Incomplete-series HAC intervals are withheld because standard
row-lag HAC would compress calendar gaps. OLS coefficients remain descriptive calendar-time slopes.

Theil–Sen is the median of paired elapsed-time slopes, robust to isolated extremes. Its iid
confidence interval is deliberately not used. Kendall tau measures ordinal time/value association;
its iid p-value is deliberately not used. Neither method removes serial dependence or seasonality.
No multiple-testing significance claims, ANOVA or iid t-tests are made.

Implementation references: [statsmodels HAC documentation](https://www.statsmodels.org/stable/generated/statsmodels.regression.linear_model.OLSResults.get_robustcov_results.html),
[SciPy Theil–Sen](https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.stats.theilslopes.html),
[SciPy Kendall tau](https://docs.scipy.org/doc/scipy-1.14.1/reference/generated/scipy.stats.kendalltau.html).

## Seasonality

Within-year index I_(y,m)=100*y_(y,m)/mean_m(y_(y,m)). Profiles compare all three years and
their pairwise correlations. They retain within-year trend, so repeating growth can inflate apparent
seasonality. Calendar-day sensitivity divides counts by calendar days then renormalizes within each
year; it is not working-day/holiday adjustment. ACF uses ordered complete monthly observations,
lags 0–24, FFT disabled. Both raw and linear-detrended ACF are exported, without iid confidence
bounds. Incomplete histories are skipped rather than compressed or zero-filled.

Robust STL period 12 is exploratory and requires complete history >=24 months. Components satisfy
y=trend+seasonal+residual. Seasonal strength=max(0,1−Var(residual)/Var(residual+seasonal)).
Only three cycles, changing trend and cost behavior limit identification: high STL strength alone
cannot demonstrate stable seasonality. Cost and cost/item profiles can reflect shifts rather than
annual recurrence. See [statsmodels STL](https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html)
and [ACF](https://www.statsmodels.org/stable/generated/statsmodels.tsa.stattools.acf.html).

## Regional comparisons

The seven fixed NHS regions are compared in matched calendar months. Items/NIC use January 2023=100
indices to compare relative trajectories; NIC/item uses absolute GBP/item contrasts. Mean, median
and range of paired differences are effect descriptions, not confidence intervals. Calendar matching
controls calendar timing descriptively; no random-sample regional inference or population adjustment
is justified. Differences cannot establish prescribing quality, efficiency or intervention effects.

## Exact cost decomposition

For each annual comparison, C=V sum_j(s_j p_j), where V is total item volume, s is item share,
and p is weighted within-presentation NIC/item. Shapley allocations average the marginal contribution
of changing each factor across all 3!=6 orders. For factor k, phi_k=(1/6) sum_orders
[C(after k switches)−C(before k switches)]. Then sum_k phi_k=C1−C0 exactly.
We compare 2024/2023, 2025/2024 and 2025/2023 using all common presentation/unit categories.
The observed data have positive annual denominators and twelve aggregate months for each category.
New/disappearing/zero-item or incomplete categories would make unobserved counterfactual p values
unidentified; the three-factor calculation is skipped with an explicit status, not silently imputed.

The Shapley allocation is a symmetric accounting convention, not uniquely identified causal effects.
Within-presentation NIC/item combines quantity per item, basic-price inputs and subpresentation
regional/source mix. It is not a manufacturer-price estimate. The independent two-factor identity
(V1−V0)(P1+P0)/2 + (P1−P0)(V1+V0)/2 is checked against Phase 2. Three-factor volume can differ slightly
from two-factor volume because interactions are allocated differently. All residuals must be <=GBP0.01.
Presentation and regional contributions divide individual changes by the national net change;
offsetting increases mean some shares are negative and declining contributors can sum above 100%.

## Anomaly review

Every original three-IQR flag remains. Within-series robust z=0.67448975*(x−median)/MAD,
where MAD=median(|x−median|), requires >=12 observations and positive MAD. Zero MAD/short
history gives undefined z. Other diagnostic flags use |calendar MoM|>=50% and |deviation from
the prior six-calendar-month median|>=50%, with at least four observed prior months.
Thresholds are transparent review cutoffs, not calibrated false-positive probabilities.
The union yields one record per series/month/metric, with method list, original fences,
calendar neighbors, rolling baseline and evidence limits. Counts are metric flags, not unique rows.

Classification priority: invalid/negative value → Potential data issue; insufficient neighbors,
history or zero MAD → Insufficient evidence; three subsequent complete observations persist at
least 30% in the same direction relative to the prior median → Potential structural shift;
otherwise → Unusual but plausible activity. The persistence criterion uses future observations
and is retrospective, not an online detector. No review label proves a reporting error, legitimate
dispensing event or causal structural break. Actual source validation found no verified critical errors.

## Robustness and forecasting

Sensitivities include: omitting five largest original flagged rows ranked by excess beyond IQR
fences divided by within-series IQR (avoids mixing native scales); mean versus median; monthly
versus annual weighted ratios; complete/incomplete cohorts; coverage 75/90/100 and internal-gap
0/36 thresholds with >=24 months and >=36,000 items; removing the largest presentation; all regions;
and trend/HAC/month-indicator alternatives. Exclusions affect diagnostic copies only. Available-case
incomplete-cohort sums do not bound missing activity; unknown missingness can still bias conclusions.
Sensitivity ranges are not sampling uncertainty. No bootstrap is used and no synthetic population
confidence interval is supplied.

Forecast diagnostics cover national, regional, screened national presentations and Phase 2 eligible
regional/presentation series, for items and NIC. They report trend, raw/detrended variability,
zero frequency, missingness, ACF, exploratory seasonality, large changes and >=20% annual mean
shift review flags. These heuristics do not certify stationarity or forecast accuracy. No forecast
model, forecast output, stationarity-based selection or full backtest is fitted. Initial horizons
1–3 months are pragmatic; later evaluation must use chronological origins and training-only selection.
Shortlist: naive, seasonal naive, drift, damped ETS, regularized lag regression. Seasonal naive is
a benchmark, not an assumption that seasonality is established. Cost shifts require separate scrutiny.

## Limits

Three years; one chemical; fixed administrative geography; unknown absent-cell mechanisms; no
population/patient exposure, dose equivalence, dated tariff validation or intervention information.
No causal, clinical, India-market or manufacturer-revenue inference is supported. Full-history
diagnostics and persistence labels are retrospective and must not leak into Phase 4 evaluation.
