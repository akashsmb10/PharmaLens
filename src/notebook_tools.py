"""Build and execute the initial inspection notebook with this environment's Python."""
import argparse
import asyncio
import os
import sys
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager
from .common import ROOT, write_json

def build_notebook(root=ROOT):
    md = nbf.v4.new_markdown_cell
    code = nbf.v4.new_code_cell
    nb = nbf.v4.new_notebook(cells=[
        md('# 01 — Data understanding\n\nPhase 1 only. Observed NHSBSA community dispensing is not company sales. Synthetic fixtures used in tests are separate from observed analysis. Read the acquisition manifest for the active mode.'),
        code("from pathlib import Path\nimport json\nimport pandas as pd\nimport matplotlib.pyplot as plt\nfrom IPython.display import display\nroot = Path.cwd()\nif root.name == 'notebooks':\n    root = root.parent\nassert (root / 'config/dataset.json').exists(), 'Run from the project or notebooks directory'\ndf = pd.read_parquet(root / 'data/processed/monthly_prescribing.parquet')\nsource = pd.read_parquet(root / 'data/processed/source_rows.parquet')\nmanifest = json.loads((root / 'data/processed/acquisition_manifest.json').read_text(encoding='utf-8'))\nquality = json.loads((root / 'outputs/validation/quality_report.json').read_text(encoding='utf-8'))"),
        md('## Dataset overview and provenance\nThe extract is scoped to one chemical with multiple presentations. The raw API rows and region aggregation have different grains.'),
        code("display({'mode': manifest['mode'], 'source_shape': source.shape, 'monthly_shape': df.shape, 'source': manifest['dataset']['source_url'], 'monthly_key': manifest['processed_business_key']})\ndisplay(df.head(10))\ndisplay(source.head(5))"),
        md('## Types, missingness and unique values\nBlank optional supplier names mean unknown/not populated. Required key and measure missingness is an error.'),
        code("display(pd.DataFrame({'dtype': source.dtypes.astype(str), 'missing': source.isna().sum(), 'unique': source.nunique(dropna=False)}))\ndisplay(pd.DataFrame({'dtype': df.dtypes.astype(str), 'missing': df.isna().sum(), 'unique': df.nunique(dropna=False)}))"),
        md('## Descriptive statistics and time coverage'),
        code("display(df[['items', 'total_quantity', 'nic_gbp']].describe())\ndisplay({'first_month': df.month.min(), 'last_month': df.month.max(), 'months': df.month.nunique()})\ncoverage = df.groupby(['product_code', 'region_code', 'unit_of_measure']).month.agg(['min', 'max', 'nunique'])\ndisplay(coverage)"),
        md('## Product/category distribution and geographic coverage\nQuantity is not summed across presentations or units. Item counts are not unique patients.'),
        code("display(df.groupby(['chemical_code', 'chemical_name']).agg(presentations=('product_code','nunique'), items=('items','sum')))\ndisplay(df.groupby(['product_code','product_name']).agg(monthly_rows=('items','size'), items=('items','sum')))\ndisplay(df.groupby(['region_code','region_name']).agg(monthly_rows=('items','size'), items=('items','sum')))"),
        md('## Initial descriptive view\nNo predictive model or forecast is fitted.'),
        code("monthly = df.groupby('month').items.sum()\nax = monthly.plot(figsize=(10,4), marker='.', title=f\"{manifest['mode'].upper()}: selected atorvastatin prescription items\")\nax.set_ylabel('Prescription items')\nplt.tight_layout()\nplt.show()"),
        md('## Quality findings and business interpretation\nThree-IQR outliers and absent series periods are review warnings. They are retained. Revenue arithmetic is not applicable because no observed revenue exists.'),
        code("display(pd.DataFrame(quality['checks']))\ndisplay(pd.DataFrame(quality.get('missing_series_periods', [])).head(20))\ndisplay(pd.DataFrame(quality.get('extremes', [])).head(20))\nassert quality['passed'], 'Source or aggregation quality gate failed'\nassert not df.duplicated(manifest['processed_business_key']).any()"),
        md('## Supported and unsupported questions\nSupports monthly dispensing volume, ingredient-cost trends, presentation mix and regional comparisons within the selected chemical. Cannot establish manufacturer revenue, India demand, promotion effects, physician engagement, profitability or whole-market share. Future forecasting requires sufficient complete series, time-based validation and explicit treatment of product lifecycle/geographic changes. See docs/INITIAL_DATA_ASSESSMENT.md.')
    ])
    nb.metadata['kernelspec'] = {'name': 'pharma-phase1', 'display_name': 'Python (pharma phase 1)', 'language': 'python'}
    nb.metadata['language_info'] = {'name': 'python', 'version': '.'.join(map(str,sys.version_info[:3]))}
    path = root / 'notebooks/01_data_understanding.ipynb'
    nbf.write(nb, path)
    return path

def execute_notebook(root=ROOT):
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    path = root / 'notebooks/01_data_understanding.ipynb'
    kernels = root / 'config/kernels'
    write_json(kernels / 'pharma-phase1/kernel.json', {'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'], 'display_name': 'Python (pharma phase 1)', 'language': 'python'})
    runtime = root / 'outputs/validation/jupyter_runtime'
    runtime.mkdir(parents=True, exist_ok=True)
    os.environ['JUPYTER_RUNTIME_DIR'] = str(runtime)
    nb = nbf.read(path, as_version=4)
    class ProjectNotebookClient(NotebookClient):
        def create_kernel_manager(self):
            manager = super().create_kernel_manager()
            manager.kernel_spec_manager = KernelSpecManager(kernel_dirs=[str(kernels)])
            return manager
    client = ProjectNotebookClient(nb, timeout=180, kernel_name='pharma-phase1', resources={'metadata': {'path': str(root)}})
    client.execute()
    nbf.write(nb, path)
    write_json(root / 'outputs/validation/notebook_execution.json', {'notebook': str(path.relative_to(root)),
        'python': sys.executable, 'code_cells_executed': sum(c.cell_type == 'code' for c in nb.cells),
        'error_outputs': sum(o.output_type == 'error' for c in nb.cells if c.cell_type == 'code' for o in c.outputs)})
    print('Notebook executed successfully', flush=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action='store_true')
    args = parser.parse_args()
    if args.build:
        build_notebook()
    execute_notebook()
