"""Runtime-data packaging and independent dashboard audit; never rebuilds prior phases."""
import argparse
import hashlib
import importlib.metadata
import json
import platform
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
import pandas as pd
from .common import ROOT,sha256,write_json
from .decision_features import protected_snapshot as previous_snapshot

def protected_snapshot(root=ROOT):
    inventory=previous_snapshot(root)
    for directory,pattern in [('outputs/phase5/tables','*'),('outputs/phase5/charts','*.png'),('outputs/phase5/validation','*.json'),
                               ('outputs/phase5/validation','*.xml'),('outputs/phase5/validation','*.csv'),('docs','PHASE5*.md'),
                               ('notebooks','0[67]*.ipynb'),('config','decision_intelligence.yaml')]:
        for p in (root/directory).glob(pattern):
            if p.is_file(): inventory[str(p.relative_to(root)).replace('\\','/')]=sha256(p)
    return dict(sorted(inventory.items()))

def prepare(root=ROOT):
    directory=root/'outputs/phase6/validation'; directory.mkdir(parents=True,exist_ok=True)
    before=protected_snapshot(root); guard=directory/'source_guard.json'
    if guard.exists() and json.loads(guard.read_text(encoding='utf-8'))!=before: raise AssertionError('Protected Phase 1–5 artifacts changed')
    if not guard.exists(): write_json(guard,before)
    audit=json.loads((root/'outputs/phase5/validation/final_audit.json').read_text(encoding='utf-8'))
    if not audit['passed']: raise AssertionError('Phase 5 audit must pass')
    specifications={}
    for name,item in audit['exports'].items():
        for suffix in ['csv','parquet']:
            if sha256(root/f'outputs/phase5/tables/{name}.{suffix}')!=item[suffix+'_sha256']: raise AssertionError('Phase 5 output hash mismatch')
        specifications['p5/'+name]=(f'outputs/phase5/tables/{name}.parquet',item['business_key'])
    extras={
      'p2/cost_analytics':('outputs/tables/cost_analytics.parquet',['month','region_code','presentation_key']),
      'p2/missing_series_months':('outputs/tables/missing_series_months.parquet',['month','region_code','presentation_key']),
      'p2/national_monthly_trends':('outputs/tables/national_monthly_trends.parquet',['month']),
      'p2/national_annual_trends':('outputs/tables/national_annual_trends.parquet',['calendar_year']),
      'p3/cost_decomposition_diagnostics':('outputs/phase3/tables/cost_decomposition_diagnostics.parquet',['comparison']),
      'p4/backtest_predictions':('outputs/phase4/tables/backtest_predictions.parquet',['series_id','variant','origin_date','horizon','split_type']),
      'p4/model_selection_decisions':('outputs/phase4/tables/model_selection_decisions.parquet',['series_id']),
      'p4/frozen_family_configurations':('outputs/phase4/tables/frozen_family_configurations.parquet',['aggregation_level','variant']),
      'p4/holdout_model_metrics':('outputs/phase4/tables/holdout_model_metrics.parquet',['aggregation_level','variant']),
      'p4/horizon_metrics':('outputs/phase4/tables/horizon_metrics.parquet',['split_type','aggregation_level','variant','horizon']),
    }
    specifications.update(extras)
    datasets={}
    for name,(path,keys) in sorted(specifications.items()):
        frame=pd.read_parquet(root/path)
        dates={col:[frame[col].min().isoformat(),frame[col].max().isoformat()] for col in frame if pd.api.types.is_datetime64_any_dtype(frame[col]) and frame[col].notna().any()}
        datasets[name]={'path':path,'keys':keys,'columns':list(frame.columns),'dtypes':{c:str(frame[c].dtype) for c in frame},'dates':dates,'rows':len(frame),'sha256':sha256(root/path)}
    m={'app_version':'1.0.0','validated':True,'data_version':hashlib.sha256(json.dumps(datasets,sort_keys=True).encode()).hexdigest(),
       'historical_start':'2023-01-01','historical_end':'2025-12-01','datasets':datasets}
    write_json(root/'config/dashboard_manifest.json',m)
    inspected=['README.md','requirements.txt','run_pipeline.py','config/forecasting.yaml','config/decision_intelligence.yaml']+[f'docs/PHASE{i}_AUDIT.md' for i in range(1,6)]+[
        'docs/PHASE4_MODEL_CARD.md','docs/PHASE4_MODEL_COMPARISON.md','docs/PHASE5_EXECUTIVE_SUMMARY.md','docs/PHASE5_DECISION_FRAMEWORK.md','docs/PHASE5_SCENARIO_METHODOLOGY.md']
    write_json(directory/'repository_inspection.json',{'inspected_files':{p:sha256(root/p) for p in inspected if (root/p).is_file()},
        'missing_expected_files':[p for p in inspected if not (root/p).is_file()],'settings_yaml_exists':(root/'config/settings.yaml').exists(),
        'all_prior_reporting_tables':[{'path':str(p.relative_to(root)).replace('\\','/'),'rows':len(pd.read_parquet(p)),'columns':list(pd.read_parquet(p).columns)} for d in ['outputs/tables','outputs/phase3/tables','outputs/phase4/tables','outputs/phase5/tables'] for p in sorted((root/d).glob('*.parquet'))]})
    return m

