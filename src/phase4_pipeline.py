"""Development selection is persisted before holdout execution; original artifacts are read-only."""
import argparse
import importlib.metadata
import json
import platform
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from .common import ROOT,sha256,write_json
from .sql_analytics import atomic_csv
from .forecast_config import configuration
from .forecast_data import load_forecasting_data,protected_snapshot
from .forecast_splits import folds
from .forecast_models import variants,fit_forecast
from .forecast_backtesting import backtest
from .forecast_metrics import grouped_metrics
from .forecast_selection import common_support,select_models,selected_rows
from .forecast_intervals import calibrate,add_intervals,coverage
from .forecast_reconciliation import hierarchy,independent_validation,operational_validation

def frozen_families(development,decisions):
    rows=[]
    for level,f in development.groupby('aggregation_level',sort=True):
        ridge=f[f.model.eq('ridge')]
        scores=grouped_metrics(common_support(ridge),['variant','alpha']).sort_values(['MASE','variant'])
        winner=decisions[decisions.aggregation_level.eq(level)].iloc[0]
        ridge_variant=winner.selected_variant if winner.selected_model=='ridge' else scores.iloc[0].variant
        for variant,g in f.groupby('variant',sort=True):
            model=g.model.iloc[0]
            if model!='ridge' or variant==ridge_variant:
                rows.append({'aggregation_level':level,'model':model,'variant':variant,
                             'alpha':float(g.alpha.iloc[0]) if model=='ridge' else None})
    return pd.DataFrame(rows)

def family_backtest(series,folds_table,family_configs,cfg):
    pieces=[]
    for level,f in family_configs.groupby('aggregation_level',sort=True):
        subset={sid:item for sid,item in series.items() if item['metadata']['aggregation_level']==level}
        settings=f[['model','variant','alpha']].to_dict('records')
        pieces.append(backtest(subset,folds_table,settings,cfg))
    return pd.concat(pieces,ignore_index=True)

def operational(series,decisions,calibration,cfg,data_version):
    rows=[]; model_records=[]; ets_states=[]; ridge_coefficients=[]
    all_variants={v['variant']:v for v in variants(cfg)}
    for r in decisions.itertuples():
        item=series[r.series_id]; train=item['values']; setting=all_variants[r.selected_variant]
        raw,prediction,parameters,artifacts=fit_forecast(train,cfg['forecast_horizons'],setting,cfg)
        model_records.append({'series_id':r.series_id,'model':setting['model'],'variant':setting['variant'],
                              'training_end_date':str(train.index[-1].date()),'training_observations':len(train),'parameters':parameters})
        if 'ets_fitted' in artifacts:
            for i,month in enumerate(train.index):
                ets_states.append({'series_id':r.series_id,'month':month,'actual':float(train.iloc[i]),
                                   'fitted':artifacts['ets_fitted'][i],'level':artifacts['ets_level'][i],'trend':artifacts['ets_trend'][i]})
        if 'ridge_coefficients' in artifacts:
            ridge_coefficients.extend({'series_id':r.series_id,**coefficient} for coefficient in artifacts['ridge_coefficients'])
        for i,h in enumerate(cfg['forecast_horizons']):
            rows.append({'series_id':r.series_id,'aggregation_level':r.aggregation_level,'target':cfg['primary_target'],
                         'model':setting['model'],'variant':setting['variant'],'training_end_date':train.index[-1],
                         'forecast_month':train.index[-1]+pd.DateOffset(months=h),'horizon':h,'prediction':float(prediction[i]),
                         'raw_prediction':float(raw[i]),'model_version':cfg['model_version'],'data_version':data_version,
                         'forecast_context':'Retrospective as of December 2025; not a live current forecast'})
    frame=add_intervals(pd.DataFrame(rows),calibration).rename(columns={'prediction':'point_forecast'})
    return frame,model_records,pd.DataFrame(ets_states,columns=['series_id','month','actual','fitted','level','trend']),pd.DataFrame(ridge_coefficients,columns=['series_id','horizon','feature','coefficient_per_standardized_feature'])

