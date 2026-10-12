"""Measured Phase 1 inspection and generated documentation, with no predictive models."""
import json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import duckdb
from .common import ROOT, write_json

def inspect_data(root=ROOT):
    df = pd.read_parquet(root / 'data/processed/monthly_prescribing.parquet')
    raw = pd.read_parquet(root / 'data/processed/source_rows.parquet')
    manifest = json.loads((root / 'data/processed/acquisition_manifest.json').read_text(encoding='utf-8'))
    quality = json.loads((root / 'outputs/validation/quality_report.json').read_text(encoding='utf-8'))
    tables = root / 'outputs/tables'
    tables.mkdir(parents=True, exist_ok=True)
    df.describe(include='all').astype('string').to_csv(tables / 'descriptive_statistics.csv')
    df.groupby(['product_code','product_name'], dropna=False).agg(monthly_rows=('items','size'), items=('items','sum'), nic_gbp=('nic_gbp','sum')).to_csv(tables / 'product_distribution.csv')
    df.groupby(['region_code','region_name'], dropna=False).agg(monthly_rows=('items','size'), items=('items','sum'), nic_gbp=('nic_gbp','sum')).to_csv(tables / 'geographic_coverage.csv')
    monthly_totals = df.groupby('month')[['items','nic_gbp']].sum()
    monthly_totals.to_csv(tables / 'monthly_totals.csv')
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(monthly_totals.index, monthly_totals['items'], marker='.')
    ax.set(title=f"{manifest['mode'].upper()}: selected atorvastatin prescription items", ylabel='Prescription items', xlabel='Month')
    fig.tight_layout()
    fig.savefig(root / 'outputs/charts/monthly_items.png', dpi=150)
    plt.close(fig)
    # SQL-ready staging only; Phase 2 commercial queries remain unimplemented.
    with duckdb.connect(str(root / 'data/processed/pharma.duckdb')) as con:
        con.register('monthly_frame', df)
        con.execute('CREATE OR REPLACE TABLE monthly_prescribing AS SELECT * FROM monthly_frame')
        count = con.execute('SELECT count(*) FROM monthly_prescribing').fetchone()[0]
        assert count == len(df)
    findings = [c for c in quality['checks'] if c['count'] and c['severity'] in ['error','warning','info']]
    text = f'''# Initial data assessment

Generated from the executed Phase 1 pipeline. Data mode: **{manifest['mode']}**.

The source extract contains **{len(raw):,} rows and {len(manifest['source_columns'])} source columns**.
The monthly table contains **{len(df):,} rows and {len(df.columns)} columns**,
covering **{df.month.min().date()} to {df.month.max().date()}**, with **{df.month.nunique()} months**,
**{df.product_code.nunique()} presentations**, **{df.chemical_code.nunique()} chemical category** and
**{df.region_code.nunique()} geographic codes**. See geographic_coverage.csv for actual region labels,
including any unknown/special codes. Product presentation is a formulation/strength identifier, not a sales SKU.

Required processed-column missing cells: **{int(df.isna().sum().sum())}**.
Source missing cells: **{int(raw.isna().sum().sum())}**, including optional administrative fields.
Audit error gate passed: **{quality['passed']}**. All anomalies are retained.

## Measured findings

'''
    text += '\n'.join(f"- {c['check']}: {c['count']:,}. {c['explanation']}" for c in findings) or '- No findings.'
    schema = manifest.get('files', [])
    variations = {}
    for page in schema:
        fields = tuple(page.get('source_fields', []))
        if fields:
            variations.setdefault(fields, []).append(page['file'])
    text += '\n\nSource schema variations: ' + str(sorted(len(fields) for fields in variations)) + ' columns per monthly response; the detailed table retains the union.\n'
    if 'PHARMACY_ADVANCED_SERVICE' in raw:
        text += 'PHARMACY_ADVANCED_SERVICE is absent before February 2024 and has the observed label Not applicable thereafter in this selected extract. Its earlier nulls are structural schema absence.\n'
    text += '''

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
'''
    (root / 'docs/INITIAL_DATA_ASSESSMENT.md').write_text(text, encoding='utf-8')
    return df

if __name__ == '__main__':
    inspect_data()
