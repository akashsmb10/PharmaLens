"""Decision intelligence orchestration; never calls a forecast fitting function."""
import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
import pandas as pd
from .common import ROOT,sha256,write_json
from .sql_analytics import atomic_csv
from .decision_features import configuration,protected_snapshot,load_inputs,historical_features,enrich_forecasts,dictionary
from .forecast_risk import risk_tables,hierarchy_gaps
from .prioritization import priority_scores,sensitivity
from .regional_intelligence import profiles as regional_profiles
from .presentation_intelligence import profiles as presentation_profiles
from .scenario_engine import scenarios
from .decision_recommendations import recommendations,evidence_register,FEATURE_TABLES
from .decision_validation import validate

def assemble(inputs,cfg):
    features=historical_features(inputs,cfg)
    reliability,risk,horizons=risk_tables(inputs,cfg); gaps=hierarchy_gaps(inputs,cfg)
    features=enrich_forecasts(features,reliability,inputs['p4/operational_forecasts'],gaps)
    tables={FEATURE_TABLES[k]:v for k,v in features.items()}
    tables['decision_feature_dictionary']=dictionary(features)
    region,matrix=regional_profiles(features['regional'])
    presentation,contributions,concentration=presentation_profiles(features['presentation'])
    tables.update(regional_monitoring_profiles=region,regional_growth_risk_matrix=matrix,
                  presentation_monitoring_profiles=presentation,presentation_change_contributions=contributions,
                  presentation_concentration_risk=concentration,forecast_reliability_profiles=reliability,
                  forecast_risk_register=risk,forecast_horizon_risk=horizons,forecast_hierarchy_gap_analysis=gaps)
    priorities={k:priority_scores(v,cfg) for k,v in features.items() if k!='national'}
    for level,f in priorities.items(): tables[level+'_priority_scores']=f
    details,summary,thresholds,unstable=sensitivity(features,priorities,cfg)
    tables.update(priority_sensitivity_results=details,rank_stability_summary=summary,
                  priority_threshold_sensitivity=thresholds,priority_rank_instability=unstable,
                  monitoring_priority_register=pd.concat(priorities.values(),ignore_index=True))
    tables.update(scenarios(features,inputs,cfg))
    rec,actions=recommendations(features,reliability,priorities,unstable,gaps,cfg)
    tables.update(executive_recommendations=rec,decision_action_register=actions)
    kpis=[]; n=features['national'].iloc[0]
    for key in ['historical_items','historical_nic_gbp','recent_items','recent_nic_gbp','item_growth_pct','nic_growth_pct','recent_nic_per_item_gbp','nic_per_item_change_pct']:
        kpis.append({'metric':key,'value':n[key],'unit':'percent' if key.endswith('pct') else 'GBP/item' if 'per_item' in key else 'GBP' if 'nic' in key else 'prescription items',
                     'period':'2023–2025' if key.startswith('historical') else '2025 versus 2024' if 'growth' in key or 'change' in key else '2025',
                     'source_output':'national_decision_summary','evidence_class':'Verified descriptive finding'})
    national_risk=reliability[reliability.series_id.eq('England')].iloc[0]
    for key in ['holdout_MASE','holdout_MAE','holdout_RMSE','holdout_WAPE','holdout_Bias','holdout_n']:
        kpis.append({'metric':key,'value':national_risk[key],'unit':'percent' if 'WAPE' in key else 'ratio' if 'MASE' in key else 'forecast rows' if key=='holdout_n' else 'prescription items',
                     'period':'July–December 2025','source_output':'forecast_reliability_profiles','evidence_class':'Validated historical model result'})
    decomposition=inputs['p3/cost_decomposition_diagnostics'].query("comparison == '2025 vs 2024'").iloc[0]
    for key in ['item_volume_effect_gbp','presentation_mix_effect_gbp','within_presentation_cost_per_item_effect_gbp']:
        kpis.append({'metric':key,'value':decomposition[key],'unit':'GBP','period':'2025 versus 2024','source_output':'Phase 3 cost_decomposition_diagnostics','evidence_class':'Verified descriptive finding'})
    tables['executive_kpi_summary']=pd.DataFrame(kpis)
    tables['regional_dashboard']=region.copy(); tables['presentation_dashboard']=presentation.copy()
    tables['region_presentation_dashboard']=features['region_presentation'].copy()
    tables['forecast_dashboard']=inputs['p4/operational_forecasts'].copy()
    tables['forecast_dashboard']['evidence_class']='Validated historical model result'
    tables['forecast_dashboard']['limitation']='Retrospective point forecasts; intervals unavailable; analytical cutoff does not reconstruct release vintage'
    tables['forecast_risk_dashboard']=risk.copy(); tables['scenario_dashboard']=tables['scenario_results'].copy()
    tables['priority_dashboard']=tables['monitoring_priority_register'].copy()
    tables['recommendations_dashboard']=rec.copy()
    tables['data_quality_dashboard']=pd.concat([f[['aggregation_level','entity_id','monthly_observations','expected_cells','observed_cells','missing_cells','missing_cell_pct','extreme_flags','flagged_cells','coverage_interpretation','evidence_class']] for f in features.values()],ignore_index=True)
    contracts={}
    for name,f in tables.items():
        if name=='decision_feature_dictionary': keys=['grain','feature']
        elif name=='priority_sensitivity_results': keys=['aggregation_level','entity_id','scheme','normalization']
        elif name=='rank_stability_summary': keys=['aggregation_level','scheme','normalization']
        elif name=='priority_threshold_sensitivity': keys=['aggregation_level','entity_id','high_threshold','moderate_threshold']
        elif name=='forecast_horizon_risk': keys=['series_id','split_type','horizon']
        elif name=='forecast_hierarchy_gap_analysis': keys=['context','origin_date','forecast_month','horizon']
        elif name=='presentation_mix_scenarios': keys=['scenario_id','presentation_key']
        elif name=='accounting_break_even_analysis': keys=['volume_change_pct']
        elif name=='forecast_dashboard': keys=['series_id','forecast_month','horizon']
        elif 'recommendation_id' in f: keys=['recommendation_id']
        elif 'scenario_id' in f: keys=['scenario_id']
        elif 'entity_id' in f: keys=['aggregation_level','entity_id'] if 'aggregation_level' in f else ['entity_id']
        elif 'series_id' in f: keys=['series_id']
        elif 'metric' in f: keys=['metric']
        else: raise AssertionError('No contract: '+name)
        if f.duplicated(keys).any(): raise AssertionError('Duplicate grain: '+name)
        contracts[name]=keys
    tables['decision_evidence_register']=evidence_register(tables,cfg)
    contracts['decision_evidence_register']=['output_table','evidence_class']
    dashboard_dictionary=[]
    for name,f in tables.items():
        if name.endswith('_dashboard') or name=='executive_kpi_summary':
            for col in f:
                dashboard_dictionary.append({'output_table':name,'field':col,'dtype':str(f[col].dtype),'business_key':';'.join(contracts[name]),
                    'grain':'One row per '+', '.join(contracts[name]),'unit':'Percent 0–100' if col.endswith('_pct') or col.endswith('WAPE') else 'GBP' if col.endswith('_gbp') else 'prescription items' if 'items' in col or col in ['point_forecast','raw_prediction'] else 'See decision_feature_dictionary/model metadata',
                    'definition':col.replace('_',' '),'source':'Matching analytical table in outputs/phase5/tables; frozen Phase 4 for forecast_dashboard',
                    'null_behavior':'Null retains unavailable/undefined evidence; never zero-filled','interpretation':'Evidence class and source period are explicit; no UI or PBIX generated'})
    tables['dashboard_data_dictionary']=pd.DataFrame(dashboard_dictionary)
    contracts['dashboard_data_dictionary']=['output_table','field']
    return tables,contracts

