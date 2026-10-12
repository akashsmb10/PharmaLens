# Phase 5 executive summary

Verified England atorvastatin extract: **212,022,236 items**, **GBP 336,940,603.13 NIC**,
January 2023–December 2025. 2025 versus 2024: items **7.5799%**, NIC **-39.9342%**,
weighted NIC/item **-44.1663%**. These are dispensing/accounting observations,
not patients, manufacturer revenue or India demand.

## Monitoring priorities

Policy weights 25/20/20/20/15%, five retained dimensions; score cutoffs 70/40. Top region:
**NORTH EAST AND YORKSHIRE**, score **63.3333**, tier
**Moderate review priority**. Ranking and high-review classification are distinct.

| region_name | historical_item_share_pct | item_growth_pct | holdout_MASE | composite_score | rank | monitoring_tier |
|---|---|---|---|---|---|---|
| NORTH EAST AND YORKSHIRE | 21.484424 | 11.094574 | 0.868110 | 63.333333 | 1 | Moderate review priority |
| SOUTH EAST | 11.800603 | 7.828730 | 1.027080 | 57.500000 | 2 | Moderate review priority |
| NORTH WEST | 13.161437 | 5.818157 | 0.928264 | 55.000000 | 3 | Moderate review priority |
| MIDLANDS | 19.331709 | 8.168225 | 0.889676 | 51.666667 | 4 | Moderate review priority |
| LONDON | 13.533512 | 3.362745 | 0.902890 | 46.666667 | 5 | Moderate review priority |
| SOUTH WEST | 9.277265 | 5.647721 | 0.916923 | 45.000000 | 6 | Moderate review priority |
| EAST OF ENGLAND | 11.411050 | 8.359882 | 0.866515 | 30.833333 | 7 | Routine monitoring |

All **17** presentations remain visible; **4** are scored,
**13** have insufficient required forecast evidence.
Presentation forecast metrics concern eligible regional subsets, not national presentation predictions.

| presentation_name | historical_item_share_pct | nic_per_item_change_pct | composite_score | rank | monitoring_tier | missing_components |
|---|---|---|---|---|---|---|
| Atorvastatin 80mg tablets | 14.354200 | -52.731370 | 66.250000 | 1 | Moderate review priority |  |
| Atorvastatin 40mg tablets | 25.810663 | -46.397170 | 56.145833 | 2 | Moderate review priority |  |
| Atorvastatin 20mg tablets | 50.453230 | -46.251142 | 51.041667 | 3 | Moderate review priority |  |
| Atorvastatin 10mg tablets | 9.042099 | -47.524631 | 41.406250 | 4 | Moderate review priority |  |
| Atorvastatin 20mg/5ml oral solution | 0.000180 | 15.245187 | Undefined | <NA> | Insufficient evidence | forecast |
| Atorvastatin 10mg/5ml oral solution | 0.000291 | 993.803775 | Undefined | <NA> | Insufficient evidence | forecast |
| Atorvastatin 30mg tablets | 0.022847 | -62.293131 | Undefined | <NA> | Insufficient evidence | forecast |
| Atorvastatin 60mg tablets | 0.060772 | -67.084667 | Undefined | <NA> | Insufficient evidence | forecast |
| Atorvastatin 20mg/5ml oral suspension | 0.000776 | 12.542956 | Undefined | <NA> | Insufficient evidence | forecast |
| Atorvastatin 10mg/5ml oral suspension | 0.000082 | 105.145983 | Undefined | <NA> | Insufficient evidence | forecast |
| Atorvastatin 20mg/5ml oral suspension sugar free | 0.011063 | 3.295256 | Undefined | <NA> | Insufficient evidence | forecast |
| Lipitor 10mg tablets | 0.043454 | -0.914517 | Undefined | <NA> | Insufficient evidence | forecast |
| Lipitor 20mg tablets | 0.081398 | -4.328822 | Undefined | <NA> | Insufficient evidence | forecast |
| Lipitor 40mg tablets | 0.045212 | -1.167786 | Undefined | <NA> | Insufficient evidence | forecast |
| Lipitor 80mg tablets | 0.015821 | -0.414664 | Undefined | <NA> | Insufficient evidence | forecast |
| Lipitor 10mg chewable tablets | 0.009955 | 25.480689 | Undefined | <NA> | Insufficient evidence | forecast |
| Lipitor 20mg chewable tablets | 0.047958 | -0.003006 | Undefined | <NA> | Insufficient evidence | forecast |

