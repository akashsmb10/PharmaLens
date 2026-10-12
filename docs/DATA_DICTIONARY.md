# Data dictionary

Active executed mode: **observed**. Examples below come from the executed extract.

Raw JSON values are preserved byte-for-byte. In the normalized detailed table, identifiers use
pandas string dtype, blanks become missing, date becomes datetime64 and measures become float64.
Raw rows remain in data/raw; no abnormal observations are removed.

## Source columns and normalized mapping

| Source column → normalized field | Stored normalized dtype | Business meaning | Measured example | Allowed values | Missing meaning | Forecast use | Origin |
|---|---|---|---|---|---|---|---|
| YEAR_MONTH → YEAR_MONTH | string | Source calendar month YYYYMM, retained alongside parsed month | 202301 | Six digits representing a valid month | Required | Time index after date parsing | Observed NHSBSA |
| REGION_NAME → region_name | string | Dispensing region label, not patient residence | MIDLANDS | Source label paired with region code | Required | Display only | Observed NHSBSA |
| REGION_CODE → region_code | string | Dispensing administrative region identifier | Y60 | Source region code; special values require review | Required | Grouping | Observed NHSBSA |
| ICB_NAME → ICB_NAME | string | Integrated Care Board label | NHS COVENTRY AND WARWICKSHIRE INTEGRATED CARE BOARD | Source label | Unknown/unpopulated if missing | Display only | Observed NHSBSA |
| ICB_CODE → ICB_CODE | string | Integrated Care Board of dispensing contractor | QWU | Source ICB identifier | Unknown/unpopulated if missing | Grouping with geography review | Observed NHSBSA |
| DISPENSER_ACCOUNT_TYPE → DISPENSER_ACCOUNT_TYPE | string | Type of dispensing contractor account | English Pharmacy | Publisher categories; inspect observed distinct values | Unknown/unpopulated | Possible segmentation later | Observed NHSBSA |
| BNF_PRESENTATION_CODE → product_code | string | BNF product presentation identifier (formulation/strength) | 0212000B0AAAAAA | 15 uppercase alphanumeric characters | Required | Series grouping | Observed NHSBSA |
| BNF_PRESENTATION_NAME → product_name | string | Source medicine presentation label | Atorvastatin 10mg tablets | Source label; names may evolve | Required | Display only | Observed NHSBSA |
| SNOMED_CODE → SNOMED_CODE | string | Source SNOMED medicine concept identifier | 39695411000001103 | Identifier stored as string, never floating point | No source concept supplied | Grouping/reference only | Observed NHSBSA |
| SUPPLIER_NAME → SUPPLIER_NAME | string | Source supplier label where available | Viatris UK Healthcare Ltd | Source string | Unknown/not populated; not assumed generic | Not a sales-representative feature | Observed NHSBSA |
| UNIT_OF_MEASURE → unit_of_measure | string | Physical unit associated with total quantity | tablet | Source unit such as tablet or ml; see actual values | Required; quantity is uninterpretable without unit | Grouping to prevent mixed-unit totals | Observed NHSBSA |
| GENERIC_BNF_EQUIVALENT_CODE → GENERIC_BNF_EQUIVALENT_CODE | string | Generic equivalent BNF presentation identifier | 0212000B0AAAAAA | Source BNF identifier | No equivalent supplied | Reference or later grouping | Observed NHSBSA |
| GENERIC_BNF_EQUIVALENT_NAME → GENERIC_BNF_EQUIVALENT_NAME | string | Generic equivalent label | Atorvastatin 10mg tablets | Source label | No equivalent supplied | Display only | Observed NHSBSA |
| BNF_CHEMICAL_SUBSTANCE_CODE → chemical_code | string | BNF chemical identifier | 0212000B0 | 0212000B0 in this selected observed extract | Required | Category grouping | Observed NHSBSA |
| BNF_CHEMICAL_SUBSTANCE → chemical_name | string | BNF chemical label | Atorvastatin | Atorvastatin in selected observed extract | Required | Category grouping | Observed NHSBSA |
| BNF_PARAGRAPH_CODE → BNF_PARAGRAPH_CODE | string | BNF paragraph classification code | 021200 | Source BNF code | Classification absent | Later category grouping | Observed NHSBSA |
| BNF_PARAGRAPH → BNF_PARAGRAPH | string | BNF paragraph label | Lipid-regulating drugs | Source label | Classification absent | Display only | Observed NHSBSA |
| BNF_SECTION_CODE → BNF_SECTION_CODE | string | BNF section classification code | 0212 | Source BNF code | Classification absent | Later category grouping | Observed NHSBSA |
| BNF_SECTION → BNF_SECTION | string | BNF section label | Lipid-regulating drugs | Source label | Classification absent | Display only | Observed NHSBSA |
| BNF_CHAPTER_CODE → BNF_CHAPTER_CODE | string | BNF chapter classification code | 02 | Source BNF code, leading zeros retained | Classification absent | Later category grouping | Observed NHSBSA |
| BNF_CHAPTER → BNF_CHAPTER | string | BNF chapter label | Cardiovascular System | Source label | Classification absent | Display only | Observed NHSBSA |
| PREP_CLASS → PREP_CLASS | string | Source dispensed preparation-class code | 01 | Publisher code retained without inferred meaning | Not populated | Reference pending publisher mapping | Observed NHSBSA |
| PRESCRIBED_PREP_CLASS → PRESCRIBED_PREP_CLASS | string | Source prescribed preparation-class code | 01 | Publisher code retained without inferred meaning | Not populated | Reference pending publisher mapping | Observed NHSBSA |
| ITEMS → items | float64 | Number of prescription items dispensed; not patients or packs | 10266.0 | Finite nonnegative integer count | Required; no silent zero imputation | Candidate future target/lags | Observed NHSBSA |
| TOTAL_QUANTITY → total_quantity | float64 | Dispensed physical quantity in source unit | 314592.0 | Finite nonnegative number; comparable only within units/presentations | Required | Candidate future target/lags within units | Observed NHSBSA |
| NIC → nic_gbp | float64 | Net ingredient cost in GBP; payer-cost metric, not manufacturer revenue | 7640.02 | Finite number; negative cost flagged for review | Required | Candidate future cost target/lags | Observed NHSBSA |
| PHARMACY_ADVANCED_SERVICE → PHARMACY_ADVANCED_SERVICE | string | Publisher advanced-service classification, retained without inferring additional coding meanings | Not applicable | Observed label: Not applicable in this extract | Field absent before February 2024; structural absence, not missing dispensing | Reference only; no varying signal in this extract | Observed NHSBSA |