def run_phase5(root=ROOT,make_charts=True,make_reports=True):
    cfg=configuration(root); before=protected_snapshot(root)
    validation=root/'outputs/phase5/validation'; validation.mkdir(parents=True,exist_ok=True)
    guard=validation/'source_guard.json'
    if guard.exists() and json.loads(guard.read_text(encoding='utf-8'))!=before: raise AssertionError('Phase 1–4 artifact changed')
    if not guard.exists(): write_json(guard,before)
    inputs=load_inputs(root)
    catalog=[{'source_table':name,'rows':len(f),'columns':list(f.columns)} for name,f in inputs.items()]
    inspected=['README.md','requirements.txt','run_pipeline.py','config/forecasting.yaml','docs/METRIC_DEFINITIONS.md','docs/PHASE2_AUDIT.md','docs/PHASE2_BUSINESS_INSIGHTS.md','docs/PHASE3_AUDIT.md','docs/PHASE3_STATISTICAL_FINDINGS.md','docs/PHASE3_BUSINESS_INSIGHTS.md','docs/PHASE4_AUDIT.md','docs/PHASE4_MODEL_COMPARISON.md','docs/PHASE4_MODEL_CARD.md','docs/PHASE4_BUSINESS_INSIGHTS.md']
    for path in inspected: (root/path).read_text(encoding='utf-8')
    write_json(validation/'input_inventory.json',{'tables':catalog,'inspected_files':inspected,'settings_yaml_exists':(root/'config/settings.yaml').exists()})
    tables,contracts=assemble(inputs,cfg)
    reconciliation,passed=validate(tables,inputs,cfg,contracts)
    atomic_csv(reconciliation,validation/'decision_reconciliation.csv')
    if not passed: raise AssertionError('Independent decision reconciliation failed; inspect CSV')
    exports={}
    for name,f in tables.items():
        csv=root/f'outputs/phase5/tables/{name}.csv'; atomic_csv(f,csv)
        parquet=csv.with_suffix('.parquet'); f.to_parquet(parquet,index=False)
        exports[name]={'rows':len(f),'columns':list(f.columns),'business_key':contracts[name],
                       'csv_sha256':sha256(csv),'parquet_sha256':sha256(parquet)}
    charts=[]
    if make_charts:
        from .phase5_visualizations import generate
        charts=generate(tables,root)
    unchanged=protected_snapshot(root)==before
    if not unchanged: raise AssertionError('Prior artifacts changed during Phase 5')
    metadata={'python_version':platform.python_version(),'dependency_versions':{p:importlib.metadata.version(p) for p in ['pandas','numpy','scipy','pyarrow','matplotlib','nbclient']},
              'configuration':cfg,'configuration_sha256':sha256(root/'config/decision_intelligence.yaml'),
              'input_hashes':before,'execution_commands':['python run_pipeline.py --phase 5','python -m src.phase5_pipeline --audit']}
    write_json(validation/'run_metadata.json',metadata)
    result={'passed':True,'exports':exports,'charts':charts,'independent_checks':len(reconciliation),'independent_failed_checks':int(reconciliation.status.ne('passed').sum()),
            'protected_artifacts':len(before),'protected_artifacts_unchanged':unchanged,'configuration_sha256':metadata['configuration_sha256']}
    write_json(validation/'pipeline_summary.json',result)
    if make_reports:
        from .phase5_reports import reports
        reports(tables,result,cfg,root)
    print(f'Phase 5 complete: {len(exports)} table pairs; {len(reconciliation)} independent checks',flush=True)
    return result