def robustness_tables(series,dev_folds,development,decisions,eligibility,cfg):
    rows=[]; scores=grouped_metrics(development,['aggregation_level','model','variant','horizon'])
    rows.extend(scores.assign(experiment='model and horizon',scenario='all development configurations').to_dict('records'))
    for window,policy,clip,label in [(cfg['sensitivity_windows'][0],'original',True,'trailing 24 months'),
                                     (None,'training_mad_clip',True,'training-only MAD clipping'),(None,'original',False,'unconstrained forecasts')]:
        print('Development-only sensitivity: '+label,flush=True)
        settings=variants(cfg); modified={**cfg,'nonnegative':clip}
        result=backtest(series,dev_folds,settings,modified,policy=policy,window=window)
        summary=grouped_metrics(result[result.model_status.eq('ok')],['aggregation_level','model','variant'])
        rows.extend(summary.assign(experiment='training and constraints',scenario=label).to_dict('records'))
        treatment=result[['series_id','origin_date','altered_training_rows']].drop_duplicates()
        rows.append({'experiment':'anomaly treatment count','scenario':label,'altered_rows_across_series_origins':int(treatment.altered_training_rows.sum())})
    for threshold in cfg['sensitivity_tie_thresholds']:
        selected=select_models(development,{**cfg,'selection_tie_relative':threshold},eligibility)
        for level,f in selected.groupby('aggregation_level'):
            rows.append({'experiment':'selection tie threshold','scenario':str(threshold),'aggregation_level':level,
                         'selected_variant':f.selected_variant.iloc[0],'selected_series':len(f)})
    for level,f in eligibility.groupby('aggregation_level'):
        rows.append({'experiment':'missingness and coverage','scenario':'initial-window only, no gap filling','aggregation_level':level,
                     'eligible_series':int(f.eligible.sum()),'incomplete_initial_series':int(f.initial_training_coverage_pct.lt(100).sum()),
                     'phase2_full_history_candidates':int(f.phase2_full_history_candidate.sum())})
    return pd.DataFrame(rows)

