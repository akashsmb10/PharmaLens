# Phase 5 final audit

Overall pass: **True**. Phase 1–4 baseline: **124 passed**, zero failures;
baseline_tests.xml is separate from the final suite. Existing settings.yaml is absent. Existing pinned
environment reused with no dependencies installed. Read-only Phase 2/3 input checks and all Phase 4
export/frozen-decision hashes are verified. input_inventory.json records actual schemas and inspected files.
The Phase 3 guard excludes later-phase reports from its prior-input inventory; original hashes remain valid.
No earlier reports, frozen forecasts or model-selection decisions are rewritten.

## Implementation inventory

- `README.md`
- `config/decision_intelligence.yaml`
- `docs/PHASE5_AUDIT.md`
- `docs/PHASE5_BUSINESS_RECOMMENDATIONS.md`
- `docs/PHASE5_DECISION_FRAMEWORK.md`
- `docs/PHASE5_EXECUTIVE_SUMMARY.md`
- `docs/PHASE5_SCENARIO_METHODOLOGY.md`
- `notebooks/06_decision_intelligence.ipynb`
- `notebooks/07_scenario_analysis.ipynb`
- `run_pipeline.py`
- `src/decision_features.py`
- `src/decision_recommendations.py`
- `src/decision_validation.py`
- `src/forecast_risk.py`
- `src/phase3_pipeline.py`
- `src/phase5_notebooks.py`
- `src/phase5_pipeline.py`
- `src/phase5_reports.py`
- `src/phase5_visualizations.py`
- `src/presentation_intelligence.py`
- `src/prioritization.py`
- `src/regional_intelligence.py`
- `src/scenario_engine.py`
- `tests/conftest.py`
- `tests/test_phase5_features.py`
- `tests/test_phase5_forecast_risk.py`
- `tests/test_phase5_prioritization.py`
- `tests/test_phase5_recommendations.py`
- `tests/test_phase5_reconciliation.py`
- `tests/test_phase5_reproducibility.py`
- `tests/test_phase5_scenarios.py`

## Features, scoring and sensitivity

Feature grains: seven regions, 17 presentations, 119 region/presentation cells, one national row.
The absence-only 364-row export is unioned with 3,920 observed rows to form the 4,284-cell diagnostic grid.
Share/ratio definitions, complete-year changes, forecast-subset scope and unique joins are in
PHASE5_DECISION_FRAMEWORK.md and the two exported dictionaries. Original and Phase 3 flag counts remain distinct.
Missing activity is never zero-filled. Priorities use retained percentile components and policy weights
{'activity': 0.25, 'change': 0.2, 'cost': 0.2, 'forecast': 0.2, 'quality': 0.15}; missing required dimensions leave explicit unscored status. Initial tiers are
70/40; ranks do not assert commercial value.
Weight, leave-out, threshold and min-max alternatives are exported with rank/tier changes and overlap.

| region_name | composite_score | rank | monitoring_tier |
|---|---|---|---|
| NORTH EAST AND YORKSHIRE | 63.333333 | 1 | Moderate review priority |
| SOUTH EAST | 57.500000 | 2 | Moderate review priority |
| NORTH WEST | 55.000000 | 3 | Moderate review priority |
| MIDLANDS | 51.666667 | 4 | Moderate review priority |
| LONDON | 46.666667 | 5 | Moderate review priority |
| SOUTH WEST | 45.000000 | 6 | Moderate review priority |
| EAST OF ENGLAND | 30.833333 | 7 | Routine monitoring |

