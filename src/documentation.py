"""Generate the complete source/derived dictionary using measured example values."""
import json
import pandas as pd
from .common import ROOT

DEFINITIONS = {
 'YEAR_MONTH': ('Source calendar month YYYYMM, retained alongside parsed month', 'Six digits representing a valid month', 'Required', 'Time index after date parsing', 'YEAR_MONTH'),
 'REGION_CODE': ('Dispensing administrative region identifier', 'Source region code; special values require review', 'Required', 'Grouping', 'region_code'),
 'REGION_NAME': ('Dispensing region label, not patient residence', 'Source label paired with region code', 'Required', 'Display only', 'region_name'),
 'ICB_CODE': ('Integrated Care Board of dispensing contractor', 'Source ICB identifier', 'Unknown/unpopulated if missing', 'Grouping with geography review', 'ICB_CODE'),
 'ICB_NAME': ('Integrated Care Board label', 'Source label', 'Unknown/unpopulated if missing', 'Display only', 'ICB_NAME'),
 'STP_CODE': ('Legacy Sustainability and Transformation Partnership identifier', 'Source legacy STP identifier', 'Not populated if current ICB schema', 'Historical geography review', 'STP_CODE'),
 'STP_NAME': ('Legacy STP label', 'Source label', 'Not populated if current ICB schema', 'Display only', 'STP_NAME'),
 'DISPENSER_ACCOUNT_TYPE': ('Type of dispensing contractor account', 'Publisher categories; inspect observed distinct values', 'Unknown/unpopulated', 'Possible segmentation later', 'DISPENSER_ACCOUNT_TYPE'),
 'BNF_PRESENTATION_CODE': ('BNF product presentation identifier (formulation/strength)', '15 uppercase alphanumeric characters', 'Required', 'Series grouping', 'product_code'),
 'BNF_PRESENTATION_NAME': ('Source medicine presentation label', 'Source label; names may evolve', 'Required', 'Display only', 'product_name'),
 'SNOMED_CODE': ('Source SNOMED medicine concept identifier', 'Identifier stored as string, never floating point', 'No source concept supplied', 'Grouping/reference only', 'SNOMED_CODE'),
 'SUPPLIER_NAME': ('Source supplier label where available', 'Source string', 'Unknown/not populated; not assumed generic', 'Not a sales-representative feature', 'SUPPLIER_NAME'),
 'PHARMACY_ADVANCED_SERVICE': ('Publisher advanced-service classification, retained without inferring additional coding meanings', 'Observed label: Not applicable in this extract', 'Field absent before February 2024; structural absence, not missing dispensing', 'Reference only; no varying signal in this extract', 'PHARMACY_ADVANCED_SERVICE'),
 'UNIT_OF_MEASURE': ('Physical unit associated with total quantity', 'Source unit such as tablet or ml; see actual values', 'Required; quantity is uninterpretable without unit', 'Grouping to prevent mixed-unit totals', 'unit_of_measure'),
 'GENERIC_BNF_EQUIVALENT_CODE': ('Generic equivalent BNF presentation identifier', 'Source BNF identifier', 'No equivalent supplied', 'Reference or later grouping', 'GENERIC_BNF_EQUIVALENT_CODE'),
 'GENERIC_BNF_EQUIVALENT_NAME': ('Generic equivalent label', 'Source label', 'No equivalent supplied', 'Display only', 'GENERIC_BNF_EQUIVALENT_NAME'),
 'BNF_CHEMICAL_SUBSTANCE_CODE': ('BNF chemical identifier', '0212000B0 in this selected observed extract', 'Required', 'Category grouping', 'chemical_code'),
 'BNF_CHEMICAL_SUBSTANCE': ('BNF chemical label', 'Atorvastatin in selected observed extract', 'Required', 'Category grouping', 'chemical_name'),
 'BNF_PARAGRAPH_CODE': ('BNF paragraph classification code', 'Source BNF code', 'Classification absent', 'Later category grouping', 'BNF_PARAGRAPH_CODE'),
 'BNF_PARAGRAPH': ('BNF paragraph label', 'Source label', 'Classification absent', 'Display only', 'BNF_PARAGRAPH'),
 'BNF_SECTION_CODE': ('BNF section classification code', 'Source BNF code', 'Classification absent', 'Later category grouping', 'BNF_SECTION_CODE'),
 'BNF_SECTION': ('BNF section label', 'Source label', 'Classification absent', 'Display only', 'BNF_SECTION'),
 'BNF_CHAPTER_CODE': ('BNF chapter classification code', 'Source BNF code, leading zeros retained', 'Classification absent', 'Later category grouping', 'BNF_CHAPTER_CODE'),
 'BNF_CHAPTER': ('BNF chapter label', 'Source label', 'Classification absent', 'Display only', 'BNF_CHAPTER'),
 'PREP_CLASS': ('Source dispensed preparation-class code', 'Publisher code retained without inferred meaning', 'Not populated', 'Reference pending publisher mapping', 'PREP_CLASS'),
 'PRESCRIBED_PREP_CLASS': ('Source prescribed preparation-class code', 'Publisher code retained without inferred meaning', 'Not populated', 'Reference pending publisher mapping', 'PRESCRIBED_PREP_CLASS'),
 'ITEMS': ('Number of prescription items dispensed; not patients or packs', 'Finite nonnegative integer count', 'Required; no silent zero imputation', 'Candidate future target/lags', 'items'),
 'TOTAL_QUANTITY': ('Dispensed physical quantity in source unit', 'Finite nonnegative number; comparable only within units/presentations', 'Required', 'Candidate future target/lags within units', 'total_quantity'),
 'NIC': ('Net ingredient cost in GBP; payer-cost metric, not manufacturer revenue', 'Finite number; negative cost flagged for review', 'Required', 'Candidate future cost target/lags', 'nic_gbp'),
}

