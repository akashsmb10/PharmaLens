# Final Phase 2 audit

Executed at 2026-10-11T10:05:36.038322+00:00. Overall pass: **True**.

## Baseline and preserved artifacts

Phase 1 baseline: **19 tests passed**, with separate phase2_baseline_tests.xml evidence.
config/settings.yaml was absent; existing config/dataset.json was inspected and retained.
The protected Phase 1 raw snapshots, processed CSV/Parquet/manifest, notebook, original docs and
validation records retain identical hashes: **True**. Source guard tracks 98 files.
The existing DuckDB monthly_prescribing table is unchanged logically; the new phase2 schema is additive.

## Executed implementation

SQL order: 01_schema.sql, 02_data_quality.sql, 03_national_trends.sql, 04_regional_performance.sql, 05_presentation_performance.sql, 06_cost_analytics.sql, 08_series_coverage.sql, 07_region_presentation_intelligence.sql, 09_reporting_views.sql. All nine execute successfully; 08 coverage intentionally precedes
07 eligibility. Fact has 3,920 observed rows, dim_month 36, dim_region 7 and dim_presentation 17.
All six model-integrity checks pass and reporting-view contracts are documented in PHASE2_DATA_MODEL.md.
No synthetic production observations, missing-month zero filling, incompatible quantity totals, PBIX or
forecasting model is introduced. Cost is always net ingredient cost, never manufacturer revenue.

## Reporting outputs and row counts

| Export (CSV and Parquet) | Rows | View |
|---|---|---|
| national_monthly_trends | 36 | phase2.vw_national_monthly_kpis |
| national_annual_trends | 3 | phase2.vw_national_annual_kpis |
| regional_performance | 7 | phase2.vw_regional_performance |
| regional_monthly_trends | 252 | phase2.vw_regional_monthly_trends |
| regional_annual_trends | 21 | phase2.vw_regional_annual_trends |
| presentation_performance | 17 | phase2.vw_presentation_performance |
| presentation_monthly_trends | 612 | phase2.vw_presentation_monthly_trends |
| presentation_annual_trends | 51 | phase2.vw_presentation_annual_trends |
| presentation_concentration | 17 | phase2.vw_presentation_concentration |
| cost_analytics | 3920 | phase2.vw_cost_analytics |
| cost_change_decomposition | 37 | phase2.vw_cost_change_decomposition |
| region_presentation_summary | 119 | phase2.vw_region_presentation_summary |
| region_presentation_mix | 117 | phase2.vw_region_presentation_mix |
| forecast_candidate_series | 29 | phase2.vw_forecast_candidates |
| series_coverage | 119 | phase2.vw_series_coverage |
| missing_series_months | 364 | phase2.vw_missing_series_months |
| extreme_value_review | 161 | phase2.vw_extreme_value_review |
| threshold_sensitivity | 12 | phase2.vw_threshold_sensitivity |
| presentation_regional_costs | 117 | phase2.vw_presentation_regional_costs |
| model_quality_checks | 6 | phase2.vw_model_quality |

All CSV and Parquet files exist under outputs/tables. They are clean BI exports; database views remain
queryable after registered Python input relations are removed. Thirteen source-noted PNG charts exist
under outputs/charts/phase2, including all twelve requested figures and growth-versus-size comparison.

## Verified KPIs and data findings

- Total prescription items: **212,022,236** (Jan 2023–Dec 2025).
- Total net ingredient cost: **£336,940,603.13**.
- Original 292 observed-series missing months reproduced. Complete grid adds 72 never-observed
  applicability-unknown cells. Of 364 absent cells: 45 before first, 88 after last, 159 internal, 72 never observed.
- All 161 original extreme flags, including their values and keys, reproduce exactly within numeric tolerance.
  They cover 82 unique observed rows; flags are retained, not declared errors or causal effects.
- Supplier missingness 17,220 and pre-February-2024 structural field absence 18,250 reproduce.
- 94/119 candidate series have 36 observed months; 29 satisfy the default forecasting eligibility screen.
- Eight numerical findings are in PHASE2_BUSINESS_INSIGHTS.md. 10 machine-readable
  headline claims rechecked against unrounded SQL views; supporting tables are linked in each finding.

## Reconciliation, tests and reproducibility

SQL/Pandas checks: **3,980 passed**, **0 failed**.
Item counts compare exactly; GBP costs use absolute £0.01 tolerance, ratios/growth/shares use 1e-10.
All 37 monthly/annual exact two-factor cost decompositions pass;
maximum absolute residual **£2.60770320892e-08**.
Full pytest: **43 tests**, **0 failures**, **0 errors**, **0 skipped**.
Two complete pipeline executions produce byte-identical reporting CSV and Parquet files: **True**.
Counts and hashes are recorded in phase2_final_audit.json and phase2_exports.json.
An earlier rerun check caught Parquet differences in floating-point CV values despite identical CSVs.
Ordered standard-deviation aggregation and one-thread SQL execution resolved this. The historical
phase2_reproducibility_failure.json is retained as evidence; it does not represent the final audit status.

## Limits and Phase 3 recommendations

