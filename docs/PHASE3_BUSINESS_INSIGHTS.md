# Phase 3 business insights

## Executive summary

The validated extract records **212,022,236 items** and
**GBP 336,940,603.13 NIC**, January 2023–December 2025.
Item activity increases consistently across regions; 2025 NIC falls despite higher volume.
The three-factor identity attributes the decline principally to within-presentation NIC/item,
with volume and presentation mix offsetting some decline. Statistical diagnostics are descriptive
and short-series model estimates; no causal price, clinical or India-market inference is made.

## Nine findings, evidence and recommendations

1. **Observed fact and model estimate — rising item activity.** During 2025 versus 2024, items grew **7.579853%**. Over Jan 2023–Dec 2025 OLS estimates **46,650.04 items/month**, with model-conditional 95% HAC interval **[41,844.58, 51,455.49]**; Theil–Sen estimates **47,729.62**. Plan capacity around observed growth, then validate forecasts. A linear association is not a causal demand estimate. Evidence: trend_summary.csv, national_annual_trends.parquet; charts 01 and 16.

2. **Observed fact — regional consistency with different magnitudes.** All **7/7** regions grew in 2025 versus 2024. Growth ranges **3.362745%–11.094574%**; strongest is **NORTH EAST AND YORKSHIRE**. That region contributes **31.380147%** of the national item increase. Compare relative activity trajectories rather than treating regional size as efficiency. Fixed regions are not independent samples and no population adjustment exists. Evidence: regional_trend_summary.csv and regional_statistical_comparisons.csv; charts 04–05.

3. **Observed fact — presentation concentration.** The leading presentation, **Atorvastatin 20mg tablets**, contributes **50.453230%** of full-window items; the leading four contribute **99.660192%**. Prioritize these series for reconciliation and forecasts while retaining rare products. This is share within the selected chemical, not pharmaceutical market share or clinical substitution. Evidence: presentation_cost_change_contributions.csv and Phase 2 presentation_performance.parquet; charts 06–07.

4. **Statistical association — limited recurring item pattern.** Item year-profile correlation averages **0.668679**, detrended lag-12 ACF is **0.220321**, and exploratory STL seasonal strength is **0.802226**. The seasonal index range falls from **15.812292** to **8.569063 index points** after calendar-day normalization. Use seasonal naive as a future benchmark; do not declare stable seasonality from three cycles or STL strength alone. Evidence: seasonality_summary.csv and monthly_seasonal_indices.csv; charts 08–10.

5. **Observed fact and accounting identity — 2025 NIC divergence.** Items grew **7.579853%** while NIC fell **-39.934224%**, a change of **GBP -50,510,471.75**. Annual weighted NIC/item fell from **GBP 1.770361 to GBP 0.988457 (-44.166334%)**. Exact Shapley effects: volume **GBP +7,478,389.50**, presentation mix **GBP +1,254,765.30**, within-presentation NIC/item **GBP -59,243,626.55**. Mix offsets part of the decline under this convention. Investigate quantity/item and dated basic-price inputs before assigning a mechanism. This is accounting, not evidence of manufacturer price cuts or intervention savings. Evidence: cost_decomposition_diagnostics.csv; chart 11.

6. **Observed fact — cost decline broad by region, concentrated by presentation.** Weighted NIC/item falls in **7/7** regions, spanning **-45.695266% to -42.646320%**. It falls in **11/17** presentations. Four largest declining contributors account for **101.350191%** of the net NIC decline; offsetting increases explain a contribution above 100%. Review these presentations first, not every rare-series percentage swing equally. Within-presentation ratios retain quantity and finer-mix effects. Evidence: presentation_cost_change_contributions.csv and regional_cost_change_contributions.csv; charts 12–13.

7. **Hypothesis requiring review — unusual observations remain valid inputs.** All **161** original flags are retained; classifications below are retrospective heuristics. The full union contains **2102** series-month-metric flags, not that many unique rows. The largest absolute national MoM NIC movement is **GBP +9,393,170.11 in July 2023**, alongside **-103,022 items**. Prioritize source/tariff review for persistent shifts; no flagged value is a confirmed reporting error and nothing is removed. Evidence: anomaly_diagnostics.csv and extreme_value_review_phase3.csv; charts 14–15.

