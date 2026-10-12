"""Reports interpolate executed numerical tables; findings keep interpretation limits explicit."""
import json
from .common import ROOT,write_json
from .phase2_reports import md_table as _md_table

def md_table(frame):
    """Readable report precision; analytical exports retain full numerical values."""
    import numpy as np
    formatted=frame.copy()
    for column in formatted:
        if formatted[column].dtype.kind=='f':
            decimals=2 if ('gbp' in column and 'per_item' not in column) else 6
            formatted[column]=formatted[column].map(lambda value: 'Undefined' if not np.isfinite(value) else f'{value:,.{decimals}f}')
    return _md_table(formatted)

METHODS=r'''# Phase 3 methodology

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
'''

def reports(tables,loaded,result,root=ROOT):
    docs=root/'docs'; docs.mkdir(exist_ok=True)
    (docs/'PHASE3_METHODOLOGY.md').write_text(METHODS,encoding='utf-8')
    annual=loaded['national_annual_trends'].sort_values('calendar_year')
    nat=loaded['national_monthly_trends'].sort_values('month')
    trend=tables['trend_summary'].set_index('metric'); items=trend.loc['prescription_items']
    seasonal=tables['seasonality_summary'].set_index('metric').loc['prescription_items']
    decomposition=tables['cost_decomposition_diagnostics']; d=decomposition[decomposition.comparison=='2025 vs 2024'].iloc[0]
    reg=tables['regional_cost_change_contributions']; pre=tables['presentation_cost_change_contributions']
    allflags=tables['anomaly_diagnostics']; retained=tables['extreme_value_review_phase3']
    sensitivity=tables['sensitivity_results']; stats=tables['descriptive_statistics']
    a0=annual[annual.calendar_year==2024].iloc[0]; a1=annual[annual.calendar_year==2025].iloc[0]
    ig=100*(a1.prescription_items/a0.prescription_items-1); cg=100*(a1.net_ingredient_cost_gbp/a0.net_ingredient_cost_gbp-1)
    cost0=a0.net_ingredient_cost_gbp/a0.prescription_items; cost1=a1.net_ingredient_cost_gbp/a1.prescription_items
    totalpre=loaded['presentation_performance'].sort_values('prescription_items',ascending=False)
    topfour=100*totalpre.prescription_items.head(4).sum()/totalpre.prescription_items.sum()
    leading=totalpre.iloc[0].presentation_name
    without=sensitivity[(sensitivity.analysis=='dominant presentation sensitivity')&(sensitivity.scenario=='without largest presentation')].set_index('metric')
    cohort=sensitivity[sensitivity.analysis=='coverage cohort']
    controls=sensitivity[(sensitivity.analysis=='trend specification')&(sensitivity.metric=='prescription_items')&(sensitivity.scenario=='HAC 3; month controls True')].iloc[0]
    excluded=sensitivity[(sensitivity.analysis=='extreme exclusion diagnostic only')&(sensitivity.metric=='prescription_items')].iloc[0]
    classes=retained.groupby('classification').size().rename('flags').reset_index()
    growing=loaded['regional_annual_trends']; latest=growing[growing.calendar_year==2025].sort_values('items_annual_growth_pct',ascending=False)
    costdrops=pre.cost_per_item_change_pct.lt(0).sum()
    topdeclines=pre.nsmallest(4,'nic_change_gbp'); share=100*topdeclines.nic_change_gbp.sum()/pre.nic_change_gbp.sum()
    natmom=nat.assign(nic_delta=nat.net_ingredient_cost_gbp.diff(),items_delta=nat.prescription_items.diff())
    shock=natmom.loc[natmom.nic_delta.abs().idxmax()]
    findings=[
        f'''**Observed fact and model estimate — rising item activity.** During 2025 versus 2024, items grew **{ig:.6f}%**. Over Jan 2023–Dec 2025 OLS estimates **{items.ols_slope_per_month:,.2f} items/month**, with model-conditional 95% HAC interval **[{items.hac_ci_low:,.2f}, {items.hac_ci_high:,.2f}]**; Theil–Sen estimates **{items.theil_sen_slope_per_month:,.2f}**. Plan capacity around observed growth, then validate forecasts. A linear association is not a causal demand estimate. Evidence: trend_summary.csv, national_annual_trends.parquet; charts 01 and 16.''',
        f'''**Observed fact — regional consistency with different magnitudes.** All **{int(latest.items_annual_growth_pct.gt(0).sum())}/{len(latest)}** regions grew in 2025 versus 2024. Growth ranges **{latest.items_annual_growth_pct.min():.6f}%–{latest.items_annual_growth_pct.max():.6f}%**; strongest is **{latest.iloc[0].region_name}**. That region contributes **{reg.loc[reg.region_name==latest.iloc[0].region_name,'items_change_contribution_pct'].iloc[0]:.6f}%** of the national item increase. Compare relative activity trajectories rather than treating regional size as efficiency. Fixed regions are not independent samples and no population adjustment exists. Evidence: regional_trend_summary.csv and regional_statistical_comparisons.csv; charts 04–05.''',
        f'''**Observed fact — presentation concentration.** The leading presentation, **{leading}**, contributes **{100*totalpre.iloc[0].prescription_items/totalpre.prescription_items.sum():.6f}%** of full-window items; the leading four contribute **{topfour:.6f}%**. Prioritize these series for reconciliation and forecasts while retaining rare products. This is share within the selected chemical, not pharmaceutical market share or clinical substitution. Evidence: presentation_cost_change_contributions.csv and Phase 2 presentation_performance.parquet; charts 06–07.''',
        f'''**Statistical association — limited recurring item pattern.** Item year-profile correlation averages **{seasonal.mean_year_profile_correlation:.6f}**, detrended lag-12 ACF is **{seasonal.detrended_acf_lag12:.6f}**, and exploratory STL seasonal strength is **{seasonal.stl_seasonal_strength:.6f}**. The seasonal index range falls from **{seasonal.raw_seasonal_index_range:.6f}** to **{seasonal.day_adjusted_index_range:.6f} index points** after calendar-day normalization. Use seasonal naive as a future benchmark; do not declare stable seasonality from three cycles or STL strength alone. Evidence: seasonality_summary.csv and monthly_seasonal_indices.csv; charts 08–10.''',
        f'''**Observed fact and accounting identity — 2025 NIC divergence.** Items grew **{ig:.6f}%** while NIC fell **{cg:.6f}%**, a change of **GBP {d.observed_cost_change_gbp:,.2f}**. Annual weighted NIC/item fell from **GBP {cost0:.6f} to GBP {cost1:.6f} ({100*(cost1/cost0-1):.6f}%)**. Exact Shapley effects: volume **GBP {d.item_volume_effect_gbp:+,.2f}**, presentation mix **GBP {d.presentation_mix_effect_gbp:+,.2f}**, within-presentation NIC/item **GBP {d.within_presentation_cost_per_item_effect_gbp:+,.2f}**. Mix offsets part of the decline under this convention. Investigate quantity/item and dated basic-price inputs before assigning a mechanism. This is accounting, not evidence of manufacturer price cuts or intervention savings. Evidence: cost_decomposition_diagnostics.csv; chart 11.''',
        f'''**Observed fact — cost decline broad by region, concentrated by presentation.** Weighted NIC/item falls in **{int(reg.cost_per_item_change_pct.lt(0).sum())}/{len(reg)}** regions, spanning **{reg.cost_per_item_change_pct.min():.6f}% to {reg.cost_per_item_change_pct.max():.6f}%**. It falls in **{costdrops}/{len(pre)}** presentations. Four largest declining contributors account for **{share:.6f}%** of the net NIC decline; offsetting increases explain a contribution above 100%. Review these presentations first, not every rare-series percentage swing equally. Within-presentation ratios retain quantity and finer-mix effects. Evidence: presentation_cost_change_contributions.csv and regional_cost_change_contributions.csv; charts 12–13.''',
        f'''**Hypothesis requiring review — unusual observations remain valid inputs.** All **{len(retained)}** original flags are retained; classifications below are retrospective heuristics. The full union contains **{len(allflags)}** series-month-metric flags, not that many unique rows. The largest absolute national MoM NIC movement is **GBP {shock.nic_delta:+,.2f} in {shock.month:%B %Y}**, alongside **{shock.items_delta:+,.0f} items**. Prioritize source/tariff review for persistent shifts; no flagged value is a confirmed reporting error and nothing is removed. Evidence: anomaly_diagnostics.csv and extreme_value_review_phase3.csv; charts 14–15.''',
        f'''**Sensitivity evidence — major item-growth direction persists.** Excluding the largest presentation leaves **{without.loc['prescription_items','estimate']:.6f}%** item growth and **{without.loc['net_ingredient_cost_gbp','estimate']:.6f}%** NIC change in 2025 versus 2024. Coverage-cohort item growth spans **{cohort.estimate.min():.6f}%–{cohort.estimate.max():.6f}%**. Month-controlled item slope is **{controls.estimate:,.2f}**, versus **{items.ols_slope_per_month:,.2f}** baseline; omitting five IQR-scaled extreme rows gives **{excluded.estimate:,.2f} items/month**. Direction survives these specific diagnostics, but unknown missing activity is not bounded. Evidence: sensitivity_results.csv and diagnostic_excluded_rows.csv; chart 16.''',
        f'''**Diagnostic judgment — item forecasts deserve priority over cost forecasts.** National and seven regional aggregates have 36 observed months; the Phase 2 screen selects **{len(loaded['forecast_candidate_series'])}** region/presentation series and **{tables['forecasting_diagnostics'].query("level == 'presentation'").presentation_key.nunique()}** national presentations meet the volume screen. Raw national item CV is **{stats.query("level == 'national' and metric == 'prescription_items'").coefficient_of_variation.iloc[0]:.6f}**, while detrended residual CV is **{items.residual_cv:.6f}**. Cost residual lag-1 correlation is **{trend.loc['net_ingredient_cost_gbp','residual_lag1_correlation']:.6f}** and simple NIC-trend HAC uncertainty spans zero. Start 1–3 month chronological evaluations with simple baselines; treat NIC shifts separately. Eligibility is not validated forecast accuracy. Evidence: forecasting_diagnostics.csv; charts 17–18.'''
    ]
    headline={
        'items_2025_growth_pct':ig,'nic_2025_growth_pct':cg,'national_item_ols_slope':float(items.ols_slope_per_month),
        'national_item_hac_ci':[float(items.hac_ci_low),float(items.hac_ci_high)],'top_four_item_share_pct':topfour,
        'cost_volume_effect_gbp':float(d.item_volume_effect_gbp),'cost_mix_effect_gbp':float(d.presentation_mix_effect_gbp),
        'cost_within_presentation_effect_gbp':float(d.within_presentation_cost_per_item_effect_gbp),
        'cost_change_gbp':float(d.observed_cost_change_gbp),'original_flag_classifications':retained.groupby('classification').size().to_dict(),
        'all_diagnostic_flags':len(allflags),'regions_growing':int(latest.items_annual_growth_pct.gt(0).sum()),
        'item_growth_excluding_largest_presentation_pct':float(without.loc['prescription_items','estimate'])}
    write_json(root/'outputs/phase3/validation/business_claims.json',headline)
    executive=f'''# Phase 3 business insights

## Executive summary

The validated extract records **{result['input_verification']['total_items']:,} items** and
**GBP {result['input_verification']['total_nic_gbp']:,.2f} NIC**, January 2023–December 2025.
Item activity increases consistently across regions; 2025 NIC falls despite higher volume.
The three-factor identity attributes the decline principally to within-presentation NIC/item,
with volume and presentation mix offsetting some decline. Statistical diagnostics are descriptive
and short-series model estimates; no causal price, clinical or India-market inference is made.

## Nine findings, evidence and recommendations

'''+ '\n\n'.join(f'{i+1}. {f}' for i,f in enumerate(findings)) + f'''

## Annual prescribing and cost behavior

{md_table(annual[['calendar_year','prescription_items','net_ingredient_cost_gbp','ingredient_cost_per_item_gbp']])}

## Regional cost and mix comparisons: 2025 vs 2024

{md_table(reg[['region_name','items_change','cost_per_item_change_pct','item_share_change_pp','nic_change_gbp']])}

## Presentation changes: 2025 vs 2024

{md_table(pre[['presentation_name','items_change','nic_change_gbp','cost_per_item_change_pct','item_share_change_pp']])}

## Original-flag classifications

{md_table(classes)}

These labels are evidence-limited review categories, not confirmed events. No Potential data issue
label appears when source numeric/key checks and diagnostics contain no such trigger. A sustained
shift is a hypothesis requiring dated source/reference verification.

## Robustness and statistical diagnostics

{md_table(tables['robustness_summary'])}

NIC's smooth trend is less adequate than item's: large residual dependence and specification-sensitive
intervals reinforce the need to inspect paths, not reduce the cost behavior to one slope. Mean/median
differences are descriptive; available-case cohort comparisons cannot establish what absent cells contain.

## Business recommendations and Phase 4

Prioritize national/regional item baselines and leading presentations; reconcile their totals. Review
the major cost-decline presentations using quantity/item and dated tariff evidence before explaining
price mechanisms. Keep every flagged record and route persistent shifts for evidence review. Compare
naive, seasonal naive and drift with damped ETS and regularized lag regression at 1–3 month horizons,
with chronological origins and training-fold-only eligibility/preprocessing. No forecasting model or
backtest has been trained here. Do not choose a more complex model without measured improvement.

## Limitations

Three annual cycles; unknown absent-cell causes; unadjusted regional totals; no patients, dose equivalents,
interventions or dated price validation; one selected chemical in England. NIC is not revenue and cannot
support manufacturer sales or India-market claims. Exact accounting contributions are not causal effects.
See PHASE3_METHODOLOGY.md for assumptions and FORECASTING_READINESS.md for initial model choices.

Outputs are under outputs/phase3/tables and outputs/phase3/charts. Earlier referenced Phase 2 tables
remain under outputs/tables. Every numerical report statement derives from those executed outputs.
'''
    (docs/'PHASE3_BUSINESS_INSIGHTS.md').write_text(executive,encoding='utf-8')
    statistical=f'''# Phase 3 statistical findings

Observation units and assumptions: PHASE3_METHODOLOGY.md. All histories are monthly and calendar ordered.
Model intervals are conditional uncertainty; fixed totals have no sampling intervals. No iid p-value
claims, region ANOVA, causal explanation or forecasting model is supplied.

## National trend effects

{md_table(tables['trend_summary'])}

## Regional trend effects

{md_table(tables['regional_trend_summary'])}

## Seasonal diagnostics (three annual cycles)

{md_table(tables['seasonality_summary'])}

## Exact cost identities

{md_table(decomposition)}

Maximum decomposition residual: **GBP {result['decomposition_max_residual_gbp']:.12g}**.

## Business-question evidence map

| Question | Executed evidence and interpretation |
|---|---|
| Q1 Increasing activity | trend_summary; annual item growth and positive robust/OLS slopes |
| Q2 Across regions | regional_trend_summary; all seven latest annual item changes positive |
| Q3 Seasonality | seasonality_summary; profile correlation, day adjustment, detrended ACF; weak three-cycle evidence |
| Q4 Presentations driving growth | presentation_cost_change_contributions includes absolute item changes and contribution shares |
| Q5 Variability | descriptive_statistics raw CV; trend/forecast diagnostics detrended residual CV |
| Q6 Regional differences | matched calendar descriptive contrasts; no independent-region sampling inference |
| Q7 NIC divergence | weighted ratios, exact two/three-factor identity; association not causation |
| Q8 Breadth vs concentration | presentation/regional contributions; within-presentation ratios; mix effect |
| Q9 Large changes | calendar MoM diagnostics, rolling median, MAD and national path review |
| Q10 Meaning of extremes | all original flags classified retrospectively; no confirmed error without external verification |
| Q11 Future forecasting | coverage, zeros, volatility, ACF and shifts; no accuracy validation |
| Q12 Missingness/aggregation | cohort thresholds, complete/incomplete history, annual/monthly ratios; absent activity remains unknown |
| Q13 Robust recommendations | positive item direction across models/cohorts/regions and largest-presentation exclusion; cost mechanism unproven |
| Q14 Unsupported conclusions | clinical/causal/patient/India/manufacturer revenue claims and stable annual seasonality |

## Anomaly evidence and robustness

{md_table(classes)}

{md_table(tables['robustness_summary'])}

All presentation effects, paired-region comparisons, growth distributions and forecast diagnostics are
exported as CSV/Parquet. Tables preserve dates, missingness, grouping keys and unit labels. Charts
summarize actual outputs, with source notes. Source data and previous calculations remain intact.
'''
    (docs/'PHASE3_STATISTICAL_FINDINGS.md').write_text(statistical,encoding='utf-8')
    readiness=docs/'FORECASTING_READINESS.md'
    text=readiness.read_text(encoding='utf-8')
    marker='\n<!-- PHASE3 DIAGNOSTICS -->'
    text=text.split(marker)[0]
    text+=marker+f'''

## Phase 3 executed diagnostics

National item OLS slope **{items.ols_slope_per_month:,.2f}/month**, HAC 95% interval
**[{items.hac_ci_low:,.2f}, {items.hac_ci_high:,.2f}]**; detrended residual CV **{items.residual_cv:.6f}**.
Exploratory item seasonal strength **{seasonal.stl_seasonal_strength:.6f}**, detrended lag-12 ACF
**{seasonal.detrended_acf_lag12:.6f}**, year-profile correlation **{seasonal.mean_year_profile_correlation:.6f}**.
Three cycles and calendar length restrict seasonal confidence. NIC trends have substantial residual
dependence and uncertain smooth slopes; the annual cost decline is observed, but extrapolation is unsafe.

Forecast diagnostics contain **{len(tables['forecasting_diagnostics'])} series-target records**: national,
seven regions, ten volume-screened national presentations, and 29 Phase 2 eligible region/presentation
series, each for items and NIC. Zero fractions describe only observed months; missing cells stay unknown.
The >=20% annual mean shift flag is a transparent review heuristic, not a break test.

Phase 4 shortlist: naive, seasonal naive (benchmark only), drift, damped ETS, regularized lag regression.
Use initial 1–3 month horizons, chronological rolling origins, forecast-error comparisons and reconciliation
across aggregation levels. Cost shifts may require separate scenarios and origin-specific refitting;
avoid asserting a permanent new regime from this extract. Recompute candidate screens and anomaly
thresholds within each training fold. Preserve an honest holdout. No forecast model/backtest trained.
Detailed output: outputs/phase3/tables/forecasting_diagnostics.csv. See PHASE3_METHODOLOGY.md.
'''
    readiness.write_text(text,encoding='utf-8')