One chemical, England community dispensing, no population denominators or patient counts, and 36 months
of history limit inference. Absent-series causes and lifecycle are unknown. Ingredient cost is not final
NHS total cost or manufacturer revenue. Cost/item changes mix basic price, quantity/item and presentation
composition; the exact decomposition does not isolate causal prices or clinical substitution.
Per-100 native quantity is not dose-equivalent. Full-history screens and IQR flags must be recomputed
within training folds in a later forecast backtest. See FORECASTING_READINESS.md.
Next investigate item/cost/mix distributions, calendar effects, dated tariff references, and flagged/incomplete
series. Forecasting remains a later phase. No unresolved critical execution or validation failure remains
when the overall pass above is True.

## Exact implementation and output files

- `config/phase2.json`
- `src/sql_analytics.py`
- `src/reconcile_metrics.py`
- `src/phase2_visualizations.py`
- `src/phase2_reports.py`
- `src/phase2_pipeline.py`
- `tests/conftest.py`
- `tests/test_phase2_sql.py`
- `tests/test_phase2_metrics.py`
- `tests/test_phase2_coverage.py`
- `tests/test_phase2_reconciliation.py`
- `sql/01_schema.sql`
- `sql/02_data_quality.sql`
- `sql/03_national_trends.sql`
- `sql/04_regional_performance.sql`
- `sql/05_presentation_performance.sql`
- `sql/06_cost_analytics.sql`
- `sql/08_series_coverage.sql`
- `sql/07_region_presentation_intelligence.sql`
- `sql/09_reporting_views.sql`
- `docs/PHASE2_DATA_MODEL.md`
- `docs/METRIC_DEFINITIONS.md`
- `docs/PHASE2_DATA_QUALITY_REVIEW.md`
- `docs/PHASE2_BUSINESS_INSIGHTS.md`
- `docs/FORECASTING_READINESS.md`
- `docs/PHASE2_AUDIT.md`
- `outputs/tables/national_monthly_trends.csv`
- `outputs/tables/national_monthly_trends.parquet`
- `outputs/tables/national_annual_trends.csv`
- `outputs/tables/national_annual_trends.parquet`
- `outputs/tables/regional_performance.csv`
- `outputs/tables/regional_performance.parquet`
- `outputs/tables/regional_monthly_trends.csv`
- `outputs/tables/regional_monthly_trends.parquet`
- `outputs/tables/regional_annual_trends.csv`
- `outputs/tables/regional_annual_trends.parquet`
- `outputs/tables/presentation_performance.csv`
- `outputs/tables/presentation_performance.parquet`
- `outputs/tables/presentation_monthly_trends.csv`
- `outputs/tables/presentation_monthly_trends.parquet`
- `outputs/tables/presentation_annual_trends.csv`
- `outputs/tables/presentation_annual_trends.parquet`
- `outputs/tables/presentation_concentration.csv`
- `outputs/tables/presentation_concentration.parquet`
- `outputs/tables/cost_analytics.csv`
- `outputs/tables/cost_analytics.parquet`
- `outputs/tables/cost_change_decomposition.csv`
- `outputs/tables/cost_change_decomposition.parquet`
- `outputs/tables/region_presentation_summary.csv`
- `outputs/tables/region_presentation_summary.parquet`
- `outputs/tables/region_presentation_mix.csv`
- `outputs/tables/region_presentation_mix.parquet`
- `outputs/tables/forecast_candidate_series.csv`
- `outputs/tables/forecast_candidate_series.parquet`
- `outputs/tables/series_coverage.csv`
- `outputs/tables/series_coverage.parquet`
- `outputs/tables/missing_series_months.csv`
- `outputs/tables/missing_series_months.parquet`
- `outputs/tables/extreme_value_review.csv`
- `outputs/tables/extreme_value_review.parquet`
- `outputs/tables/threshold_sensitivity.csv`
- `outputs/tables/threshold_sensitivity.parquet`
- `outputs/tables/presentation_regional_costs.csv`
- `outputs/tables/presentation_regional_costs.parquet`
- `outputs/tables/model_quality_checks.csv`
- `outputs/tables/model_quality_checks.parquet`
- `outputs/charts/phase2/01_monthly_items.png`
- `outputs/charts/phase2/02_monthly_ingredient_cost.png`
- `outputs/charts/phase2/03_region_items.png`
- `outputs/charts/phase2/04_region_cost.png`
- `outputs/charts/phase2/05_top_presentation_items.png`
- `outputs/charts/phase2/06_top_presentation_cost.png`
- `outputs/charts/phase2/07_regional_yoy_growth.png`
- `outputs/charts/phase2/08_presentation_pareto.png`
- `outputs/charts/phase2/09_cost_per_item.png`
- `outputs/charts/phase2/10_activity_heatmap.png`
- `outputs/charts/phase2/11_series_coverage.png`
- `outputs/charts/phase2/12_extreme_value_review.png`
- `outputs/charts/phase2/13_regional_growth_vs_size.png`
- `outputs/validation/phase2_baseline_tests.xml`
- `outputs/validation/phase2_source_guard.json`
- `outputs/validation/phase2_phase1_verification.json`
- `outputs/validation/phase2_exports.json`
- `outputs/validation/sql_python_reconciliation.csv`
- `outputs/validation/phase2_reconciliation.json`
- `outputs/validation/phase2_business_claims.json`
- `outputs/validation/phase2_pipeline_summary.json`
- `outputs/validation/phase2_final_audit.json`
- `outputs/validation/phase2_tests.xml`
- `outputs/validation/phase2_test_execution.log`

Modified: run_pipeline.py (optional --phase 2), README.md (Phase 2 section). No dependency changes.