def numerical_checks(root=ROOT):
    from dashboard.data_loader import load
    from dashboard.filters import apply
    from dashboard.metrics import totals,monthly,annual_growth,summarize,comparisons
    from dashboard.scenarios import simulate,mix_simulation
    rows=[]
    def check(name,expected,observed,tolerance=1e-6):
        difference=float(observed)-float(expected); passed=abs(difference)<=tolerance
        rows.append({'check_name':name,'expected':expected,'observed':observed,'difference':difference,'tolerance':tolerance,'status':'passed' if passed else 'failed'})
    fact=load('p2/cost_analytics',root)
    reference=load('p2/national_monthly_trends',root)
    check('full historical item sum',reference.prescription_items.sum(),totals(fact)['items'],0)
    check('full historical NIC sum',reference.net_ingredient_cost_gbp.sum(),totals(fact)['nic_gbp'],.01)
    for r in reference.itertuples():
        k=totals(apply(fact,start=r.month,end=r.month))
        check(f'{r.month:%Y-%m}: items',r.prescription_items,k['items'],0)
        check(f'{r.month:%Y-%m}: NIC',r.net_ingredient_cost_gbp,k['nic_gbp'],.01)
        check(f'{r.month:%Y-%m}: weighted ratio',r.net_ingredient_cost_gbp/r.prescription_items,k['nic_per_item_gbp'],1e-10)
    for region in sorted(fact.region_code.unique()):
        for year in sorted(fact.month.dt.year.unique()):
            f=apply(fact,regions=[region]); f=f[f.month.dt.year.eq(year)]
            counts=[x.prescription_items for x in f.itertuples()]; costs=[x.net_ingredient_cost_gbp for x in f.itertuples()]
            k=totals(f); check(f'{region}/{year}: filtered items',sum(counts),k['items'],0)
            check(f'{region}/{year}: weighted ratio',sum(costs)/sum(counts),k['nic_per_item_gbp'],1e-10)
    for r in load('p2/national_annual_trends',root).itertuples():
        if pd.notna(r.prior_year_items):
            g=annual_growth(fact,r.calendar_year).iloc[0]
            check(f'{r.calendar_year}: item growth',100*(r.prescription_items/r.prior_year_items-1),g.item_growth_pct)
            check(f'{r.calendar_year}: NIC growth',100*(r.net_ingredient_cost_gbp/r.prior_year_cost_gbp-1),g.nic_growth_pct)
    back=load('p4/backtest_predictions',root); families=load('p4/frozen_family_configurations',root)
    for level in ['national','regional','region_presentation']:
        ids=load('p4/model_selection_decisions',root); ids=ids[ids.aggregation_level.eq(level)]
        variants=families[families.aggregation_level.eq(level)].variant.tolist()
        for sid in ids.series_id:
            for h in [1,2,3]:
                f=apply(back[back.series_id.eq(sid)],horizon=h,stage='holdout')
                metrics,good=comparisons(f,variants)
                for r in metrics.itertuples():
                    values=good[good.variant.eq(r.variant)]
                    errors=[x.prediction-x.actual for x in values.itertuples()]
                    check(f'{sid}/{h}/{r.variant}: MAE',sum(abs(x) for x in errors)/len(errors),r.MAE)
                    check(f'{sid}/{h}/{r.variant}: MASE',sum(abs(x.prediction-x.actual)/x.mase_scale for x in values.itertuples())/len(errors),r.MASE)
    year=int(fact.month.dt.year.max()); f=fact[fact.month.dt.year.eq(year)]; k=totals(f)
    for v in [-20,-5,0,5,20]:
        for c in [-20,-5,0,5,20]:
            out=simulate(k['items'],k['nic_gbp'],v,c,str(year)).iloc[0]
            check(f'scenario {v}/{c}',k['nic_gbp']*(1+v/100)*(1+c/100),out.hypothetical_nic_gbp,.01)
            check(f'break-even {v}/{c}',1,(1+v/100)*(1+out.break_even_cost_change_pct/100),1e-12)
    p=summarize(f,['presentation_key','presentation_name']).rename(columns={'prescription_items':'recent_items','nic_per_item_gbp':'recent_nic_per_item_gbp'}).sort_values('recent_items',ascending=False)
    for transfer in [0,1,2,5]:
        out=mix_simulation(p,k['items'],p.presentation_key.iloc[0],p.presentation_key.iloc[1],transfer)
        check('mix share conservation '+str(transfer),1,sum(out.scenario_share),1e-12)
        check('mix item conservation '+str(transfer),k['items'],sum(out.hypothetical_items),1e-6)
    frame=pd.DataFrame(rows); frame.to_csv(root/'outputs/phase6/validation/dashboard_reconciliation.csv',index=False)
    if frame.status.ne('passed').any(): raise AssertionError('Dashboard numerical reconciliation failed')
    return {'checks':len(frame),'failed_checks':0,'calculation_sha256':sha256(root/'outputs/phase6/validation/dashboard_reconciliation.csv')}

