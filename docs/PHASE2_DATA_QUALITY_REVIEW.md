# Phase 2 data-quality review

The read-only Phase 1 verification reproduced its 19-test baseline and all original quality counts.
50,456 detailed rows aggregate to 3,920 monthly rows; the six SQL model integrity checks pass.
Original raw files, processed Parquet/CSV, Phase 1 reports, notebook and validation evidence retain
their hashes. The existing monthly_prescribing DuckDB table is logically unchanged.

## Missing-series investigation

The complete candidate grid contains 36 × 7 regions × 17 valid presentation/unit pairs = 4,284 cells.
Of these, 3,920 are observed and 364 are absent. This is a diagnostic grid, not a claim that
all combinations should exist. No physical observations are generated or zero-filled.

| Status | Absent months |
|---|---|
| after_last_observation_not_proven_discontinuation | 88 |
| before_first_observation_not_proven_launch | 45 |
| internal_gap_reporting_or_no_activity_unknown | 159 |
| never_observed_applicability_unknown | 72 |

Phase 1 examined only the 117 pairs observed at least once: its **292** absent months match the
sum of before-first, after-last and internal gaps. Adding two never-observed pairs adds **72** candidate
cells whose applicability is unknown. No pair is proven structurally inapplicable from these files.
Incompatible presentation/unit combinations are excluded by the dimension design, not treated as demand gaps.
Before/after observed activity is not evidence of launch or discontinuation. Internal gaps may represent
no dispensing, reporting omissions or other mechanisms; no reason is proven. The files cannot identify
genuine reporting gaps separately from nonactivity. All 119 candidate pairs have first/last date,
observed count, internal gaps, coverage, observed zeros and longest observed/missing runs exported.

Observed zero-item months: 0. Full 36-month coverage:
94 series. See series_coverage.csv and missing_series_months.csv.

## Extreme-value review

All **161** Phase 1 flags reproduce in SQL: {'nic_gbp': 65, 'total_quantity': 53, 'items': 43}.
They correspond to **82 distinct observed rows**;
one row may flag multiple measures. Method: three times the interquartile range outside Q1/Q3 within
one region/presentation/metric, at least 12 observed months, positive IQR. Original values are preserved.
No deletion or winsorization occurs. Neighboring observed values/dates and the calendar-month cost/item
change are exported. 11 flags have a missing interval between neighboring observed points.
61 flags coincide with an absolute calendar MoM cost/item change of at least 20% (a descriptive
review cutoff, not a price-change test). Coincidence does not identify cause; cost/item also contains
quantity/mix. Inspect monthly values and external dated basic-price data before explaining anomalies.

| presentation_name | region_name | metric_flags |
|---|---|---|
| Lipitor 80mg tablets | SOUTH WEST | 15 |
| Lipitor 80mg tablets | SOUTH EAST | 14 |
| Lipitor 10mg chewable tablets | MIDLANDS | 10 |
| Lipitor 10mg chewable tablets | NORTH EAST AND YORKSHIRE | 9 |
| Lipitor 10mg chewable tablets | NORTH WEST | 9 |

These are review findings, not proven data errors. Source numeric/date/key checks found no critical
errors. Rare/intermittent series can have legitimate extremes, and macro trends can also trigger IQR
flags; source confirmation is required. See extreme_value_review.csv and the phase2 extreme-review chart.

## Optional fields and schema evolution

Missing supplier labels: **17,220**, matching Phase 1's **17,220**.
No rows are dropped for these blanks, and no supplier is inferred. PHARMACY_ADVANCED_SERVICE is absent
in resources before February 2024: **18,250** structural nulls, matching **18,250**.
After introduction there are **0** nulls; this extract's populated label is Not applicable.
This is schema evolution, not missing item/quantity/cost data. The official [resource dictionary](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data/resource/7a543ac0-923f-4ea0-91c7-13c8a719398b)
defines the field as the advanced service through which an item was supplied.

## Blocking and retained findings

Fact/dimension key violations, orphan joins, row multiplication, non-integral items, changed protected
artifacts, reconciliation failures and invalid source lineage block production. Coverage gaps, IQR flags
and optional metadata absence remain visible. No causal or clinical interpretation is assigned.