| aggregation_level | scheme | normalization | paired_scored_entities | spearman_rank_correlation | top_k | top_priority_overlap_pct | tier_changes | newly_scored_entities | evidence_class |
|---|---|---|---|---|---|---|---|---|---|
| regional | default | percentile | 7 | 1.000000 | 3 | 100.000000 | 0 | 0 | Exploratory signal |
| regional | default | minmax | 7 | 0.821429 | 3 | 66.666667 | 1 | 0 | Exploratory signal |
| regional | equal | percentile | 7 | 0.882919 | 3 | 100.000000 | 0 | 0 | Exploratory signal |
| regional | activity_heavy | percentile | 7 | 0.720750 | 3 | 66.666667 | 2 | 0 | Exploratory signal |
| regional | forecast_heavy | percentile | 7 | 0.378394 | 3 | 66.666667 | 1 | 0 | Exploratory signal |
| regional | quality_heavy | percentile | 7 | 0.200033 | 3 | 66.666667 | 3 | 0 | Exploratory signal |
| regional | leave_out_activity | percentile | 7 | 0.500000 | 3 | 66.666667 | 0 | 0 | Exploratory signal |
| regional | leave_out_change | percentile | 7 | 0.607143 | 3 | 66.666667 | 0 | 0 | Exploratory signal |
| regional | leave_out_cost | percentile | 7 | 0.857143 | 3 | 66.666667 | 2 | 0 | Exploratory signal |
| regional | leave_out_forecast | percentile | 7 | 0.857143 | 3 | 66.666667 | 2 | 0 | Exploratory signal |
| regional | leave_out_quality | percentile | 7 | 0.821429 | 3 | 66.666667 | 1 | 0 | Exploratory signal |
| presentation | default | percentile | 4 | 1.000000 | 3 | 100.000000 | 0 | 0 | Exploratory signal |
| presentation | default | minmax | 4 | 0.400000 | 3 | 100.000000 | 4 | 0 | Exploratory signal |
| presentation | equal | percentile | 4 | 1.000000 | 3 | 100.000000 | 1 | 0 | Exploratory signal |
| presentation | activity_heavy | percentile | 4 | 1.000000 | 3 | 100.000000 | 1 | 0 | Exploratory signal |
| presentation | forecast_heavy | percentile | 4 | 1.000000 | 3 | 100.000000 | 2 | 0 | Exploratory signal |
| presentation | quality_heavy | percentile | 4 | 0.400000 | 3 | 66.666667 | 3 | 0 | Exploratory signal |
| presentation | leave_out_activity | percentile | 4 | 1.000000 | 3 | 100.000000 | 2 | 0 | Exploratory signal |
| presentation | leave_out_change | percentile | 4 | 1.000000 | 3 | 100.000000 | 1 | 0 | Exploratory signal |
| presentation | leave_out_cost | percentile | 4 | 1.000000 | 3 | 100.000000 | 1 | 0 | Exploratory signal |
| presentation | leave_out_forecast | percentile | 4 | 0.800000 | 3 | 0.000000 | 13 | 13 | Exploratory signal |
| presentation | leave_out_quality | percentile | 4 | 1.000000 | 3 | 100.000000 | 1 | 0 | Exploratory signal |
| region_presentation | default | percentile | 28 | 1.000000 | 3 | 100.000000 | 0 | 0 | Exploratory signal |
| region_presentation | default | minmax | 28 | 0.626710 | 3 | 0.000000 | 28 | 0 | Exploratory signal |
| region_presentation | equal | percentile | 28 | 0.992337 | 3 | 100.000000 | 1 | 0 | Exploratory signal |
| region_presentation | activity_heavy | percentile | 28 | 0.926108 | 3 | 66.666667 | 8 | 0 | Exploratory signal |
| region_presentation | forecast_heavy | percentile | 28 | 0.933771 | 3 | 66.666667 | 10 | 0 | Exploratory signal |
| region_presentation | quality_heavy | percentile | 28 | 0.711002 | 3 | 33.333333 | 6 | 0 | Exploratory signal |
| region_presentation | leave_out_activity | percentile | 28 | 0.973727 | 3 | 66.666667 | 10 | 0 | Exploratory signal |
| region_presentation | leave_out_change | percentile | 28 | 0.922824 | 3 | 100.000000 | 4 | 0 | Exploratory signal |
| region_presentation | leave_out_cost | percentile | 28 | 0.986316 | 3 | 66.666667 | 5 | 0 | Exploratory signal |
| region_presentation | leave_out_forecast | percentile | 28 | 0.735632 | 3 | 0.000000 | 68 | 66 | Exploratory signal |
| region_presentation | leave_out_quality | percentile | 28 | 0.972085 | 3 | 100.000000 | 6 | 0 | Exploratory signal |