8. **Sensitivity evidence — major item-growth direction persists.** Excluding the largest presentation leaves **6.576248%** item growth and **-38.662185%** NIC change in 2025 versus 2024. Coverage-cohort item growth spans **7.579949%–7.580323%**. Month-controlled item slope is **45,642.27**, versus **46,650.04** baseline; omitting five IQR-scaled extreme rows gives **46,648.62 items/month**. Direction survives these specific diagnostics, but unknown missing activity is not bounded. Evidence: sensitivity_results.csv and diagnostic_excluded_rows.csv; chart 16.

9. **Diagnostic judgment — item forecasts deserve priority over cost forecasts.** National and seven regional aggregates have 36 observed months; the Phase 2 screen selects **29** region/presentation series and **10** national presentations meet the volume screen. Raw national item CV is **0.090151**, while detrended residual CV is **0.034103**. Cost residual lag-1 correlation is **0.801529** and simple NIC-trend HAC uncertainty spans zero. Start 1–3 month chronological evaluations with simple baselines; treat NIC shifts separately. Eligibility is not validated forecast accuracy. Evidence: forecasting_diagnostics.csv; charts 17–18.

## Annual prescribing and cost behavior

| calendar_year | prescription_items | net_ingredient_cost_gbp | ingredient_cost_per_item_gbp |
|---|---|---|---|
| 2023 | 63715915 | 134,482,734.82 | 2.110662 |
| 2024 | 71445431 | 126,484,170.03 | 1.770361 |
| 2025 | 76860890 | 75,973,698.28 | 0.988457 |

## Regional cost and mix comparisons: 2025 vs 2024

| region_name | items_change | cost_per_item_change_pct | item_share_change_pp | nic_change_gbp |
|---|---|---|---|---|
| LONDON | 326443 | -45.695266 | -0.532626 | -7,480,041.46 |
| SOUTH WEST | 375498 | -44.758044 | -0.167134 | -5,046,955.77 |
| SOUTH EAST | 660508 | -44.078259 | 0.027319 | -6,804,549.31 |
| MIDLANDS | 1126239 | -42.945773 | 0.105548 | -9,590,043.09 |
| EAST OF ENGLAND | 679144 | -42.646320 | 0.082445 | -5,283,425.99 |
| NORTH WEST | 548248 | -45.062624 | -0.215982 | -6,797,613.50 |
| NORTH EAST AND YORKSHIRE | 1699379 | -44.317374 | 0.700430 | -9,507,842.63 |

## Presentation changes: 2025 vs 2024

| presentation_name | items_change | nic_change_gbp | cost_per_item_change_pct | item_share_change_pp |
|---|---|---|---|---|
| Atorvastatin 10mg tablets | -299443 | -4,404,489.31 | -47.524631 | -1.018700 |
| Atorvastatin 20mg tablets | 3099228 | -22,410,496.48 | -46.251142 | 0.459898 |
| Atorvastatin 40mg tablets | 1253443 | -12,318,287.82 | -46.397170 | -0.181269 |
| Atorvastatin 80mg tablets | 1317873 | -12,059,185.89 | -52.731370 | 0.705251 |
| Atorvastatin 20mg/5ml oral solution | -26 | -4,174.12 | 15.245187 | -0.000046 |
| Atorvastatin 10mg/5ml oral solution | -162 | 45,709.04 | 993.803775 | -0.000239 |
| Atorvastatin 30mg tablets | 4199 | -180,218.61 | -62.293131 | 0.003929 |
| Atorvastatin 60mg tablets | 17202 | -513,119.62 | -67.084667 | 0.018438 |
| Atorvastatin 20mg/5ml oral suspension | -167 | -44,772.71 | 12.542956 | -0.000272 |
| Atorvastatin 10mg/5ml oral suspension | -29 | 210.93 | 105.145983 | -0.000043 |
| Atorvastatin 20mg/5ml oral suspension sugar free | 1809 | 769,343.60 | 3.295256 | 0.001585 |
| Lipitor 10mg tablets | -1970 | -38,960.06 | -0.914517 | -0.005522 |
| Lipitor 20mg tablets | 11892 | 275,728.64 | -4.328822 | 0.010174 |
| Lipitor 40mg tablets | 1893 | 43,978.88 | -1.167786 | -0.000731 |
| Lipitor 80mg tablets | 277 | 7,832.40 | -0.414664 | -0.000614 |
| Lipitor 10mg chewable tablets | 2415 | 73,247.64 | 25.480689 | 0.002489 |
| Lipitor 20mg chewable tablets | 7025 | 247,181.74 | -0.003006 | 0.005673 |

