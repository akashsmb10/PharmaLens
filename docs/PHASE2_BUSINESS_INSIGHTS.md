# Phase 2 business insights

## Executive summary

The observed atorvastatin extract contains **212,022,236 prescription items** and
**£336,940,603.13 net ingredient cost** during January 2023–December 2025.
Annual item activity increased while ingredient cost fell. Four presentations dominate item activity;
regional comparisons are unadjusted and describe dispensing, not commercial performance.
Source: [NHSBSA PCA monthly](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data).

## National prescribing and ingredient-cost trends

| Year | Prescription items | NIC (£) | NIC/item (£) | Items YoY (%) | NIC YoY (%) |
|---|---|---|---|---|---|
| 2023 | 63,715,915 | 134,482,734.82 | 2.1107 | Undefined | Undefined |
| 2024 | 71,445,431 | 126,484,170.03 | 1.7704 | 12.13 | -5.95 |
| 2025 | 76,860,890 | 75,973,698.28 | 0.9885 | 7.58 | -39.93 |

Supporting output: outputs/tables/national_annual_trends.csv. Month-level MoM/YoY growth and complete
3/6/12-month rolling averages are in national_monthly_trends.csv. January 2023 had
5,079,551 items; December 2025 had 6,924,473, a
36.32%
endpoint-month change. This comparison can contain month-length and seasonal differences; comparable
calendar-year totals are the preferred descriptive comparison.

## Regional differences (unadjusted)

| Region | 2023–2025 items | Item share (%) | 2025 vs 2024 items (%) | NIC/item (£) |
|---|---|---|---|---|
| NORTH EAST AND YORKSHIRE | 45,551,756 | 21.48 | 11.09 | 1.4492 |
| MIDLANDS | 40,987,521 | 19.33 | 8.17 | 1.6354 |
| LONDON | 28,694,054 | 13.53 | 3.36 | 1.5837 |
| NORTH WEST | 27,905,174 | 13.16 | 5.82 | 1.5462 |
| SOUTH EAST | 25,019,903 | 11.80 | 7.83 | 1.8199 |
| EAST OF ENGLAND | 24,193,964 | 11.41 | 8.36 | 1.5459 |
| SOUTH WEST | 19,669,864 | 9.28 | 5.65 | 1.6458 |

Regional size reflects observed activity, not population-adjusted use or commercial success. No regional
population denominators are available. Regional contribution to national change, monthly growth and
CV are supplied in regional_annual_trends.csv, regional_monthly_trends.csv and regional_performance.csv.
The growth-versus-size chart compares 2025/2023 annual item growth with full-window item share.

## Presentation patterns

| Presentation | Items | NIC (£) | Item share (%) |
|---|---|---|---|
| Atorvastatin 20mg tablets | 106,972,067 | 145,150,699.54 | 50.453 |
| Atorvastatin 40mg tablets | 54,724,344 | 75,541,459.64 | 25.811 |
| Atorvastatin 80mg tablets | 30,434,096 | 66,438,302.35 | 14.354 |
| Atorvastatin 10mg tablets | 19,171,260 | 22,658,278.48 | 9.042 |
| Lipitor 20mg tablets | 172,581 | 5,191,005.60 | 0.081 |

Supporting output: presentation_performance.csv. Annual trends, monthly growth, item-share changes in
percentage points and contributions are in presentation_annual_trends.csv/presentation_monthly_trends.csv.
Native quantity rankings are separated by unit and are not dose-equivalent comparisons. The largest
tablet-quantity presentation is Atorvastatin 20mg tablets, with 3,634,422,123 tablets over the full
window. The highest-volume ml presentation is Atorvastatin 20mg/5ml oral suspension sugar free, with 5,697,600 ml.
There is no combined tablet-plus-ml total.

Latest comparable annual item changes among national presentations meeting the full-window activity
screen (at least 36,000 items):

| Presentation | 2025 items | 2025 vs 2024 items (%) |
|---|---|---|
| Atorvastatin 60mg tablets | 57,184 | 43.02 |
| Atorvastatin 30mg tablets | 19,760 | 26.98 |
| Lipitor 20mg tablets | 65,618 | 22.13 |
| Lipitor 20mg chewable tablets | 42,175 | 19.99 |
| Atorvastatin 80mg tablets | 11,553,041 | 12.88 |
| Atorvastatin 20mg tablets | 39,323,494 | 8.56 |
| Atorvastatin 40mg tablets | 19,628,046 | 6.82 |
| Lipitor 40mg tablets | 34,275 | 5.85 |
| Atorvastatin 10mg tablets | 6,079,825 | -4.69 |
| Lipitor 10mg tablets | 28,038 | -6.56 |