YEAR_MONTH itself is retained as a string in the detailed table; `month` is its parsed month-start datetime.

## Monthly and diagnostic derived fields

| Field | Type | Meaning / example | Allowed values | Missing meaning | Forecast use | Origin |
|---|---|---|---|---|---|---|
| month | datetime64[ns] | Calendar month start / 2023-01-01 00:00:00 | Configured window | Invalid source date; error | Time index | Derived from Observed NHSBSA |
| source_row_count | int64 | Number of source rows contributing to a monthly key / 11 | Positive integer | Not allowed | Quality context, not prospective regressor | Derived |
| data_origin | string | Active lineage / observed_nhsbsa | observed_nhsbsa, synthetic_demo | Not allowed | Filter/label only | Explicit lineage |
| invalid_items, invalid_total_quantity, invalid_nic_gbp | bool | Nonmissing source value failed numeric parsing / False | True or False | Not allowed | Quality flags; never a target | Derived |

The other monthly fields retain the source mapping above. Measures are summed within month ×
presentation × region × unit. If any contributing measure is missing, its aggregate remains missing.
Product/region labels use the first populated source label; mapping changes are flagged before use.

## Business grain and modeling cautions

Source candidate key: every non-measure source dimension, including month, ICB, account type,
supplier, SNOMED, preparation classes and presentation. It is audited rather than assumed unique.
Monthly business key: month, product_code, region_code, unit_of_measure.
Presentation and chemical codes are not interchangeable. No actual sales/revenue/unit-price field exists.
The future forecast-use column indicates potential use only; contemporaneous cost/quantity cannot be
used to predict unknown future items unless known in advance. No model is fitted in Phase 1.
STP/ICB and BNF classification changes need temporal review. Preparation codes have no invented decoding.

## Actual measured categories

- unit_of_measure: ['ml', 'tablet']
- region_code: ['Y56', 'Y58', 'Y59', 'Y60', 'Y61', 'Y62', 'Y63']
- region_name: ['EAST OF ENGLAND', 'LONDON', 'MIDLANDS', 'NORTH EAST AND YORKSHIRE', 'NORTH WEST', 'SOUTH EAST', 'SOUTH WEST']
- chemical_code: ['0212000B0']
- chemical_name: ['Atorvastatin']
- DISPENSER_ACCOUNT_TYPE: ['English Dispensing Doctor', 'English Pharmacy']
- PREP_CLASS: ['01', '03', '05', '1', '3', '5']
- PRESCRIBED_PREP_CLASS: ['01', '02', '03', '05', '1', '2', '3', '5']