def final_audit(root=ROOT):
    prepare(root)
    from .phase6_startup import startup
    startup_result=startup(root)
    first=numerical_checks(root); second=numerical_checks(root)
    if first!=second: raise AssertionError('Dashboard calculations are not deterministic')
    write_json(root/'outputs/phase6/validation/reproducibility.json',{'identical':True,'first':first,'second':second})
    command=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',f'--basetemp=outputs/phase6/validation/tests_tmp_{uuid.uuid4().hex[:8]}','--junitxml=outputs/phase6/validation/all_tests.xml']
    process=subprocess.run(command,cwd=root,capture_output=True,text=True)
    (root/'outputs/phase6/validation/test_execution.log').write_text(process.stdout+process.stderr,encoding='utf-8'); print(process.stdout,flush=True)
    suites=ET.parse(root/'outputs/phase6/validation/all_tests.xml').getroot().findall('testsuite')
    counts={k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
    guard=json.loads((root/'outputs/phase6/validation/source_guard.json').read_text(encoding='utf-8'))
    unchanged=protected_snapshot(root)==guard
    result={'passed':process.returncode==0 and unchanged and startup_result['passed'] and startup_result['server_stopped'],'tests':counts,'numerical_validation':second,
            'startup':startup_result,
            'protected_artifacts':len(guard),'protected_artifacts_unchanged':unchanged,'calculations_deterministic':True,
            'browser_inspection':'Not performed: no browser automation tool available; AppTest used instead',
            'cloud_deployment':'Not performed; local startup and deployment packaging only',
            'python':platform.python_version(),'versions':{p:importlib.metadata.version(p) for p in ['streamlit','plotly','pandas','numpy','pyarrow']},
            'dataset_manifest_sha256':sha256(root/'config/dashboard_manifest.json'),'theme_sha256':sha256(root/'.streamlit/config.toml')}
    write_json(root/'outputs/phase6/validation/final_audit.json',result)
    from .phase6_reports import reports
    reports(result,root)
    if not result['passed']: raise AssertionError('Phase 6 audit failed')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--prepare',action='store_true'); args=parser.parse_args()
    prepare() if args.prepare else final_audit()
