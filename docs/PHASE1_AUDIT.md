# Final Phase 1 audit

Executed at 2026-10-11T09:37:02.062778+00:00. Mode: observed.

Overall pass: **True**. Source: NHSBSA PCA monthly administrative data, OGL v3.0.
Source shape: 50,456 × 27. Monthly shape: 3,920 × 13.
Coverage: 2023-01-01 to 2025-12-01 (36 months), 17 presentations, 7 regions.

Tests: 19 executed; 0 failures; 0 errors; 0 skipped.
Notebook: 7 code cells executed, 0 error outputs.
Verified raw pages: 36. Repeated processed CSV SHA-256: `d4522179e99cd1f368191a61461aee0e20f3af49c6287e976b86b50757c8be8a`.
Dependency consistency exit code: 0. Missing required paths: [].

## Data findings

- required_columns: 0 (error). []
- data_type_correctness: 0 (error). []
- total_records: 0 (info). 50456 source rows, 3920 monthly rows
- empty_data: 0 (error). A successful acquisition must be nonempty
- required_missing_values: 0 (error). Required keys, labels and metrics must be present
- monthly_required_missing_values: 0 (error). Aggregated keys/labels/measures must be populated
- structural_schema_absence: 18,250 (info). Optional field did not exist in earlier monthly resources; valid schema exception
- optional_missing_values: 17,220 (warning). Optional source fields may be absent; unknown suppliers are not imputed
- duplicate_source_rows: 0 (error). Count includes all members of duplicate groups
- duplicate_source_business_keys: 0 (error). Candidate full-dimensional source key; validate before interpreting repeated simpler product/month keys
- duplicate_monthly_business_keys: 0 (error). ['month', 'product_code', 'region_code', 'unit_of_measure']
- invalid_dates: 0 (error). YEAR_MONTH must parse to a calendar month start
- invalid_monthly_dates: 0 (error). Aggregated dates must also be calendar month starts
- dates_outside_extract: 0 (error). Fixed configured extraction window
- invalid_numeric_items: 0 (error). Missing, unparseable or non-finite values
- negative_items: 0 (error). Negative cost requires source review; negative volume violates the intended demand use case
- zero_items: 0 (info). Valid business exception retained; zero is not missing
- invalid_numeric_total_quantity: 0 (error). Missing, unparseable or non-finite values
- negative_total_quantity: 0 (error). Negative cost requires source review; negative volume violates the intended demand use case
- zero_total_quantity: 0 (info). Valid business exception retained; zero is not missing
- invalid_numeric_nic_gbp: 0 (error). Missing, unparseable or non-finite values
- negative_nic_gbp: 0 (warning). Negative cost requires source review; negative volume violates the intended demand use case
- zero_nic_gbp: 0 (info). Valid business exception retained; zero is not missing
- fractional_prescription_items: 0 (error). Prescription item counts must be integral
- missing_global_months: 0 (error). []
- missing_series_months: 292 (warning). May reflect launches, discontinuations or no dispensing; absence is not automatically zero
- extreme_observations: 161 (warning). Three-IQR fences within each monthly series/metric; review, do not remove
- unexpected_origin_categories: 0 (error). Allowed observed_nhsbsa or synthetic_demo
- unexpected_chemical_category: 0 (error). Must match configured acquisition filter
- inconsistent_product_identifiers: 0 (error). Expected 15-character alphanumeric BNF presentation code
- product_code_name_changes: 0 (warning). Names can evolve; identifiers remain the analytical key
- geographic_inconsistencies: 0 (error). Missing/blank region identifiers
- unexpected_geographic_categories: 0 (warning). Special/unknown source codes require interpretation; retained
- region_code_name_changes: 0 (warning). Review administrative naming changes, including STP-to-ICB transitions
- product_unit_changes: 0 (warning). Unit is included in the monthly key to avoid mixing quantities
- aggregation_reconciliation_items: 0 (error). Absolute source-minus-processed total difference = 0.000000
- aggregation_reconciliation_total_quantity: 0 (error). Absolute source-minus-processed total difference = 0.000000
- aggregation_reconciliation_nic_gbp: 0 (error). Absolute source-minus-processed total difference = 0.000000
- data_grain_violations: 0 (error). Exactly one row per month/presentation/region/unit
- revenue_arithmetic: 0 (not_applicable). No revenue or transaction unit price exists. NIC is NHS ingredient cost, not company revenue.

## Remaining interpretation work

Review incomplete presentation-region series, extreme observations and any name/geography changes before
forecasting. Warnings are retained business-review findings, not automatically removed records.
One chemical, England community dispensing and NHS ingredient cost do not establish manufacturer revenue
or India market demand. Raw preparation-class codes have not been decoded without source reference.
OpenPrescribing acquisition was blocked (403); the official NHSBSA dataset was acquired instead.
The initial metadata access date is known, but its exact download time was not recorded. Individual
pipeline-acquired pages have exact UTC receipts. No forecasting, synthetic revenue or final dashboard
was implemented. See the source evaluation and initial assessment for analytical limits.

## Created files

- `.gitignore`
- `README.md`
- `config/dataset.json`
- `config/kernels/pharma-phase1/kernel.json`
- `data/processed/acquisition_manifest.json`
- `data/processed/monthly_prescribing.csv`
- `data/processed/monthly_prescribing.parquet`
- `data/processed/pharma.duckdb`
- `data/processed/source_rows.parquet`
- `docs/DATA_DICTIONARY.md`
- `docs/DATA_SOURCE_EVALUATION.md`
- `docs/INITIAL_DATA_ASSESSMENT.md`
- `docs/PHASE1_AUDIT.md`
- `notebooks/01_data_understanding.ipynb`
- `outputs/charts/monthly_items.png`
- `outputs/tables/descriptive_statistics.csv`
- `outputs/tables/geographic_coverage.csv`
- `outputs/tables/monthly_totals.csv`
- `outputs/tables/product_distribution.csv`
- `outputs/validation/column_profile.csv`
- `outputs/validation/dependency_check.log`
- `outputs/validation/extreme_observations.csv`
- `outputs/validation/final_audit.json`
- `outputs/validation/finding_samples.csv`
- `outputs/validation/missing_series_periods.csv`
- `outputs/validation/notebook_execution.json`
- `outputs/validation/quality_checks.csv`
- `outputs/validation/quality_report.json`
- `pytest.ini`
- `requirements-lock.txt`
- `requirements.txt`
- `run_pipeline.py`
- `src/__init__.py`
- `src/common.py`
- `src/documentation.py`
- `src/final_audit.py`
- `src/ingest.py`
- `src/inspect_data.py`
- `src/notebook_tools.py`
- `src/probe_source.py`
- `src/validate.py`
- `tests/test_foundation.py`
- `data/raw/`: 80 original API, receipt and research JSON files.