## Frozen forecast risk and hierarchy

Selected-series profiles recompute origin/horizon errors using the frozen selected variant; paired naive
comparisons share forecast cells. No fitting or reselection occurs. Absolute, scaled and volume-relative
errors, signed bias, sample counts, selected/all-family failures and interval-unavailable status remain explicit.
Hierarchy gaps compare direct national with all seven regions. Forecasts are unchanged and unreconciled.
See the executive summary and forecast_risk_register for actual observed risk classes and review rules.

## Scenarios, recommendations and dashboard products

Six scenario families use observed 2025 or frozen retrospective forecast baselines, explicit fixed cost
assumptions, nonnegative counts and item-conserving mix changes. Accounting break-even is independently
checked. Every scenario is hypothetical, without probabilities or observed-benefit claims.
All recommendations are deterministic, traceable to a unique source row/metric, with evidence class,
proposed analyst action and limitation. Dashboard products retain business keys, units and null/status semantics.

| table | rows | business_key | CSV/Parquet byte hashes recorded |
|---|---|---|---|
| regional_decision_features | 7 | aggregation_level;entity_id | True |
| presentation_decision_features | 17 | aggregation_level;entity_id | True |
| region_presentation_decision_features | 119 | aggregation_level;entity_id | True |
| national_decision_summary | 1 | aggregation_level;entity_id | True |
| decision_feature_dictionary | 252 | grain;feature | True |
| regional_monitoring_profiles | 7 | aggregation_level;entity_id | True |
| regional_growth_risk_matrix | 7 | entity_id | True |
| presentation_monitoring_profiles | 17 | aggregation_level;entity_id | True |
| presentation_change_contributions | 17 | entity_id | True |
| presentation_concentration_risk | 17 | entity_id | True |
| forecast_reliability_profiles | 36 | series_id | True |
| forecast_risk_register | 36 | series_id | True |
| forecast_horizon_risk | 216 | series_id;split_type;horizon | True |
| forecast_hierarchy_gap_analysis | 33 | context;origin_date;forecast_month;horizon | True |
| regional_priority_scores | 7 | aggregation_level;entity_id | True |
| presentation_priority_scores | 17 | aggregation_level;entity_id | True |
| region_presentation_priority_scores | 119 | aggregation_level;entity_id | True |
| priority_sensitivity_results | 1573 | aggregation_level;entity_id;scheme;normalization | True |
| rank_stability_summary | 33 | aggregation_level;scheme;normalization | True |
| priority_threshold_sensitivity | 429 | aggregation_level;entity_id;high_threshold;moderate_threshold | True |
| priority_rank_instability | 143 | aggregation_level;entity_id | True |
| monitoring_priority_register | 143 | aggregation_level;entity_id | True |
| scenario_assumptions | 88 | scenario_id | True |
| scenario_results | 88 | scenario_id | True |
| scenario_comparisons | 88 | scenario_id | True |
| presentation_mix_scenarios | 51 | scenario_id;presentation_key | True |
| scenario_sensitivity | 88 | scenario_id | True |
| accounting_break_even_analysis | 5 | volume_change_pct | True |
| executive_recommendations | 225 | recommendation_id | True |
| decision_action_register | 225 | recommendation_id | True |
| executive_kpi_summary | 17 | metric | True |
| regional_dashboard | 7 | aggregation_level;entity_id | True |
| presentation_dashboard | 17 | aggregation_level;entity_id | True |
| region_presentation_dashboard | 119 | aggregation_level;entity_id | True |
| forecast_dashboard | 108 | series_id;forecast_month;horizon | True |
| forecast_risk_dashboard | 36 | series_id | True |
| scenario_dashboard | 88 | scenario_id | True |
| priority_dashboard | 143 | aggregation_level;entity_id | True |
| recommendations_dashboard | 225 | recommendation_id | True |
| data_quality_dashboard | 144 | aggregation_level;entity_id | True |
| decision_evidence_register | 54 | output_table;evidence_class | True |
| dashboard_data_dictionary | 399 | output_table;field | True |