These changes do not prove clinical substitution or appropriateness. Very-low-volume liquid series have
larger percentage swings and are excluded from this table's activity screen; all 17 remain in the exports.
Among eligible regional/presentation series, the largest recent annual percentage growth is
Lipitor 20mg tablets in MIDLANDS: **38.52%**
(2025 versus 2024), with observed monthly CV **0.321**. This is a descriptive
investigation priority, not untapped potential or forecast performance. Evidence: region_presentation_summary.csv.

## Presentation contributions to ingredient-cost change

| Presentation | 2025 vs 2024 NIC change (£) | Contribution to net NIC change (%) |
|---|---|---|
| Atorvastatin 20mg tablets | -22,410,496.48 | 44.37 |
| Atorvastatin 40mg tablets | -12,318,287.82 | 24.39 |
| Atorvastatin 80mg tablets | -12,059,185.89 | 23.87 |
| Atorvastatin 10mg tablets | -4,404,489.31 | 8.72 |

The four largest absolute cost-change contributors above compare 2025 with 2024. Contributions use
the national net change denominator, so offsetting increases can have negative contributions and
contributions need not be bounded by 0–100%. Evidence: presentation_annual_trends.csv.

## Eight measured findings and interpretation

1. **Item activity increased:** 63,715,915 items in 2023 versus
   76,860,890 in 2025 (**20.63%**). The latest year grew
   7.58% versus 2024. This describes increasing recorded
   activity; it does not establish more patients or a causal demand driver. Evidence: national_annual_trends.csv.
2. **Ingredient cost moved differently:** £134,482,734.82 in 2023 versus
   £75,973,698.28 in 2025 (**-43.51%**). Weighted cost/item
   changed from £2.1107 to £0.9885.
   Basic prices, quantity/item and mix merit investigation; these are not manufacturer revenue or strategy.
   Evidence: national_annual_trends.csv and cost_analytics.csv.
3. **Regional differences persist:** NORTH EAST AND YORKSHIRE contributed 45,551,756 items
   (21.48% of this extract) in 2023–2025, with 11.09%
   growth in 2025 versus 2024. All seven regions grew in this latest annual comparison. Sizes and growth
   do not prove regional success or inappropriate use. Evidence: regional_performance.csv.
4. **One presentation accounts for half the items:** Atorvastatin 20mg tablets contributed
   106,972,067 items (50.45%) and £145,150,699.54 NIC
   in 2023–2025. Forecast aggregate and dominant-presentation activity first, while recognizing that a
   BNF presentation is not a confirmed manufacturer SKU. Evidence: presentation_performance.csv.
5. **Presentation concentration is high:** the top four account for
   99.6602% of items, with item HHI
   0.3500 (0–1 scale), over 2023–2025. This is within-chemical presentation
   concentration, not whole-market share or manufacturer concentration. Evidence: presentation_concentration.csv.
6. **Exact cost decomposition:** the 2025 versus 2024 NIC change was
   £-50,510,471.75; the symmetric item-volume effect was
   £7,470,132.05, offset by an aggregate cost-per-item-and-mix effect of
   £-57,980,603.80. This identity reconciles but does not separately
   identify price, quantity or mix causes. Evidence: cost_change_decomposition.csv.
7. **Low item share can coexist with higher cost share:** Atorvastatin 20mg/5ml oral suspension sugar free contributed
   23,456 items (0.01106%) but £8,399,251.92
   NIC (2.493%) during 2023–2025. Cost/item is £358.09.
   Different formulation, quantity and clinical context prevent conclusions about waste or substitution.
   Evidence: presentation_performance.csv and presentation_regional_costs.csv.
8. **Forecasting readiness is uneven:** 94 of 119
   candidate region/presentation series have all 36 months observed; 29 also pass the configured
   activity threshold. The 159 internal missing
   months and 161 extreme metric flags need review. No missing values were inserted as zero.
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
