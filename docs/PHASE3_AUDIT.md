# Phase 3 final audit

Overall pass: **True**. All analyses use verified observed data; no forecast models trained.

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
Original source guard remains valid. Phase 2 fact has **3920** rows;
the diagnostic grid has **4284** cells, of which
**364** remain absent. Prior database file and all protected
source/report/SQL/doc files unchanged: **True**.
FORECASTING_READINESS.md is explicitly updated; its Phase 2 content remains before the Phase 3 appendix.
README and pipeline entrypoint changes preserve earlier modes. No mixed-unit quantity total exists.

## Created or updated implementation files

- `README.md`
- `config/kernels/pharma-phase3/kernel.json`
- `docs/FORECASTING_READINESS.md`
- `docs/PHASE3_AUDIT.md`
- `docs/PHASE3_BUSINESS_INSIGHTS.md`
- `docs/PHASE3_METHODOLOGY.md`
- `docs/PHASE3_STATISTICAL_FINDINGS.md`
- `notebooks/02_advanced_eda.ipynb`
- `notebooks/03_statistical_intelligence.ipynb`
- `run_pipeline.py`
- `src/anomaly_diagnostics.py`
- `src/cost_diagnostics.py`
- `src/phase3_notebooks.py`
- `src/phase3_pipeline.py`
- `src/phase3_reports.py`
- `src/phase3_visualizations.py`
- `src/robustness_analysis.py`
- `src/seasonality_analysis.py`
- `src/statistical_analysis.py`
- `src/trend_analysis.py`
- `tests/test_phase3_costs.py`
- `tests/test_phase3_robustness.py`
- `tests/test_phase3_seasonality.py`
- `tests/test_phase3_statistics.py`
- `tests/test_phase3_trends.py`

## Tables and chart inventory

| table (CSV and Parquet) | rows | columns |
|---|---|---|
| descriptive_statistics | 432 | 18 |
| growth_rate_distributions | 864 | 19 |
| trend_summary | 3 | 20 |
| regional_trend_summary | 21 | 22 |
| presentation_trend_summary | 51 | 23 |
| seasonality_summary | 3 | 11 |
| monthly_seasonal_indices | 108 | 8 |
| autocorrelation_diagnostics | 75 | 5 |
| stl_components | 108 | 6 |
| regional_statistical_comparisons | 63 | 10 |
| cost_per_item_trends | 900 | 10 |
| presentation_cost_change_contributions | 17 | 20 |
| regional_cost_change_contributions | 7 | 19 |
| cost_decomposition_diagnostics | 3 | 11 |
| anomaly_diagnostics | 2102 | 22 |
| extreme_value_review_phase3 | 161 | 22 |
| robustness_summary | 22 | 9 |
| sensitivity_results | 59 | 10 |
| diagnostic_excluded_rows | 5 | 28 |
| forecasting_diagnostics | 94 | 31 |

All tables exist as CSV and Parquet under outputs/phase3/tables. Row counts, schemas and hashes are
recorded in final_audit.json. All required eighteen high-resolution PNG charts exist:

- `outputs/phase3/charts/01_national_items.png`
- `outputs/phase3/charts/02_national_nic.png`
- `outputs/phase3/charts/03_cost_per_item.png`
- `outputs/phase3/charts/04_regional_indexed_growth.png`
- `outputs/phase3/charts/05_regional_growth_distribution.png`
- `outputs/phase3/charts/06_presentation_item_contributions.png`
- `outputs/phase3/charts/07_presentation_mix.png`
- `outputs/phase3/charts/08_monthly_seasonal_profile.png`
- `outputs/phase3/charts/09_stl_items.png`
- `outputs/phase3/charts/10_autocorrelation.png`
- `outputs/phase3/charts/11_nic_decomposition.png`
- `outputs/phase3/charts/12_presentation_cost_per_item.png`
- `outputs/phase3/charts/13_regional_cost_per_item.png`
- `outputs/phase3/charts/14_anomaly_timeline.png`
- `outputs/phase3/charts/15_extreme_value_distribution.png`
- `outputs/phase3/charts/16_trend_sensitivity.png`
- `outputs/phase3/charts/17_coverage_volatility.png`
- `outputs/phase3/charts/18_forecasting_readiness.png`

## Notebook execution

| notebook | code_cells | unexecuted_code_cells | error_outputs |
|---|---|---|---|
| notebooks/02_advanced_eda.ipynb | 6 | 0 | 0 |
| notebooks/03_statistical_intelligence.ipynb | 6 | 0 | 0 |

Notebooks import production functions and read validated exports, without replicating the pipeline.

## Methods, assumptions and checks

Calendar-aware summaries/growth, weighted ratios, linear/log OLS with conditional HAC intervals,
Theil–Sen, descriptive Kendall tau, month indicators and bandwidth sensitivity, annual profiles,
calendar-day sensitivity, raw/detrended ACF, robust STL, paired regional contrasts, symmetric exact
three-factor decomposition, independent Phase 2 two-factor checks, within-series MAD/rolling/MoM
review, cohort/aggregation/exclusion sensitivities and forecast readiness diagnostics. Assumptions,
formulas, skip rules, heuristic classification priority and noncausal limits are in PHASE3_METHODOLOGY.md.

All **161** original metric flags retained with values and
calendar neighbors. Anomaly categories are retrospective hypotheses, not confirmed source errors.
Missingness preserved: **True**. Maximum three-factor residual:
**GBP 2.23517417908e-08**, well below GBP0.01.

## Findings and sensitivity results

National item OLS slope **46,650.037066 items/month**; 2025 item growth
**7.579853%**, NIC change **-39.934224%**.
Shapley volume/mix/within-presentation effects **GBP +7,478,389.50 /
+1,254,765.30 / -59,243,626.55**.
All seven regions grow. Removing largest presentation leaves **6.576248%**
item growth. All numerical statements are derived from exported analytical results and verified
Phase 2 source tables. Detailed nine findings and sensitivity tables: PHASE3_BUSINESS_INSIGHTS.md.

## Tests and reproducibility

Complete Phase 1–3 suite: **74 tests**, **0 failures,
**0 errors**, **0 skipped**. Evidence: all_tests.xml
and test_execution.log. Known synthetic fixtures test effects, gaps, ordering, ratios, zero MAD,
short history, grouped units, decomposition reversibility and identities. Integration checks verify
missingness, all original flags, input immutability, schemas, PNG dimensions and two reruns.
All twenty CSV and twenty Parquet outputs byte-identical on two complete executions:
**True**. Notebook execution metadata is nondeterministic by design;
notebook source cells and analytical table values are deterministic. Source data remain untouched.
Independent fact-based headline and original-flag checks: **13 passed**,
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
.\.venv\Scripts\python.exe run_pipeline.py --phase 3
.\.venv\Scripts\python.exe -m src.phase3_pipeline --audit
```