def dictionary(root=ROOT):
    source = pd.read_parquet(root / 'data/processed/source_rows.parquet')
    monthly = pd.read_parquet(root / 'data/processed/monthly_prescribing.parquet')
    manifest = json.loads((root / 'data/processed/acquisition_manifest.json').read_text(encoding='utf-8'))
    def example(series):
        valid = series.dropna()
        if valid.empty:
            return 'No populated example'
        return str(valid.iloc[0]).replace('|', '\\|').replace('\n', ' ')[:100]
    lines = ['# Data dictionary', '', f"Active executed mode: **{manifest['mode']}**. Examples below come from the executed extract.", '',
             'Raw JSON values are preserved byte-for-byte. In the normalized detailed table, identifiers use',
             'pandas string dtype, blanks become missing, date becomes datetime64 and measures become float64.',
             'Raw rows remain in data/raw; no abnormal observations are removed.', '',
             '## Source columns and normalized mapping', '',
             '| Source column → normalized field | Stored normalized dtype | Business meaning | Measured example | Allowed values | Missing meaning | Forecast use | Origin |',
             '|---|---|---|---|---|---|---|---|']
    origin = 'Observed NHSBSA' if manifest['mode'] == 'observed' else 'Synthetic fallback (fictional)'
    for field in manifest['source_columns']:
        meaning, allowed, missing, forecast, normalized = DEFINITIONS[field]
        column = normalized if normalized in source else field
        lines.append(f'| {field} → {normalized} | {source[column].dtype} | {meaning} | {example(source[column])} | {allowed} | {missing} | {forecast} | {origin} |')
    lines += ['', 'YEAR_MONTH itself is retained as a string in the detailed table; `month` is its parsed month-start datetime.', '',
              '## Monthly and diagnostic derived fields', '',
              '| Field | Type | Meaning / example | Allowed values | Missing meaning | Forecast use | Origin |',
              '|---|---|---|---|---|---|---|',
              f"| month | {monthly.month.dtype} | Calendar month start / {example(monthly.month)} | Configured window | Invalid source date; error | Time index | Derived from {origin} |",
              f"| source_row_count | {monthly.source_row_count.dtype} | Number of source rows contributing to a monthly key / {example(monthly.source_row_count)} | Positive integer | Not allowed | Quality context, not prospective regressor | Derived |",
              f"| data_origin | string | Active lineage / {example(monthly.data_origin)} | observed_nhsbsa, synthetic_demo | Not allowed | Filter/label only | Explicit lineage |",
              '| invalid_items, invalid_total_quantity, invalid_nic_gbp | bool | Nonmissing source value failed numeric parsing / False | True or False | Not allowed | Quality flags; never a target | Derived |', '',
              'The other monthly fields retain the source mapping above. Measures are summed within month ×',
              'presentation × region × unit. If any contributing measure is missing, its aggregate remains missing.',
              'Product/region labels use the first populated source label; mapping changes are flagged before use.',
              '', '## Business grain and modeling cautions', '',
              'Source candidate key: every non-measure source dimension, including month, ICB, account type,',
              'supplier, SNOMED, preparation classes and presentation. It is audited rather than assumed unique.',
              'Monthly business key: month, product_code, region_code, unit_of_measure.',
              'Presentation and chemical codes are not interchangeable. No actual sales/revenue/unit-price field exists.',
              'The future forecast-use column indicates potential use only; contemporaneous cost/quantity cannot be',
              'used to predict unknown future items unless known in advance. No model is fitted in Phase 1.',
              'STP/ICB and BNF classification changes need temporal review. Preparation codes have no invented decoding.',
              '', '## Actual measured categories', '']
    for field in ['unit_of_measure','region_code','region_name','chemical_code','chemical_name','DISPENSER_ACCOUNT_TYPE','PREP_CLASS','PRESCRIBED_PREP_CLASS']:
        if field in source:
            lines.append(f"- {field}: {sorted(str(x) for x in source[field].dropna().unique())}")
    (root / 'docs/DATA_DICTIONARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')

if __name__ == '__main__':
    dictionary()
