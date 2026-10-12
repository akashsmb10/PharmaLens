# Initial data assessment

Generated from the executed Phase 1 pipeline. Data mode: **observed**.

The source extract contains **50,456 rows and 27 source columns**.
The monthly table contains **3,920 rows and 13 columns**,
covering **2023-01-01 to 2025-12-01**, with **36 months**,
**17 presentations**, **1 chemical category** and
**7 geographic codes**. See geographic_coverage.csv for actual region labels,
including any unknown/special codes. Product presentation is a formulation/strength identifier, not a sales SKU.

Required processed-column missing cells: **0**.
Source missing cells: **35470**, including optional administrative fields.
Audit error gate passed: **True**. All anomalies are retained.

## Measured findings

- structural_schema_absence: 18,250. Optional field did not exist in earlier monthly resources; valid schema exception
- optional_missing_values: 17,220. Optional source fields may be absent; unknown suppliers are not imputed
- missing_series_months: 292. May reflect launches, discontinuations or no dispensing; absence is not automatically zero
- extreme_observations: 161. Three-IQR fences within each monthly series/metric; review, do not remove

Source schema variations: [26, 27] columns per monthly response; the detailed table retains the union.
PHARMACY_ADVANCED_SERVICE is absent before February 2024 and has the observed label Not applicable thereafter in this selected extract. Its earlier nulls are structural schema absence.


## Supported questions

Observed data supports describing monthly community dispensing volumes and ingredient costs for this
selected chemical, presentation mix, regional variation and missing-series patterns. Later phases can
evaluate forecasts of prescription items using chronological holdouts and assess cost-per-item changes.
Quantity is meaningful only within a consistent presentation and unit; items are not patient counts.

## Unsupported questions and limitations

No company sales revenue, realized selling price, margin, sales representatives, promotion, physician
engagement, hospital/private market, patient adherence or India market estimates are available. NIC is
NHS ingredient cost and excludes commercial rebates/margins; dividing NIC by quantity is an aggregate
cost ratio, not a transaction selling price. This deliberately bounded atorvastatin extract cannot establish
whole-market shares or effects of interventions. Dispensing region is not necessarily patient residence.
Missing series months may reflect lifecycle or non-dispensing; do not impute zero without source review.
STP/ICB administrative boundaries can change; the region aggregation reduces but does not prove away
geographic discontinuities. Monthly PCA is management information, not the annual official statistic.

Synthetic commercial scenarios may be added separately in later phases with explicit synthetic columns,
assumptions and lineage. No synthetic revenue has been added to this observed table.

## Outputs

See outputs/validation for checks, column profiles, missing periods, extreme observations and sample
records. See outputs/tables for descriptive statistics, product distribution and geographic coverage.
The chart is an initial descriptive inspection, with no model fit or forecast. The DuckDB table is only
a staging representation of the validated monthly data.
