"""Build small review notebooks importing production functions, then execute every cell."""
import asyncio
import os
import sys
import nbformat as nbf
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager
from .common import ROOT,write_json

def build_and_execute(root=ROOT):
    if sys.platform=='win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    md=nbf.v4.new_markdown_cell; code=nbf.v4.new_code_cell
    setup="""from pathlib import Path
import sys
import pandas as pd
from IPython.display import display, Image
root=Path.cwd()
if root.name=='notebooks': root=root.parent
sys.path.insert(0,str(root))
from src.statistical_analysis import describe_series, calendar_series
from src.trend_analysis import estimate_trend
from src.cost_diagnostics import shapley_cost
def table(name): return pd.read_parquet(root / f'outputs/phase3/tables/{name}.parquet')
def chart(name): display(Image(filename=str(root / f'outputs/phase3/charts/{name}.png')))
national=pd.read_parquet(root/'outputs/tables/national_monthly_trends.parquet')
"""
    specs={
        '02_advanced_eda':[
            md('# Advanced EDA\nObserved England community dispensing, January 2023–December 2025. Items are product occurrences; NIC is not manufacturer revenue. Missing regional/presentation months are unknown, not zero.'),code(setup),
            md('## Distributions and observation units\nEach summary describes monthly observations within one stated national, region, presentation/unit, or region/presentation/unit series. CV includes trend. No native quantity is aggregated across presentations.'),
            code("summary=table('descriptive_statistics')\ndisplay(summary[summary.level=='national'])\ndisplay(table('growth_rate_distributions').query(\"level == 'national'\"))\ndisplay(describe_series(calendar_series(national,'prescription_items')))"),
            md('## Regional composition and variability\nCalendar-month matched contrasts describe fixed NHS regions; they do not estimate population-adjusted rates or prescribing quality.'),
            code("display(summary.query(\"level == 'regional' and metric == 'prescription_items'\"))\ndisplay(table('regional_statistical_comparisons').head(12))\nchart('04_regional_indexed_growth')\nchart('05_regional_growth_distribution')"),
            md('## Presentation contributions and mix\nAbsolute contributions complement percentage growth on small denominators. The four leading strengths dominate item counts; all presentations remain in the tables.'),
            code("display(table('presentation_cost_change_contributions').sort_values('items_change',ascending=False))\nchart('06_presentation_item_contributions')\nchart('07_presentation_mix')"),
            md('## Trends and cost behavior\nNational cost per item is the ratio of sums, not the average of presentation ratios.'),
            code("display(table('cost_per_item_trends').query(\"level == 'national'\").tail(12))\nchart('01_national_items')\nchart('03_cost_per_item')"),
            md('## Coverage and limitations\nAn absent cell has no established reporting/nonactivity explanation. NIC depends on quantity per item and presentation composition. No clinical, causal or India-market conclusion is supported.'),
            code("display(summary.query(\"level == 'region_presentation' and metric == 'prescription_items'\").sort_values('coverage_pct').head(12))\nchart('17_coverage_volatility')")],
        '03_statistical_intelligence':[
            md('# Statistical intelligence\nShort monthly series require cautious interpretation. Statistical models below describe association and model uncertainty, not randomized causal effects.'),code(setup),
            md('## Trend methods\nOLS uses elapsed calendar month. HAC covariance uses Bartlett lags 3, a small-sample correction and t intervals. Theil–Sen uses the median paired slope; Kendall tau is descriptive without iid p-values. HAC 1/6/12 and month indicators are sensitivities.'),
            code("display(table('trend_summary'))\ndisplay(estimate_trend(calendar_series(national,'prescription_items')))\nchart('16_trend_sensitivity')"),
            md('## Seasonal evidence\nOnly three annual cycles are available. Annual-mean indices retain within-year trend. Calendar-day normalization is a sensitivity, not working-day adjustment. Robust STL period 12 displays a seasonal component without establishing stable seasonality.'),
            code("display(table('seasonality_summary'))\ndisplay(table('monthly_seasonal_indices').head(12))\nchart('08_monthly_seasonal_profile')\nchart('10_autocorrelation')"),
            md('## Exact cost identity\n$C=V\\sum_j s_jp_j$. Shapley contributions average all six orders for changing volume $V$, shares $s$, and within-presentation NIC/item $p$. They reconcile exactly; the factor allocation is a convention, not a uniquely identified causal mechanism.'),
            code("display(table('cost_decomposition_diagnostics'))\ndisplay(shapley_cost(100,[.6,.4],[2,5],120,[.5,.5],[1,4]))\nchart('11_nic_decomposition')"),
            md('## Anomalies and robustness\nMAD z-scores use 0.67449 normalization within each series. Zero MAD and histories below 12 observations give undefined scores. Original IQR flags are retained. Classifications are heuristic review labels. Exclusions affect diagnostic copies only.'),
            code("display(table('extreme_value_review_phase3').groupby('classification').size())\ndisplay(table('anomaly_diagnostics').head(12))\ndisplay(table('robustness_summary'))\nchart('14_anomaly_timeline')"),
            md('## Forecasting implications\nNo forecast model or backtest is trained. Start with naive, seasonal-naive and drift baselines, then damped ETS and regularized lag regression. Evaluate 1–3 month horizons with chronological origins; refit preprocessing and eligibility inside folds.'),
            code("display(table('forecasting_diagnostics').query(\"level == 'national'\"))\nchart('18_forecasting_readiness')\nassert table('cost_decomposition_diagnostics').reconciliation_residual_gbp.abs().max()<.01")]
    }
    kernels=root/'config/kernels'
    write_json(kernels/'pharma-phase3/kernel.json',{'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Python (pharma phase 3)','language':'python'})
    runtime=root/'outputs/phase3/validation/jupyter_runtime'; runtime.mkdir(parents=True,exist_ok=True)
    os.environ['JUPYTER_RUNTIME_DIR']=str(runtime)
    class ProjectClient(NotebookClient):
        def create_kernel_manager(self):
            manager=super().create_kernel_manager()
            manager.kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernels)])
            return manager
    results=[]
    for stem,cells in specs.items():
        # Fixed cell IDs permit stable source diffs despite kernel execution IDs.
        for i,c in enumerate(cells): c['id']=f'{stem}-{i:02d}'
        nb=nbf.v4.new_notebook(cells=cells)
        nb.metadata['kernelspec']={'name':'pharma-phase3','display_name':'Python (pharma phase 3)','language':'python'}
        path=root/f'notebooks/{stem}.ipynb'; nbf.write(nb,path)
        ProjectClient(nb,timeout=180,kernel_name='pharma-phase3',resources={'metadata':{'path':str(root)}}).execute()
        nbf.write(nb,path)
        codes=[c for c in nb.cells if c.cell_type=='code']
        results.append({'notebook':str(path.relative_to(root)).replace('\\','/'),'code_cells':len(codes),
                        'unexecuted_code_cells':sum(c.execution_count is None for c in codes),
                        'error_outputs':sum(o.output_type=='error' for c in codes for o in c.outputs)})
        print(f'Executed {stem}',flush=True)
    write_json(root/'outputs/phase3/validation/notebook_execution.json',results)
    return results

if __name__=='__main__': build_and_execute()