## Original-flag classifications

| classification | flags |
|---|---|
| Insufficient evidence | 16 |
| Potential structural shift | 61 |
| Unusual but plausible activity | 84 |

These labels are evidence-limited review categories, not confirmed events. No Potential data issue
label appears when source numeric/key checks and diagnostics contain no such trigger. A sustained
shift is a hypothesis requiring dated source/reference verification.

## Robustness and statistical diagnostics

| analysis | metric | scenarios | minimum_estimate | maximum_estimate | all_positive | all_negative | unit | interpretation |
|---|---|---|---|---|---|---|---|---|
| annual aggregation | ingredient_cost_per_item_gbp | 1 | -44.166334 | -44.166334 | False | True | percent; annual ratio weighted, monthly reference unweighted | Sensitivity range, not sampling confidence interval |
| annual aggregation | net_ingredient_cost_gbp | 1 | -39.934224 | -39.934224 | False | True | percent; annual ratio weighted, monthly reference unweighted | Sensitivity range, not sampling confidence interval |
| annual aggregation | prescription_items | 1 | 7.579853 | 7.579853 | True | False | percent; annual ratio weighted, monthly reference unweighted | Sensitivity range, not sampling confidence interval |
| coverage cohort | prescription_items | 3 | 7.579949 | 7.580323 | True | False | percent observed-sum annual growth; absent cells unknown | Sensitivity range, not sampling confidence interval |
| coverage eligibility | prescription_items | 6 | 29.000000 | 29.000000 | True | False | candidate series count | Sensitivity range, not sampling confidence interval |
| dominant presentation sensitivity | net_ingredient_cost_gbp | 2 | -39.934224 | -38.662185 | False | True | percent annual growth | Sensitivity range, not sampling confidence interval |
| dominant presentation sensitivity | prescription_items | 2 | 6.576248 | 7.579853 | True | False | percent annual growth | Sensitivity range, not sampling confidence interval |
| extreme exclusion diagnostic only | ingredient_cost_per_item_gbp | 1 | -0.039439 | -0.039439 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| extreme exclusion diagnostic only | net_ingredient_cost_gbp | 1 | -167,388.088837 | -167,388.088837 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| extreme exclusion diagnostic only | prescription_items | 1 | 46,648.621750 | 46,648.621750 | True | False | metric units/month | Sensitivity range, not sampling confidence interval |
| history cohorts | prescription_items | 2 | 0.201693 | 0.604190 | True | False | median observed-month CV | Sensitivity range, not sampling confidence interval |
| mean versus median | ingredient_cost_per_item_gbp | 2 | 1.312082 | 1.620331 | True | False | metric units | Sensitivity range, not sampling confidence interval |
| mean versus median | net_ingredient_cost_gbp | 2 | 8,234,836.005000 | 9,359,461.198056 | True | False | metric units | Sensitivity range, not sampling confidence interval |
| mean versus median | prescription_items | 2 | 5,889,506.555556 | 5,903,641.000000 | True | False | metric units | Sensitivity range, not sampling confidence interval |
| regional consistency | net_ingredient_cost_gbp | 7 | -31,439.458905 | -17,465.199279 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| regional consistency | prescription_items | 7 | 3,690.117632 | 13,335.064607 | True | False | metric units/month | Sensitivity range, not sampling confidence interval |
| robust trend | ingredient_cost_per_item_gbp | 1 | -0.048418 | -0.048418 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| robust trend | net_ingredient_cost_gbp | 1 | -238,635.842500 | -238,635.842500 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| robust trend | prescription_items | 1 | 47,729.625000 | 47,729.625000 | True | False | metric units/month | Sensitivity range, not sampling confidence interval |
| trend specification | ingredient_cost_per_item_gbp | 5 | -0.045833 | -0.039432 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| trend specification | net_ingredient_cost_gbp | 5 | -203,156.376875 | -167,339.592138 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| trend specification | prescription_items | 5 | 45,642.274306 | 46,650.037066 | True | False | metric units/month | Sensitivity range, not sampling confidence interval |

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