def run_phase4(root=ROOT,make_charts=True,make_reports=True,sensitivity=True):
    cfg=configuration(root); before=protected_snapshot(root)
    validation=root/'outputs/phase4/validation'; validation.mkdir(parents=True,exist_ok=True)
    guard=validation/'source_guard.json'
    if guard.exists() and json.loads(guard.read_text(encoding='utf-8'))!=before: raise AssertionError('Prior-phase artifacts changed since Phase 4 baseline')
    if not guard.exists(): write_json(guard,before)
    series,eligibility,populations,loaded,evidence=load_forecasting_data(cfg,root)
    calendar=next(iter(series.values()))['values'].index
    dev_folds=folds(calendar,cfg,'development'); hold_folds=folds(calendar,cfg,'holdout')
    print(f'Phase 4: {len(series)} training-eligible series; {len(dev_folds)} development and {len(hold_folds)} holdout origin/horizon cells',flush=True)
    development=backtest(series,dev_folds,variants(cfg),cfg)
    print('Development backtesting finished; freezing selection and interval support',flush=True)
    decisions=select_models(development,cfg,eligibility)
    families=frozen_families(development,decisions)
    chosen_development=selected_rows(development,decisions)
    calibration=calibrate(chosen_development,cfg)
    freeze={'configuration_sha256':sha256(root/'config/forecasting.yaml'),'development_last_target':str(dev_folds.target_date.max().date()),
            'holdout_first_target':cfg['final_holdout_start'],'selection_decisions':json.loads(decisions.to_json(orient='records',date_format='iso')),
            'family_configurations':json.loads(families.to_json(orient='records')),
            'interval_calibration':json.loads(calibration.to_json(orient='records')),
            'eligibility_ids':sorted(series),'selection_source':'development only; no holdout scores consulted'}
    frozen_path=validation/'frozen_development_decisions.json'; write_json(frozen_path,freeze); frozen_hash=sha256(frozen_path)
    # No holdout model call can occur before decisions/calibration are persisted.
    holdout=family_backtest(series,hold_folds,families,cfg)
    print('Final holdout backtesting finished with frozen configurations',flush=True)
    if sha256(frozen_path)!=frozen_hash: raise AssertionError('Development choices changed during holdout evaluation')
    combined=pd.concat([development,holdout],ignore_index=True)
    selected=selected_rows(combined,decisions)
    intervals=add_intervals(selected[selected.split_type.eq('holdout')],calibration)
    common=[]
    for level,f in development.groupby('aggregation_level'):
        chosen_configs=families[families.aggregation_level.eq(level)].variant
        common.append(common_support(f[f.variant.isin(chosen_configs)]))
    common_dev=pd.concat(common,ignore_index=True)
    common_hold=pd.concat([common_support(f) for _,f in holdout.groupby('aggregation_level')],ignore_index=True)
    comparable=pd.concat([common_dev,common_hold],ignore_index=True)
    model_dir=root/'outputs/phase4/models'; model_dir.mkdir(parents=True,exist_ok=True)
    op,model_records,ets_states,ridge_coefs=operational(series,decisions,calibration,cfg,sha256(root/'data/processed/monthly_prescribing.parquet'))
    op_keys=['forecast_month','horizon','training_end_date']
    op_direct=op[op.aggregation_level.eq('national')][op_keys+['point_forecast']].rename(columns={'point_forecast':'direct_national_forecast'})
    op_sum=op[op.aggregation_level.eq('regional')].groupby(op_keys).agg(regional_sum_forecast=('point_forecast',lambda s:s.sum(min_count=7)),regions=('series_id','nunique')).reset_index()
    op_aggregate=op_direct.merge(op_sum,on=op_keys,validate='one_to_one')
    op_aggregate['coherence_gap']=op_aggregate.regional_sum_forecast-op_aggregate.direct_national_forecast
    op_aggregate['forecast_context']='Retrospective as of December 2025; separate unreconciled approaches'
    write_json(model_dir/'selected_model_parameters.json',model_records)
    # These operational demonstrations fit the frozen national ETS/Ridge benchmark configs,
    # even if the selected model is another family. They are not used for selection.
    national=series['England']['values']
    if ets_states.empty or not ets_states.series_id.eq('England').any():
        _,_,_,artifact=fit_forecast(national,cfg['forecast_horizons'],{'model':'damped_ets','variant':'damped_ets','alpha':None},cfg)
        ets_states=pd.concat([ets_states,pd.DataFrame({'series_id':'England','month':national.index,'actual':national.values,
             'fitted':artifact['ets_fitted'],'level':artifact['ets_level'],'trend':artifact['ets_trend']})],ignore_index=True)
    if ridge_coefs.empty or not ridge_coefs.series_id.eq('England').any():
        setting=families[(families.aggregation_level=='national')&(families.model=='ridge')].iloc[0].to_dict()
        _,_,_,artifact=fit_forecast(national,cfg['forecast_horizons'],setting,cfg)
        ridge_coefs=pd.concat([ridge_coefs,pd.DataFrame([{'series_id':'England',**c} for c in artifact['ridge_coefficients']])],ignore_index=True)
    checks,aggregate,aggregate_scores=hierarchy(populations,selected)
    if checks.status.ne('passed').any(): raise AssertionError('Historical hierarchy inconsistent')
    independent=independent_validation(combined,series,decisions,cfg,eligibility)
    independent=pd.concat([independent,operational_validation(op,model_records,ets_states,series,cfg)],ignore_index=True)
    tables={'series_eligibility':eligibility,'development_folds':dev_folds,'holdout_folds':hold_folds,
            'backtest_predictions':combined,'development_model_metrics':grouped_metrics(common_dev,['aggregation_level','model','variant']),
            'development_configuration_metrics':grouped_metrics(development,['aggregation_level','model','variant']),
            'holdout_model_metrics':grouped_metrics(common_hold,['aggregation_level','model','variant']),
            'horizon_metrics':grouped_metrics(comparable,['split_type','aggregation_level','model','variant','horizon']),
            'regional_forecast_metrics':grouped_metrics(comparable[comparable.aggregation_level.eq('regional')],['split_type','region_code','region_name','model','variant']),
            'series_forecast_metrics':grouped_metrics(comparable,['split_type','aggregation_level','series_id','model','variant']),
            'forecast_bias_summary':grouped_metrics(comparable,['split_type','aggregation_level','model']),
            'model_selection_decisions':decisions,'frozen_family_configurations':families,'interval_calibration':calibration,
            'forecast_intervals':intervals,'interval_coverage_summary':coverage(intervals),
            'forecast_hierarchy_checks':checks,'aggregate_forecast_comparison':aggregate,'aggregate_forecast_metrics':aggregate_scores,
            'operational_forecasts':op,'operational_aggregate_comparison':op_aggregate,'ets_fitted_states':ets_states,'ridge_coefficients':ridge_coefs,
            'selected_forecast_metrics':grouped_metrics(selected,['split_type','aggregation_level','horizon']),
            'model_failures':combined[combined.model_status.ne('ok')].copy()}
    if sensitivity: tables['forecast_robustness_results']=robustness_tables(series,dev_folds,development,decisions,eligibility,cfg)
    exports={}
    for name,f in tables.items():
        path=root/f'outputs/phase4/tables/{name}.csv'; atomic_csv(f,path); parquet=path.with_suffix('.parquet'); f.to_parquet(parquet,index=False)
        exports[name]={'rows':len(f),'columns':f.columns.tolist(),'csv_sha256':sha256(path),'parquet_sha256':sha256(parquet)}
    atomic_csv(independent,validation/'forecast_validation.csv')
    chart_files=[]
    if make_charts:
        from .phase4_visualizations import charts
        chart_files=charts(tables,series,cfg,root)
    metadata={'python_version':platform.python_version(),'package_versions':{p:importlib.metadata.version(p) for p in ['pandas','numpy','scipy','statsmodels','scikit-learn','duckdb','pyarrow']},
              'configuration':cfg,'configuration_sha256':freeze['configuration_sha256'],'random_seed':cfg['random_seed'],
              'data_version':sha256(root/'data/processed/monthly_prescribing.parquet'),'model_version':cfg['model_version'],
              'prior_artifact_hashes':before,'frozen_decisions_sha256':frozen_hash}
    write_json(validation/'run_metadata.json',metadata)
    result={'passed':True,'series_count':len(series),'series_by_level':eligibility[eligibility.eligible].groupby('aggregation_level').size().to_dict(),
            'input_verification':evidence,'exports':exports,'charts':chart_files,'development_forecasts':len(development),
            'holdout_forecasts':len(holdout),'selected_holdout_forecasts':int(selected.split_type.eq('holdout').sum()),
            'independent_checks':len(independent),'independent_failed_checks':int(independent.status.ne('passed').sum()),
            'protected_artifacts':len(before),'protected_artifacts_unchanged':protected_snapshot(root)==before,
            'frozen_decisions_sha256':frozen_hash,'configuration_sha256':metadata['configuration_sha256'],'model_failures':int(combined.model_status.ne('ok').sum())}
    if not result['protected_artifacts_unchanged']: raise AssertionError('Prior artifacts changed')
    write_json(validation/'pipeline_summary.json',result)
    if make_reports:
        from .phase4_reports import reports
        reports(tables,result,cfg,root)
    print(f"Phase 4 complete: {len(development)} development / {len(holdout)} holdout forecasts; {len(independent)} independent checks",flush=True)
    return result

