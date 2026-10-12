"""Executed experiment/evaluation notebooks reuse production forecasting functions."""
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
from src.forecast_config import configuration
from src.forecast_models import fit_forecast
from src.forecast_features import supervised_pairs
from src.forecast_metrics import metrics
cfg=configuration(root)
def table(name): return pd.read_parquet(root/f'outputs/phase4/tables/{name}.parquet')
def chart(name): display(Image(filename=str(root/f'outputs/phase4/charts/{name}.png')))
national=pd.read_parquet(root/'outputs/tables/national_monthly_trends.parquet').set_index('month').prescription_items.sort_index()
"""
    specs={
      '04_forecasting_experiments':[
        md('# Forecasting experiments\nPredict recorded monthly prescription-item activity at horizons 1–3. Fixed England atorvastatin data, 2023–2025; this does not predict patients, revenue or India demand.'),code(setup),
        md('## Chronological design and training-only eligibility\nThe development data end June 2025. Holdout outcomes July–December cannot select models. The initial 24 months freeze volume/coverage eligibility; the full-history Phase 2 inventory is descriptive. Holdout origins begin June 2025, so horizon samples are triangular (6/5/4), without pre-freeze origins.'),
        code("display(table('series_eligibility').query('eligible'))\ndisplay(table('development_folds'))\ndisplay(table('holdout_folds'))"),
        md('## Baselines at one genuine origin\nNaive uses the last value; seasonal naive uses the target month a year earlier; drift extends the first-to-last slope. All three future steps are issued from the same cutoff.'),
        code("train=national.loc[:'2024-12-01']\nfor model in ['naive','seasonal_naive','drift']:\n    raw,point,parameters,_=fit_forecast(train,[1,2,3],{'model':model,'variant':model,'alpha':None},cfg)\n    display({'model':model,'origin':str(train.index[-1]),'prediction':point.tolist(),'parameters':parameters})"),
        md('## Damped ETS\nAdditive damped trend, no seasonality, estimated initialization from the training slice. Optimization failures remain unavailable and are logged; they are not relabeled fallback forecasts.'),
        code("raw,point,parameters,_=fit_forecast(train,[1,2,3],{'model':'damped_ets','variant':'damped_ets','alpha':None},cfg)\ndisplay(parameters)\ndisplay(point)\ndisplay(table('model_failures')[['series_id','origin_date','horizon','failure_reason']])"),
        md('## Direct Ridge and leakage prevention\nAt feature origin t, lag_1 is y(t), lag_2=y(t−1), lag_3=y(t−2). Training labels y(t+h) must already be observed by the cutoff. Calendar sine/cosine are known ahead. StandardScaler fits only supervised training rows. Six compact features leave 21/20/19 rows at the first origin; alpha comes from development folds.'),
        code("x,y,provenance=supervised_pairs(train,3,cfg)\ndisplay(x.head())\ndisplay(provenance.tail())\nassert provenance.target_date.max()<=train.index[-1]\n_,point,parameters,_=fit_forecast(train,[1,2,3],{'model':'ridge','variant':'ridge_alpha_10','alpha':10},cfg)\ndisplay(parameters)\ndisplay(table('development_configuration_metrics'))"),
        md('## Frozen model choice\nShared pooled-level MASE selection, with 2% simplicity tie tolerance. Any development failure excludes a configuration from selection for that level. Final holdout scores cannot change the choices.'),
        code("display(table('model_selection_decisions').drop_duplicates(['aggregation_level','selected_variant']))\nchart('01_national_history_origins')\nchart('12_development_holdout')")],
      '05_forecast_evaluation':[
        md('# Forecast evaluation\nAll results derive from stored genuine origin/horizon predictions. Overlapping errors and short holdout windows prevent independent-sample significance claims.'),code(setup),
        md('## Model comparison and baseline\nMASE scales each forecast using the mean absolute adjacent training change at its own origin. Bias=prediction−actual. Common-support comparisons remove failed cells for every model. Selected-model summaries retain all selected forecast opportunities.'),
        code("display(table('holdout_model_metrics'))\ndisplay(table('horizon_metrics').query(\"split_type == 'holdout' and aggregation_level == 'national'\"))\nchart('03_national_models')\nchart('06_accuracy_horizon')"),
        md('## Regional errors and residuals\nRaw MAE reflects size; origin-scaled MASE complements it. Regions are fixed geographic aggregates, not random independent samples. Errors overlap across horizons.'),
        code("display(table('regional_forecast_metrics').query(\"split_type == 'holdout'\"))\nchart('08_regional_error_heatmap')\nchart('10_residual_distribution')"),
        md('## Interval support\nOnly six/five/four development errors per series/horizon are available, below the prespecified minimum of 20. Bounds and empirical coverage are null. A pooled regional residual count cannot supply independent calibration for a national forecast.'),
        code("display(table('interval_calibration').query(\"series_id == 'England'\"))\ndisplay(table('interval_coverage_summary'))\nchart('15_interval_support')"),
        md('## Hierarchy\nNational observed items equal all seven regions; each region equals all observed presentations. The screened presentation subset is not the entire population. Direct national and regional-sum forecasts remain separate; coherence gaps are reported without rescaling.'),
        code("checks=table('forecast_hierarchy_checks')\nassert checks.status.eq('passed').all()\ndisplay(table('aggregate_forecast_metrics'))\ndisplay(table('aggregate_forecast_comparison').tail())\nchart('16_direct_regional_sum')"),
        md('## Retrospective operational forecasts and limits\nFrozen models are refitted through December 2025 to issue January–March 2026 forecasts. These are historical as-of forecasts, not current predictions. No 2026 actuals are fetched or implied. Point forecasts are continuous expected counts; source values are untouched.'),
        code("display(table('operational_forecasts').query(\"series_id == 'England'\"))\nchart('18_operational_forecasts')\ndisplay(table('forecast_robustness_results').head(20))\nassert not table('backtest_predictions').duplicated(['series_id','variant','origin_date','horizon','split_type']).any()")]
    }
    kernels=root/'config/kernels'; write_json(kernels/'pharma-phase4/kernel.json',{'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Python (pharma phase 4)','language':'python'})
    runtime=root/'outputs/phase4/validation/jupyter_runtime'; runtime.mkdir(parents=True,exist_ok=True); os.environ['JUPYTER_RUNTIME_DIR']=str(runtime)
    class ProjectClient(NotebookClient):
        def create_kernel_manager(self):
            manager=super().create_kernel_manager(); manager.kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernels)]); return manager
    results=[]
    for name,cells in specs.items():
        for i,cell in enumerate(cells): cell['id']=f'{name}-{i:02d}'
        nb=nbf.v4.new_notebook(cells=cells); nb.metadata['kernelspec']={'name':'pharma-phase4','display_name':'Python (pharma phase 4)','language':'python'}
        path=root/f'notebooks/{name}.ipynb'; nbf.write(nb,path)
        ProjectClient(nb,timeout=180,kernel_name='pharma-phase4',resources={'metadata':{'path':str(root)}}).execute(); nbf.write(nb,path)
        codes=[c for c in nb.cells if c.cell_type=='code']
        results.append({'notebook':str(path.relative_to(root)).replace('\\','/'),'code_cells':len(codes),
                        'unexecuted_code_cells':sum(c.execution_count is None for c in codes),
                        'error_outputs':sum(o.output_type=='error' for c in codes for o in c.outputs)})
        print('Executed '+name,flush=True)
    write_json(root/'outputs/phase4/validation/notebook_execution.json',results)
    return results