def final_audit(root=ROOT):
    first=run_phase5(root); second=run_phase5(root)
    equal=first['exports']==second['exports'] and first['configuration_sha256']==second['configuration_sha256']
    if not equal: raise AssertionError('Decision exports differ between full runs')
    write_json(root/'outputs/phase5/validation/reproducibility.json',{'byte_identical':True,'first_exports':first['exports'],'second_exports':second['exports']})
    from .phase5_notebooks import build_and_execute
    notebooks=build_and_execute(root)
    command=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',f'--basetemp=outputs/phase5/validation/tests_tmp_{uuid.uuid4().hex[:8]}','--junitxml=outputs/phase5/validation/all_tests.xml']
    tests=subprocess.run(command,cwd=root,text=True,capture_output=True)
    (root/'outputs/phase5/validation/test_execution.log').write_text(tests.stdout+tests.stderr,encoding='utf-8'); print(tests.stdout,flush=True)
    suites=ET.parse(root/'outputs/phase5/validation/all_tests.xml').getroot().findall('testsuite')
    counts={k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
    before=json.loads((root/'outputs/phase5/validation/source_guard.json').read_text(encoding='utf-8'))
    result={**second,'tests':counts,'notebooks':notebooks,'tables_byte_identical':equal,'protected_artifacts_unchanged':protected_snapshot(root)==before}
    result['passed']=tests.returncode==0 and result['protected_artifacts_unchanged'] and all(n['unexecuted_code_cells']==n['error_outputs']==0 for n in notebooks)
    write_json(root/'outputs/phase5/validation/final_audit.json',result)
    from .phase5_reports import audit_report
    audit_report(result,configuration(root),root)
    if not result['passed']: raise AssertionError('Phase 5 audit failed')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--audit',action='store_true'); args=parser.parse_args()
    final_audit() if args.audit else run_phase5()
