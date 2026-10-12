"""Executable notebooks use the reusable decision/scenario modules."""
import asyncio
import os
import sys
import nbformat as nbf
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager
from .common import ROOT,write_json

def build_and_execute(root=ROOT):
    if sys.platform=='win32': asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    setup="""from pathlib import Path
import sys
import pandas as pd
from IPython.display import display, Image
root=Path.cwd()
if root.name=='notebooks': root=root.parent
sys.path.insert(0,str(root))
from src.decision_features import configuration
from src.prioritization import priority_scores
from src.scenario_engine import accounting, break_even, mix_simulation
cfg=configuration(root)
def table(name): return pd.read_parquet(root/f'outputs/phase5/tables/{name}.parquet')
def chart(name): display(Image(filename=str(root/f'outputs/phase5/charts/{name}.png')))
"""
    specs={
      '06_decision_intelligence':[
        ('# Decision intelligence','Monitoring and investigation priorities for observed England atorvastatin activity, not market opportunity or clinical advice.'),
        setup,
        ('## Features and observed history','Grains are unique. Observed rows union absence-only cells preserves the calendar; absent activity is unknown, not zero.'),
        "display(table('executive_kpi_summary'))\ndisplay(table('regional_decision_features'))\ndisplay(table('presentation_change_contributions'))",
        ('## Transparent policy priorities','Five retained components: activity 25%, absolute change 20%, cost-pattern change 20%, forecast error 20%, data quality 15%. Percentile scores use midranks; missing required dimensions leave an entity unscored. Scores describe analytical attention, not commercial value.'),
        "f=table('regional_decision_features')\nrecalculated=priority_scores(f,cfg)\nassert recalculated.entity_id.tolist()==table('regional_priority_scores').entity_id.tolist()\ndisplay(table('regional_priority_scores')[['region_name','activity_score','change_score','cost_score','forecast_score','quality_score','composite_score','rank','monitoring_tier']])\ndisplay(table('presentation_priority_scores')[['presentation_name','rank','monitoring_tier','missing_components']])\nchart('01_regional_priority_matrix')",
        ('## Sensitivity and rank stability','Equal/activity/forecast/data-quality weights, leave-one-component-out, min-max normalization and three tier settings expose policy dependence. A changed rank is not probabilistic uncertainty.'),
        "display(table('rank_stability_summary'))\ndisplay(table('priority_rank_instability').query(\"aggregation_level == 'regional'\"))\nchart('04_priority_sensitivity')\nchart('05_rank_stability')",
        ('## Frozen forecast reliability','Phase 5 does not fit or reselect models. Historical errors are scaled and compared against naive on paired support. Six months of overlapping holdout targets cannot establish future guarantees; no calibrated intervals are available.'),
        "display(table('forecast_reliability_profiles').query(\"aggregation_level != 'region_presentation'\"))\ndisplay(table('forecast_horizon_risk').query(\"series_id == 'England' and split_type == 'holdout'\"))\nchart('09_regional_reliability')\nchart('12_hierarchy_gaps')",
        ('## Rule-based analyst investigations','Each proposed action records its trigger, source key, observed value, evidence class and limitation. No clinical, manufacturer-price or resource-investment recommendation is generated.'),
        "display(table('executive_recommendations').head(20))\ndisplay(table('decision_evidence_register'))\nassert table('recommendations_dashboard').recommendation_id.is_unique\nchart('18_recommendation_priorities')"],
      '07_scenario_analysis':[
        ('# Hypothetical accounting scenarios','Stress-test assumptions are not predicted outcomes, probabilities, savings or financial profitability.'),setup,
        ('## Observed and forecast baselines','Observed baseline: 2025 weighted NIC/item and item total. Planning baseline: frozen January–March 2026 point forecasts using the December 2025 observation cutoff. Historical 2025 cost ratios are held fixed as assumptions, not extrapolated trends.'),
        "display(table('scenario_assumptions').head(12))\ndisplay(table('scenario_results').query(\"baseline_type == 'Model forecast baseline'\").head())\nn=table('national_decision_summary').iloc[0]",
        ('## One-way and combined sensitivities','NIC = items × weighted NIC/item. Volume and cost adjustments multiply, including their interaction.'),
        "display({'demonstration_plus_5pct_volume':accounting(n.recent_items,n.recent_nic_per_item_gbp,5,0)})\ndisplay(table('scenario_results').query(\"scenario_name.str.startswith('C:')\",engine='python').head())\nchart('13_volume_sensitivity')\nchart('14_cost_sensitivity')\nchart('15_two_way_sensitivity')",
        ('## Mix-only conservation','Transfer 1/2/5 percentage points from the largest 2025 presentation to the second-largest. All 17 shares remain nonnegative and sum to one. Total prescription items stay fixed. This accounting simulation is not clinically appropriate substitution advice.'),
        "p=table('presentation_decision_features').sort_values(['recent_items','presentation_key'],ascending=[False,True])\ndonor,receiver=p.presentation_key.iloc[:2]\ndemo=mix_simulation(p,n.recent_items,donor,receiver,1)\nassert abs(demo.hypothetical_items.sum()-n.recent_items)<1e-6\ndisplay(table('presentation_mix_scenarios').head(17))\nchart('16_mix_sensitivity')",
        ('## Regional and forecast planning sensitivity','Regional scenarios change one region at a time and leave the other six fixed. Forecast planning scenarios change point expectations hypothetically; these are not confidence bands.'),
        "display(table('scenario_results').query(\"scenario_name.str.startswith('E:')\",engine='python').head(10))\ndisplay(table('scenario_results').query(\"scenario_name.str.startswith('F:')\",engine='python'))",
        ('## Accounting break-even and limits','Offsetting NIC/item change = 1/(1 + volume change) − 1. Equality of accounting NIC is unrelated to financial profitability. No intervention outcome is estimated.'),
        "display({'plus_5pct_volume_offset_pct':break_even(5)})\ndisplay(table('accounting_break_even_analysis'))\nchart('17_accounting_break_even')\nchecks=pd.read_csv(root/'outputs/phase5/validation/decision_reconciliation.csv')\nassert checks.status.eq('passed').all()\ndisplay(checks.status.value_counts())"]}
    kernels=root/'config/kernels'
    write_json(kernels/'pharma-phase5/kernel.json',{'argv':[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],'display_name':'Python (pharma phase 5)','language':'python'})
    runtime=root/'outputs/phase5/validation/jupyter_runtime'; runtime.mkdir(parents=True,exist_ok=True); os.environ['JUPYTER_RUNTIME_DIR']=str(runtime)
    class ProjectClient(NotebookClient):
        def create_kernel_manager(self):
            manager=super().create_kernel_manager(); manager.kernel_spec_manager=KernelSpecManager(kernel_dirs=[str(kernels)]); return manager
    results=[]
    for name,content in specs.items():
        cells=[nbf.v4.new_markdown_cell(x[0]+'\n\n'+x[1]) if isinstance(x,tuple) else nbf.v4.new_code_cell(x) for x in content]
        for i,cell in enumerate(cells): cell['id']=f'{name}-{i:02d}'
        nb=nbf.v4.new_notebook(cells=cells); nb.metadata['kernelspec']={'name':'pharma-phase5','display_name':'Python (pharma phase 5)','language':'python'}
        path=root/f'notebooks/{name}.ipynb'; nbf.write(nb,path)
        ProjectClient(nb,timeout=180,kernel_name='pharma-phase5',resources={'metadata':{'path':str(root)}}).execute(); nbf.write(nb,path)
        codes=[c for c in nb.cells if c.cell_type=='code']
        results.append({'notebook':str(path.relative_to(root)).replace('\\','/'),'code_cells':len(codes),
                        'unexecuted_code_cells':sum(c.execution_count is None for c in codes),'error_outputs':sum(o.output_type=='error' for c in codes for o in c.outputs)})
        print('Executed '+name,flush=True)
    write_json(root/'outputs/phase5/validation/notebook_execution.json',results)
    return results