def final_audit(root=ROOT):
    first=run_phase4(root); second=run_phase4(root)
    equal=first['exports']==second['exports'] and first['frozen_decisions_sha256']==second['frozen_decisions_sha256']
    if not equal: raise AssertionError('Forecast table rerun differs')
    write_json(root/'outputs/phase4/validation/reproducibility.json',{'byte_identical':equal,'first_exports':first['exports'],'second_exports':second['exports']})
    return finish_audit(second,equal,root)

def finish_audit(second,equal,root=ROOT):
    """Finish verification using existing, hash-verified two-run evidence."""
    evidence=json.loads((root/'outputs/phase4/validation/reproducibility.json').read_text(encoding='utf-8'))
    if not equal or not evidence['byte_identical'] or evidence['first_exports']!=evidence['second_exports'] or evidence['second_exports']!=second['exports']:
        raise AssertionError('Two-run evidence is inconsistent')
    for stem,item in second['exports'].items():
        for suffix in ['csv','parquet']:
            if sha256(root/f'outputs/phase4/tables/{stem}.{suffix}')!=item[f'{suffix}_sha256']:
                raise AssertionError('Recorded two-run table changed')
    if sha256(root/'outputs/phase4/validation/frozen_development_decisions.json')!=second['frozen_decisions_sha256']:
        raise AssertionError('Frozen decisions changed')
    from .phase4_notebooks import build_and_execute
    notebooks=build_and_execute(root)
    # Earlier integration tests overwrite their own summary. Preserve its exact bytes during tests.
    summary=root/'outputs/phase3/validation/pipeline_summary.json'; old=summary.read_bytes()
    command=[sys.executable,'-m','pytest','-q','-p','no:cacheprovider',f'--basetemp=outputs/phase4/validation/tests_tmp_{uuid.uuid4().hex[:8]}','--junitxml=outputs/phase4/validation/all_tests.xml']
    try: tests=subprocess.run(command,cwd=root,text=True,capture_output=True)
    finally: summary.write_bytes(old)
    (root/'outputs/phase4/validation/test_execution.log').write_text(tests.stdout+tests.stderr,encoding='utf-8'); print(tests.stdout,flush=True)
    suites=ET.parse(root/'outputs/phase4/validation/all_tests.xml').getroot().findall('testsuite')
    counts={k:sum(int(s.get(k,0)) for s in suites) for k in ['tests','failures','errors','skipped']}
    result={**second,'tests':counts,'notebooks':notebooks,'tables_byte_identical':equal,
            'protected_artifacts_unchanged':protected_snapshot(root)==json.loads((root/'outputs/phase4/validation/source_guard.json').read_text(encoding='utf-8'))}
    result['passed']=tests.returncode==0 and result['protected_artifacts_unchanged'] and all(n['error_outputs']==0 and n['unexecuted_code_cells']==0 for n in notebooks)
    write_json(root/'outputs/phase4/validation/final_audit.json',result)
    from .phase4_reports import audit_report
    audit_report(result,configuration(root),root)
    if not result['passed']: raise AssertionError('Phase 4 final audit failed')
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--audit',action='store_true'); args=parser.parse_args()
    final_audit() if args.audit else run_phase4()