## Chart inventory

- `outputs/phase5/charts/01_regional_priority_matrix.png`
- `outputs/phase5/charts/02_presentation_priority.png`
- `outputs/phase5/charts/03_component_scores.png`
- `outputs/phase5/charts/04_priority_sensitivity.png`
- `outputs/phase5/charts/05_rank_stability.png`
- `outputs/phase5/charts/06_growth_forecast_risk.png`
- `outputs/phase5/charts/07_presentation_concentration_growth.png`
- `outputs/phase5/charts/08_nic_per_item_change.png`
- `outputs/phase5/charts/09_regional_reliability.png`
- `outputs/phase5/charts/10_horizon_reliability.png`
- `outputs/phase5/charts/11_forecast_bias.png`
- `outputs/phase5/charts/12_hierarchy_gaps.png`
- `outputs/phase5/charts/13_volume_sensitivity.png`
- `outputs/phase5/charts/14_cost_sensitivity.png`
- `outputs/phase5/charts/15_two_way_sensitivity.png`
- `outputs/phase5/charts/16_mix_sensitivity.png`
- `outputs/phase5/charts/17_accounting_break_even.png`
- `outputs/phase5/charts/18_recommendation_priorities.png`

## Executed notebooks and tests

| notebook | code_cells | unexecuted_code_cells | error_outputs |
|---|---|---|---|
| notebooks/06_decision_intelligence.ipynb | 6 | 0 | 0 |
| notebooks/07_scenario_analysis.ipynb | 6 | 0 | 0 |

Full suite: **197 tests**, **0 failures**,
**0 errors**, **0 skipped**. Evidence:
outputs/phase5/validation/all_tests.xml and test_execution.log. Tests include deterministic accounting
fixtures, impossible mix inputs, missing-component/tie/weight behavior, future-data cutoffs, source joins,
rank sensitivity, rule traceability, schemas, chart and notebook artifacts, and full earlier-phase regression.

## Independent reconciliation, reproducibility and preservation

**2970 independent checks passed**, **0 failed**.
Separate loops/algebra reconstruct history, shares, ratios, forecast errors, weighted arithmetic/ranks,
scenario results, mix conservation, break-even, hierarchy gaps, dashboard counts and recommendation references.
Evidence: decision_reconciliation.csv with expected/observed/difference/tolerance/status.
Two complete executions have byte-identical CSV/Parquet exports: **True**;
reproducibility.json records both inventories. Notebook runtime metadata is not claimed byte-identical.
Protected prior artifacts: **347**, unchanged: **True**.
Metadata records Python/dependency versions, original hashes, configuration, weights and assumptions.

## Limitations and Phase 6

Subjective policy weights and thresholds; incomplete applicability; 36 months; overlapping short forecast
support; sparse eligible subset; no calibrated intervals; retrospective publication-vintage limitations;
fixed accounting assumptions; no population, case-mix, clinical intervention or manufacturer financial data.
Phase 6 should expose component scores, policy sensitivity, unscored entities, source evidence, origin/horizon
counts and unavailable uncertainty. Visually separate historical observations, model results and hypothetical
scenarios. No dashboard, UI or PBIX is implemented here. No critical validation remains unresolved if pass=True.

## Windows PowerShell reproduction

```powershell
Set-Location '<PROJECT_ROOT>'
.\.venv\Scripts\python.exe run_pipeline.py --phase 5
.\.venv\Scripts\python.exe -m src.phase5_pipeline --audit
```