Regional alternative-policy Spearman correlations span **0.2000–0.8829**;
top-priority overlap spans **66.67–100.00%**.
Do not treat the displayed order as invariant. Per-entity movement and newly-scored leave-out cases are exported.

## Forecast risk and hierarchy

Frozen national **damped_ets** holdout MASE **0.888323**,
MAE **242,210.51**, RMSE **263,898.13**, WAPE **3.684100%**;
**15** overlapping forecast cells. Paired naive MASE improvement
**19.753991%**. Models are not retrained or reselected.
Regional MASE ranges **0.866515–1.027080**;
**15 of 36** selected series trigger configured manual-review rules.
All intervals remain unavailable; observed-error categories do not guarantee future reliability.

| region_name | holdout_n | holdout_MASE | holdout_WAPE | bias_pct | reliability_class | manual_review |
|---|---|---|---|---|---|---|
| LONDON | 15 | 0.902890 | 3.687662 | -2.544220 | Moderate observed error | True |
| SOUTH WEST | 15 | 0.916923 | 3.643091 | -1.055555 | Higher observed error | True |
| SOUTH EAST | 15 | 1.027080 | 3.863861 | -1.365184 | Higher observed error | True |
| MIDLANDS | 15 | 0.889676 | 3.866114 | -1.029919 | Moderate observed error | False |
| EAST OF ENGLAND | 15 | 0.866515 | 3.423911 | -1.157886 | Lower observed error | False |
| NORTH WEST | 15 | 0.928264 | 4.072453 | -1.033838 | Higher observed error | True |
| NORTH EAST AND YORKSHIRE | 15 | 0.868110 | 3.734525 | -1.024375 | Lower observed error | False |

| forecast_month | horizon | signed_gap_items | absolute_gap_pct | manual_review |
|---|---|---|---|---|
| 2026-01-01 00:00:00 | 1 | -23,753.408709 | 0.357186 | False |
| 2026-02-01 00:00:00 | 2 | -26,472.333258 | 0.396204 | False |
| 2026-03-01 00:00:00 | 3 | -29,222.306604 | 0.435361 | False |

These are separate unreconciled retrospective forecasts. Coherence is not accuracy.

## Hypothetical accounting sensitivities

At the 2025 fixed weighted NIC/item, +5% item volume gives **GBP 79,772,383.19** hypothetical
NIC, a **GBP 3,798,684.91** difference. +5% volume with −5% NIC/item gives
**GBP 75,783,764.03**, difference **GBP -189,934.25**.
To exactly offset +5% items requires **-4.761905%** NIC/item change.
These are assumptions/accounting equality, not savings, profitability or future price forecasts.

| scenario_id | hypothetical_items | hypothetical_nic_gbp | nic_difference_gbp |
|---|---|---|---|
| D_1 | 76,860,890.000000 | 76,006,325.90 | 32,627.62 |
| D_2 | 76,860,890.000000 | 76,038,953.52 | 65,255.24 |
| D_5 | 76,860,890.000000 | 76,136,836.39 | 163,138.11 |

Mix-only scenarios preserve total items across all 17 presentations. They are accounting simulations,
not clinical substitutions. Forecast planning scenarios use only frozen December-cutoff point forecasts.

## Proposed investigations and Phase 6

**225** traceable rule-based investigations are exported; no action or benefit
is claimed observed. Review major weighted NIC/item changes using dated basic-price/quantity records;
inspect source coverage; review high relative forecast error/bias; show ranking sensitivity before allocating
analyst time. Keep routine tracking separate from consequential forecast planning.
Phase 6 should provide filters, component scores, sensitivity views, exact source keys, cutoff/horizon/sample
counts, unknown missingness and explicit unsupported intervals. Separate observations, model results and
hypothetical scenarios. Keep unscored entities visible. No UI or PBIX is created in Phase 5.

Limits: 36 months, short correlated/overlapping model errors, incomplete applicability information,
sparse eligible subset, subjective weights/thresholds, fixed cost assumptions and unmodeled release vintage.
No population/case-mix, clinical or manufacturer financial inference.