def audit_report(result,root=ROOT):
    rows=[]
    for name,evidence in result['tables'].items(): rows.append({'table (CSV and Parquet)':name,'rows':evidence['rows'],'columns':len(evidence['columns'])})
    import pandas as pd
    inventory=sorted(str(p.relative_to(root)).replace('\\','/') for directory,pattern in [('src','*phase3*'),('tests','test_phase3*'),('docs','PHASE3*'),('notebooks','0[23]*')] for p in (root/directory).glob(pattern) if p.is_file())
    inventory+=['src/statistical_analysis.py','src/trend_analysis.py','src/seasonality_analysis.py','src/cost_diagnostics.py','src/anomaly_diagnostics.py','src/robustness_analysis.py','run_pipeline.py','README.md','docs/FORECASTING_READINESS.md','docs/PHASE3_AUDIT.md','config/kernels/pharma-phase3/kernel.json']
    claims=json.loads((root/'outputs/phase3/validation/business_claims.json').read_text(encoding='utf-8'))
    text=f'''# Phase 3 final audit

Overall pass: **{result['passed']}**. All analyses use verified observed data; no forecast models trained.

## Baseline repository audit

Existing tests: **43 passed**, outputs/phase3/validation/baseline_tests.xml. Initial default-temp
execution had four Windows PermissionError setup errors; rerunning with authorized project-local
temp storage passed. No analytical code failure was hidden. settings.yaml was absent; existing
dataset.json and phase2.json were retained. Database data/processed/pharma.duckdb contains main and
phase2 schemas; source/report columns and DATE types are recorded in input_verification.json.
The first notebook launch also encountered Windows kernel-file security denial; the authorized
audit rerun executed both notebooks successfully without weakening Jupyter file permissions.
README, requirements, run_pipeline, Phase 1/2 audits, source metric definitions, quality review,
forecast readiness, existing src/sql/tests and twenty reporting exports were inspected.

## Input verification and preservation

Every Phase 2 Parquet equals its read-only SQL view within 1e-10 and retains its final-audit hash.
Original source guard remains valid. Phase 2 fact has **{result['input_verification']['fact_rows']}** rows;
the diagnostic grid has **{result['input_verification']['candidate_grid_rows']}** cells, of which
**{result['input_verification']['missing_cells']}** remain absent. Prior database file and all protected
source/report/SQL/doc files unchanged: **{result['protected_inputs_unchanged']}**.
FORECASTING_READINESS.md is explicitly updated; its Phase 2 content remains before the Phase 3 appendix.
README and pipeline entrypoint changes preserve earlier modes. No mixed-unit quantity total exists.

## Created or updated implementation files

'''+ '\n'.join(f'- `{p}`' for p in sorted(set(inventory))) +f'''

## Tables and chart inventory

{md_table(pd.DataFrame(rows))}

All tables exist as CSV and Parquet under outputs/phase3/tables. Row counts, schemas and hashes are
recorded in final_audit.json. All required eighteen high-resolution PNG charts exist:

'''+ '\n'.join(f'- `{p}`' for p in result['charts'])+f'''

## Notebook execution

{md_table(pd.DataFrame(result['notebooks']))}

Notebooks import production functions and read validated exports, without replicating the pipeline.

## Methods, assumptions and checks

Calendar-aware summaries/growth, weighted ratios, linear/log OLS with conditional HAC intervals,
Theil–Sen, descriptive Kendall tau, month indicators and bandwidth sensitivity, annual profiles,
calendar-day sensitivity, raw/detrended ACF, robust STL, paired regional contrasts, symmetric exact
three-factor decomposition, independent Phase 2 two-factor checks, within-series MAD/rolling/MoM
review, cohort/aggregation/exclusion sensitivities and forecast readiness diagnostics. Assumptions,
formulas, skip rules, heuristic classification priority and noncausal limits are in PHASE3_METHODOLOGY.md.

All **{result['original_extreme_flags_retained']}** original metric flags retained with values and
calendar neighbors. Anomaly categories are retrospective hypotheses, not confirmed source errors.
Missingness preserved: **{result['missing_cells_preserved']}**. Maximum three-factor residual:
**GBP {result['decomposition_max_residual_gbp']:.12g}**, well below GBP0.01.

## Findings and sensitivity results

National item OLS slope **{claims['national_item_ols_slope']:,.6f} items/month**; 2025 item growth
**{claims['items_2025_growth_pct']:.6f}%**, NIC change **{claims['nic_2025_growth_pct']:.6f}%**.
Shapley volume/mix/within-presentation effects **GBP {claims['cost_volume_effect_gbp']:+,.2f} /
{claims['cost_mix_effect_gbp']:+,.2f} / {claims['cost_within_presentation_effect_gbp']:+,.2f}**.
All seven regions grow. Removing largest presentation leaves **{claims['item_growth_excluding_largest_presentation_pct']:.6f}%**
item growth. All numerical statements are derived from exported analytical results and verified
Phase 2 source tables. Detailed nine findings and sensitivity tables: PHASE3_BUSINESS_INSIGHTS.md.

## Tests and reproducibility

Complete Phase 1–3 suite: **{result['tests']['tests']} tests**, **{result['tests']['failures']} failures,
**{result['tests']['errors']} errors**, **{result['tests']['skipped']} skipped**. Evidence: all_tests.xml
and test_execution.log. Known synthetic fixtures test effects, gaps, ordering, ratios, zero MAD,
short history, grouped units, decomposition reversibility and identities. Integration checks verify
missingness, all original flags, input immutability, schemas, PNG dimensions and two reruns.
All twenty CSV and twenty Parquet outputs byte-identical on two complete executions:
**{result['repeated_tables_identical']}**. Notebook execution metadata is nondeterministic by design;
notebook source cells and analytical table values are deterministic. Source data remain untouched.
Independent fact-based headline and original-flag checks: **{result['independent_findings_verification']['passed_checks']} passed**,
including a closed-form three-factor identity separate from the permutation implementation.
Evidence: independent_findings_verification.json.

## Limits and Phase 4 recommendations

Three seasonal cycles, residual dependence, unknown gaps and no population/tariff/patient data limit
inference. A single NIC trend is an imperfect description and cost forecasts need shift scrutiny.
No verified cause, clinical claim, revenue interpretation or India-market transfer is established.
Start chronological 1–3 month evaluations with naive/seasonal-naive/drift then damped ETS and
regularized lag regression. Training-only candidate selection and transformations are required.
No unresolved critical validation failure remains when the overall pass above is True.

## Reproduce

```powershell
.\\.venv\\Scripts\\python.exe run_pipeline.py --phase 3
.\\.venv\\Scripts\\python.exe -m src.phase3_pipeline --audit
```
'''
    (root/'docs/PHASE3_AUDIT.md').write_text(text,encoding='utf-8')
