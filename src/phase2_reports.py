"""Populate interview reports from executed reporting artifacts, with machine-readable claim lineage."""
import json
import pandas as pd
from .common import ROOT,write_json
from .sql_analytics import SETTINGS

def md_table(df):
    # Avoid adding an unnecessary tabulate dependency.
    columns=list(df.columns)
    lines=['| '+' | '.join(columns)+' |','|'+'|'.join(['---']*len(columns))+'|']
    for record in df.itertuples(index=False,name=None):
        lines.append('| '+' | '.join(str(x).replace('|','\\|') for x in record)+' |')
    return '\n'.join(lines)

def generate_reports(root=ROOT):
    def read(stem):
        return pd.read_parquet(root / f'outputs/tables/{stem}.parquet')
    nat=read('national_monthly_trends').sort_values('month')
    annual=read('national_annual_trends').sort_values('calendar_year')
    regions=read('regional_performance').sort_values('items_rank')
    presentations=read('presentation_performance').sort_values('items_rank')
    pareto=read('presentation_concentration').sort_values('pareto_position')
    coverage=read('series_coverage')
    missing=read('missing_series_months')
    extreme=read('extreme_value_review')
    candidates=read('forecast_candidate_series')
    sensitivity=read('threshold_sensitivity')
    decomposition=read('cost_change_decomposition')
    source=pd.read_parquet(root / 'data/processed/source_rows.parquet')
    verification=json.loads((root / 'outputs/validation/phase2_phase1_verification.json').read_text(encoding='utf-8'))
    counts=missing.coverage_status.value_counts().to_dict()
    first,last=annual.iloc[0],annual.iloc[-1]
    previous=annual.iloc[-2]
    leader=regions.iloc[0]
    top=presentations.iloc[0]
    largest_tablet=presentations[presentations.unit_of_measure=='tablet'].sort_values('total_quantity',ascending=False).iloc[0]
    largest_ml=presentations[presentations.unit_of_measure=='ml'].sort_values('total_quantity',ascending=False).iloc[0]
    liquid=presentations[presentations.unit_of_measure=='ml'].sort_values('net_ingredient_cost_gbp',ascending=False).iloc[0]
    cost_latest=decomposition[(decomposition.comparison_type=='annual')&(decomposition.period.dt.year==int(last.calendar_year))].iloc[0]
    latest_presentation=read('presentation_annual_trends')
    latest_presentation=latest_presentation[latest_presentation.calendar_year==int(last.calendar_year)]
    sufficient_keys=set(presentations.loc[presentations.prescription_items.ge(SETTINGS['minimum_total_items']),'presentation_key'])
    activity_snapshot=latest_presentation[latest_presentation.presentation_key.isin(sufficient_keys)].sort_values('items_annual_growth_pct',ascending=False)
    activity_display=pd.DataFrame({'Presentation':activity_snapshot.presentation_name,
        '2025 items':activity_snapshot.prescription_items.map(lambda x:f'{x:,}'),
        '2025 vs 2024 items (%)':activity_snapshot.items_annual_growth_pct.map(lambda x:'Undefined' if pd.isna(x) else f'{x:.2f}')})
    series_summary=read('region_presentation_summary')
    fastest=series_summary[series_summary.forecast_eligible].sort_values('recent_annual_items_growth_pct',ascending=False).iloc[0]
    cost_contributors=latest_presentation.reindex(latest_presentation.observed_cost_change_gbp.abs().sort_values(ascending=False).index).head(4)
    cost_contributor_display=pd.DataFrame({'Presentation':cost_contributors.presentation_name,
        '2025 vs 2024 NIC change (£)':cost_contributors.observed_cost_change_gbp.map(lambda x:f'{x:,.2f}'),
        'Contribution to net NIC change (%)':cost_contributors.observed_cost_change_contribution_pct.map(lambda x:f'{x:.2f}')})
    growth=100*(last.prescription_items-first.prescription_items)/first.prescription_items
    cost_growth=100*(last.net_ingredient_cost_gbp-first.net_ingredient_cost_gbp)/first.net_ingredient_cost_gbp
    # Values are unrounded source artifacts; only rendered text is rounded.
    claims=[
        {'id':'national_items_total','value':int(annual.prescription_items.sum()),'output':'national_annual_trends','column':'prescription_items','aggregation':'sum'},
        {'id':'national_cost_total','value':float(annual.net_ingredient_cost_gbp.sum()),'output':'national_annual_trends','column':'net_ingredient_cost_gbp','aggregation':'sum'},
        {'id':'latest_annual_items_growth_pct','value':float(last.items_annual_growth_pct),'output':'national_annual_trends','column':'items_annual_growth_pct','filter':{'calendar_year':int(last.calendar_year)}},
        {'id':'latest_annual_cost_growth_pct','value':float(last.cost_annual_growth_pct),'output':'national_annual_trends','column':'cost_annual_growth_pct','filter':{'calendar_year':int(last.calendar_year)}},
        {'id':'leading_region_items_share_pct','value':float(leader.items_share_pct),'output':'regional_performance','column':'items_share_pct','filter':{'region_code':leader.region_code}},
        {'id':'leading_presentation_items_share_pct','value':float(top.items_share_pct),'output':'presentation_performance','column':'items_share_pct','filter':{'presentation_key':top.presentation_key}},
        {'id':'top_four_items_share_pct','value':float(pareto.top_four_items_share_pct.iloc[0]),'output':'presentation_concentration','column':'top_four_items_share_pct','filter':{'pareto_position':1}},
        {'id':'forecast_candidate_count','value':len(candidates),'output':'forecast_candidate_series','aggregation':'count'},
        {'id':'internal_gap_count','value':int(counts.get('internal_gap_reporting_or_no_activity_unknown',0)),'output':'missing_series_months','aggregation':'count','filter':{'coverage_status':'internal_gap_reporting_or_no_activity_unknown'}},
        {'id':'extreme_flag_count','value':len(extreme),'output':'extreme_value_review','aggregation':'count'},
    ]
    write_json(root / 'outputs/validation/phase2_business_claims.json',claims)
    annual_display=pd.DataFrame({'Year':annual.calendar_year,'Prescription items':annual.prescription_items.map(lambda x:f'{x:,}'),
        'NIC (£)':annual.net_ingredient_cost_gbp.map(lambda x:f'{x:,.2f}'),
        'NIC/item (£)':annual.ingredient_cost_per_item_gbp.map(lambda x:f'{x:.4f}'),
        'Items YoY (%)':annual.items_annual_growth_pct.map(lambda x:'Undefined' if pd.isna(x) else f'{x:.2f}'),
        'NIC YoY (%)':annual.cost_annual_growth_pct.map(lambda x:'Undefined' if pd.isna(x) else f'{x:.2f}')})
    region_display=pd.DataFrame({'Region':regions.region_name,'2023–2025 items':regions.prescription_items.map(lambda x:f'{x:,}'),
        'Item share (%)':regions.items_share_pct.map(lambda x:f'{x:.2f}'),
        '2025 vs 2024 items (%)':regions.latest_annual_items_growth_pct.map(lambda x:f'{x:.2f}'),
        'NIC/item (£)':regions.ingredient_cost_per_item_gbp.map(lambda x:f'{x:.4f}')})
    top_display=pd.DataFrame({'Presentation':presentations.head(5).presentation_name,
        'Items':presentations.head(5).prescription_items.map(lambda x:f'{x:,}'),
        'NIC (£)':presentations.head(5).net_ingredient_cost_gbp.map(lambda x:f'{x:,.2f}'),
        'Item share (%)':presentations.head(5).items_share_pct.map(lambda x:f'{x:.3f}')})
    findings=f'''# Phase 2 business insights

## Executive summary

The observed atorvastatin extract contains **{int(annual.prescription_items.sum()):,} prescription items** and
**£{annual.net_ingredient_cost_gbp.sum():,.2f} net ingredient cost** during January 2023–December 2025.
Annual item activity increased while ingredient cost fell. Four presentations dominate item activity;
regional comparisons are unadjusted and describe dispensing, not commercial performance.
Source: [NHSBSA PCA monthly](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data).

## National prescribing and ingredient-cost trends

{md_table(annual_display)}

Supporting output: outputs/tables/national_annual_trends.csv. Month-level MoM/YoY growth and complete
3/6/12-month rolling averages are in national_monthly_trends.csv. January 2023 had
{int(nat.iloc[0].prescription_items):,} items; December 2025 had {int(nat.iloc[-1].prescription_items):,}, a
{100*(nat.iloc[-1].prescription_items-nat.iloc[0].prescription_items)/nat.iloc[0].prescription_items:.2f}%
endpoint-month change. This comparison can contain month-length and seasonal differences; comparable
calendar-year totals are the preferred descriptive comparison.

## Regional differences (unadjusted)

{md_table(region_display)}

Regional size reflects observed activity, not population-adjusted use or commercial success. No regional
population denominators are available. Regional contribution to national change, monthly growth and
CV are supplied in regional_annual_trends.csv, regional_monthly_trends.csv and regional_performance.csv.
The growth-versus-size chart compares 2025/2023 annual item growth with full-window item share.

## Presentation patterns

{md_table(top_display)}

Supporting output: presentation_performance.csv. Annual trends, monthly growth, item-share changes in
percentage points and contributions are in presentation_annual_trends.csv/presentation_monthly_trends.csv.
Native quantity rankings are separated by unit and are not dose-equivalent comparisons. The largest
tablet-quantity presentation is {largest_tablet.presentation_name}, with {largest_tablet.total_quantity:,.0f} tablets over the full
window. The highest-volume ml presentation is {largest_ml.presentation_name}, with {largest_ml.total_quantity:,.0f} ml.
There is no combined tablet-plus-ml total.

Latest comparable annual item changes among national presentations meeting the full-window activity
screen (at least {SETTINGS['minimum_total_items']:,} items):

{md_table(activity_display)}

These changes do not prove clinical substitution or appropriateness. Very-low-volume liquid series have
larger percentage swings and are excluded from this table's activity screen; all 17 remain in the exports.
Among eligible regional/presentation series, the largest recent annual percentage growth is
{fastest.presentation_name} in {fastest.region_name}: **{fastest.recent_annual_items_growth_pct:.2f}%**
(2025 versus 2024), with observed monthly CV **{fastest.monthly_items_cv:.3f}**. This is a descriptive
investigation priority, not untapped potential or forecast performance. Evidence: region_presentation_summary.csv.

## Presentation contributions to ingredient-cost change

{md_table(cost_contributor_display)}

The four largest absolute cost-change contributors above compare 2025 with 2024. Contributions use
the national net change denominator, so offsetting increases can have negative contributions and
contributions need not be bounded by 0–100%. Evidence: presentation_annual_trends.csv.

## Eight measured findings and interpretation

1. **Item activity increased:** {int(first.prescription_items):,} items in {int(first.calendar_year)} versus
   {int(last.prescription_items):,} in {int(last.calendar_year)} (**{growth:.2f}%**). The latest year grew
   {last.items_annual_growth_pct:.2f}% versus {int(previous.calendar_year)}. This describes increasing recorded
   activity; it does not establish more patients or a causal demand driver. Evidence: national_annual_trends.csv.
2. **Ingredient cost moved differently:** £{first.net_ingredient_cost_gbp:,.2f} in {int(first.calendar_year)} versus
   £{last.net_ingredient_cost_gbp:,.2f} in {int(last.calendar_year)} (**{cost_growth:.2f}%**). Weighted cost/item
   changed from £{first.ingredient_cost_per_item_gbp:.4f} to £{last.ingredient_cost_per_item_gbp:.4f}.
   Basic prices, quantity/item and mix merit investigation; these are not manufacturer revenue or strategy.
   Evidence: national_annual_trends.csv and cost_analytics.csv.
3. **Regional differences persist:** {leader.region_name} contributed {int(leader.prescription_items):,} items
   ({leader.items_share_pct:.2f}% of this extract) in 2023–2025, with {leader.latest_annual_items_growth_pct:.2f}%
   growth in 2025 versus 2024. All seven regions grew in this latest annual comparison. Sizes and growth
   do not prove regional success or inappropriate use. Evidence: regional_performance.csv.
4. **One presentation accounts for half the items:** {top.presentation_name} contributed
   {int(top.prescription_items):,} items ({top.items_share_pct:.2f}%) and £{top.net_ingredient_cost_gbp:,.2f} NIC
   in 2023–2025. Forecast aggregate and dominant-presentation activity first, while recognizing that a
   BNF presentation is not a confirmed manufacturer SKU. Evidence: presentation_performance.csv.
5. **Presentation concentration is high:** the top four account for
   {pareto.top_four_items_share_pct.iloc[0]:.4f}% of items, with item HHI
   {pareto.items_hhi_0_to_1.iloc[0]:.4f} (0–1 scale), over 2023–2025. This is within-chemical presentation
   concentration, not whole-market share or manufacturer concentration. Evidence: presentation_concentration.csv.
6. **Exact cost decomposition:** the 2025 versus 2024 NIC change was
   £{cost_latest.observed_cost_change_gbp:,.2f}; the symmetric item-volume effect was
   £{cost_latest.item_volume_effect_gbp:,.2f}, offset by an aggregate cost-per-item-and-mix effect of
   £{cost_latest.aggregate_unit_cost_and_mix_effect_gbp:,.2f}. This identity reconciles but does not separately
   identify price, quantity or mix causes. Evidence: cost_change_decomposition.csv.
7. **Low item share can coexist with higher cost share:** {liquid.presentation_name} contributed
   {int(liquid.prescription_items):,} items ({liquid.items_share_pct:.5f}%) but £{liquid.net_ingredient_cost_gbp:,.2f}
   NIC ({liquid.cost_share_pct:.3f}%) during 2023–2025. Cost/item is £{liquid.ingredient_cost_per_item_gbp:.2f}.
   Different formulation, quantity and clinical context prevent conclusions about waste or substitution.
   Evidence: presentation_performance.csv and presentation_regional_costs.csv.
8. **Forecasting readiness is uneven:** {int(coverage.full_window_coverage_pct.eq(100).sum())} of {len(coverage)}
   candidate region/presentation series have all 36 months observed; {len(candidates)} also pass the configured
   activity threshold. The {counts.get('internal_gap_reporting_or_no_activity_unknown',0)} internal missing
   months and {len(extreme)} extreme metric flags need review. No missing values were inserted as zero.
   Evidence: series_coverage.csv, forecast_candidate_series.csv, missing_series_months.csv and extreme_value_review.csv.

## Follow-up investigations

Review large cost/item shifts against dated Drug Tariff/basic-price reference data and quantities per item;
do not attribute them to company pricing. Examine item-share changes of tablet strengths and regional
mix while avoiding clinical-substitution claims. Confirm absent observations with publisher records where
practical, investigate the flagged series, and consider population denominators for comparable geographies.
Use transparent forecast baselines and time-based holdouts in a later phase; no models are fitted here.

## Limits

The extract covers one chemical, England community dispensing and three calendar years. It excludes
private/in-hospital activity, does not measure patient counts or India demand, and has no manufacturer
revenue, margins, promotion or prescriber engagement. Administrative geography and product attribution
can change. Missing months have unknown causes. Per-100 native-unit cost is not a standardized dose
measure. Findings are descriptive; causal and commercial-effectiveness claims are unsupported.
All statement values derive from executed SQL exports; machine-readable headline lineage is in
outputs/validation/phase2_business_claims.json. No synthetic observations enter production reporting.
'''
    (root / 'docs/PHASE2_BUSINESS_INSIGHTS.md').write_text(findings,encoding='utf-8')
    focus=extreme.groupby(['presentation_name','region_name']).size().nlargest(5).reset_index(name='metric_flags')
    near_gap=(extreme.months_since_previous_observation.gt(1)|extreme.months_until_next_observation.gt(1)).sum()
    shifts=extreme.cost_per_item_mom_change_pct.abs().ge(20).sum()
    intro=pd.Timestamp('2024-02-01')
    absent_before=int(source.loc[source.month<intro,'PHARMACY_ADVANCED_SERVICE'].isna().sum())
    absent_after=int(source.loc[source.month>=intro,'PHARMACY_ADVANCED_SERVICE'].isna().sum())
    quality=f'''# Phase 2 data-quality review

The read-only Phase 1 verification reproduced its 19-test baseline and all original quality counts.
50,456 detailed rows aggregate to 3,920 monthly rows; the six SQL model integrity checks pass.
Original raw files, processed Parquet/CSV, Phase 1 reports, notebook and validation evidence retain
their hashes. The existing monthly_prescribing DuckDB table is logically unchanged.

## Missing-series investigation

The complete candidate grid contains 36 × 7 regions × 17 valid presentation/unit pairs = 4,284 cells.
Of these, 3,920 are observed and {len(missing)} are absent. This is a diagnostic grid, not a claim that
all combinations should exist. No physical observations are generated or zero-filled.

{md_table(pd.DataFrame([{'Status':k,'Absent months':v} for k,v in sorted(counts.items())]))}

Phase 1 examined only the 117 pairs observed at least once: its **292** absent months match the
sum of before-first, after-last and internal gaps. Adding two never-observed pairs adds **72** candidate
cells whose applicability is unknown. No pair is proven structurally inapplicable from these files.
Incompatible presentation/unit combinations are excluded by the dimension design, not treated as demand gaps.
Before/after observed activity is not evidence of launch or discontinuation. Internal gaps may represent
no dispensing, reporting omissions or other mechanisms; no reason is proven. The files cannot identify
genuine reporting gaps separately from nonactivity. All {len(coverage)} candidate pairs have first/last date,
observed count, internal gaps, coverage, observed zeros and longest observed/missing runs exported.

Observed zero-item months: {int(coverage.observed_zero_item_months.sum())}. Full 36-month coverage:
{int(coverage.full_window_coverage_pct.eq(100).sum())} series. See series_coverage.csv and missing_series_months.csv.

## Extreme-value review

All **{len(extreme)}** Phase 1 flags reproduce in SQL: {extreme.metric.value_counts().to_dict()}.
They correspond to **{len(extreme[['month','region_code','presentation_key']].drop_duplicates())} distinct observed rows**;
one row may flag multiple measures. Method: three times the interquartile range outside Q1/Q3 within
one region/presentation/metric, at least 12 observed months, positive IQR. Original values are preserved.
No deletion or winsorization occurs. Neighboring observed values/dates and the calendar-month cost/item
change are exported. {int(near_gap)} flags have a missing interval between neighboring observed points.
{int(shifts)} flags coincide with an absolute calendar MoM cost/item change of at least 20% (a descriptive
review cutoff, not a price-change test). Coincidence does not identify cause; cost/item also contains
quantity/mix. Inspect monthly values and external dated basic-price data before explaining anomalies.

{md_table(focus)}

These are review findings, not proven data errors. Source numeric/date/key checks found no critical
errors. Rare/intermittent series can have legitimate extremes, and macro trends can also trigger IQR
flags; source confirmation is required. See extreme_value_review.csv and the phase2 extreme-review chart.

## Optional fields and schema evolution

Missing supplier labels: **{int(source.SUPPLIER_NAME.isna().sum()):,}**, matching Phase 1's **17,220**.
No rows are dropped for these blanks, and no supplier is inferred. PHARMACY_ADVANCED_SERVICE is absent
in resources before February 2024: **{absent_before:,}** structural nulls, matching **18,250**.
After introduction there are **{absent_after}** nulls; this extract's populated label is Not applicable.
This is schema evolution, not missing item/quantity/cost data. The official [resource dictionary](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data/resource/7a543ac0-923f-4ea0-91c7-13c8a719398b)
defines the field as the advanced service through which an item was supplied.

## Blocking and retained findings

Fact/dimension key violations, orphan joins, row multiplication, non-integral items, changed protected
artifacts, reconciliation failures and invalid source lineage block production. Coverage gaps, IQR flags
and optional metadata absence remain visible. No causal or clinical interpretation is assigned.
'''
    (root / 'docs/PHASE2_DATA_QUALITY_REVIEW.md').write_text(quality,encoding='utf-8')
    ready=f'''# Forecasting readiness (assessment only)

Primary target: monthly **prescription-item count**. Secondary target: monthly **net ingredient cost**.
No company revenue target exists and no forecasting model is trained in Phase 2.

National activity has 36 observed calendar months (January 2023–December 2025), with no aggregate
monthly gaps. Each of seven regional aggregates also has 36 observed months. All 17 national
presentation/unit aggregates have 36 observed months, but rare products have very low/intermittent
regional activity; {int(presentations.prescription_items.ge(SETTINGS['minimum_total_items']).sum())} national presentations
meet the default total-item activity screen.

## Descriptive eligibility and prioritization

Default regional/presentation eligibility requires at least **{SETTINGS['minimum_history_months']} observed months**,
**{SETTINGS['minimum_coverage_pct']}% full-window coverage**, **{SETTINGS['maximum_internal_gaps']} internal missing months**
and **{SETTINGS['minimum_total_items']:,} total items**. This yields **{len(candidates)} candidates** out of
{len(coverage)} possible pairs; {int(coverage.full_window_coverage_pct.eq(100).sum())} pairs are complete before the volume screen.
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

{md_table(sensitivity)}

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
'''
    (root / 'docs/FORECASTING_READINESS.md').write_text(ready,encoding='utf-8')
    return claims

if __name__=='__main__':
    generate_reports()
