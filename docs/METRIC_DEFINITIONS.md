# Metric definitions and verified source semantics

Verified 11 October 2026 using the official [PCA December 2024 resource dictionary](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data/resource/7a543ac0-923f-4ea0-91c7-13c8a719398b)
and [NHSBSA methodology, June 2024](https://nhsbsa-opendata.s3.eu-west-2.amazonaws.com/pca/pca_background_info_methodology_v001.html).

| Concept | Verified meaning / mapping |
|---|---|
| Prescription items | Product occurrences on paper/electronic prescription forms. Source ITEMS → items → prescription_items. Not distinct forms or patients. |
| Total quantity | Prescribed quantity multiplied by item count. TOTAL_QUANTITY → total_quantity. Interpreted using the presentation's UNIT_OF_MEASURE. |
| Presentation | A particular medicine type, strength and formulation. BNF_PRESENTATION_CODE → product_code → presentation_code. |
| Quantity unit | Physical/form unit of one presentation quantity; this extract contains tablet and ml. Not necessarily packs. |
| Region | NHS England regional identifier; PCA concerns community dispensing in England. Region in this dispensing extract is not patient residence or an Indian territory. |

These field definitions come from the [official resource dictionary](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data/resource/7a543ac0-923f-4ea0-91c7-13c8a719398b).

NIC uses basic medicine prices and prescribed quantities in GBP. It precedes dispenser discounts and
omits other elements of final NHS cost, including contractor remuneration and patient charges. It does
not measure manufacturer receipts or profitability. Source NIC → nic_gbp → net_ingredient_cost_gbp.
Product attribution can depend on preparation-class methodology rather than confirmed actual supplier
dispensing; BNF presentation is not a manufacturer SKU. See [official methodology](https://nhsbsa-opendata.s3.eu-west-2.amazonaws.com/pca/pca_background_info_methodology_v001.html).

Monthly PCA is management information and includes only relevant community dispensing submitted
for reimbursement. It excludes private and in-hospital dispensing. See the [dataset scope and caveats](https://opendata.nhsbsa.net/dataset/prescription-cost-analysis-pca-monthly-data).

## Authoritative project calculations

SQL files define all reporting metrics. Python independently calculates selected controls only.

- Items: SUM(prescription_items), integer counts.
- Ingredient cost: SUM(net_ingredient_cost_gbp), source GBP cents in DECIMAL(20,2).
- Cost/item: SUM(cost) / NULLIF(SUM(items),0), never an unweighted average of row ratios.
- Quantity: SUM(total_quantity) only within identical presentation and unit. No national or regional
  total quantity is reported across heterogeneous presentations.
- Cost/native unit: SUM(cost)/NULLIF(SUM(quantity),0) within one presentation/unit. Per-100 native
  units simply multiplies by 100. It is neither dose-equivalent nor standardized to active ingredient mass.
  No DDD, mg-equivalent or pack conversion is attempted without a verified mapping.
- Shares: 100 × group's observed items or NIC / observed selected-chemical national total. These are
  within-extract shares, not whole pharmaceutical market share or commercial success.
- Growth: 100 × (current−baseline)/NULLIF(baseline,0). Calendar spines make missing months NULL;
  YoY uses the same calendar month. Undefined/zero-baseline growth is NULL. Annual growth requires
  twelve observed months in both years. No missing quantity or item observation is replaced by zero.
- Rolling averages: a complete 3/6/12-month window is required, otherwise NULL.
- Volatility: sample standard deviation / arithmetic mean of observed monthly item counts. This
  describes variability including trend; it is not forecast error or a detrended volatility estimate.
- Concentration: sum of squared item shares expressed as fractions (HHI 0–1); Pareto ordering uses
  descending items with presentation key as a deterministic tie breaker.
- Contributions: a group's change divided by national net change. Contributions can be negative or
  exceed 100%; they are undefined when national change is zero.

## Exact cost-change identity

For a national period, C=V×P with V=items and P=aggregate NIC/item.

Volume effect = (V1−V0)×(P1+P0)/2.

Aggregate unit-cost-and-mix effect = (P1−P0)×(V1+V0)/2.

Their sum equals C1−C0. The second effect contains presentation mix, quantity per item and basic-price
changes. A separate causal price/mix decomposition is not identifiable from these aggregate measures.
Zero item denominators give NULL effects, not invented prices. Reconciliation tolerance is £0.01;
floating ratios use absolute 1e-10, and item counts require exact equality.
