"""Independent Python/math checks and transparent direct-versus-regional sums."""
import math
import json
import numpy as np
import pandas as pd
from .forecast_metrics import grouped_metrics

def hierarchy(populations,selected):
    national=populations['national'][0].set_index('month').prescription_items
    reg=populations['regional'][0]
    detail=populations['region_presentation'][0]
    rows=[]
    for month,expected in national.items():
        actual=reg.loc[reg.month.eq(month),'prescription_items'].sum()
        rows.append({'check':'national actual equals all seven regions','month':month,'region_code':None,
                     'expected':float(expected),'observed':float(actual),'difference':float(actual-expected),'status':'passed' if actual==expected else 'failed'})
    subtotal=detail.groupby(['month','region_code']).prescription_items.sum(min_count=1)
    for r in reg.itertuples():
        observed=subtotal.loc[(r.month,r.region_code)]
        rows.append({'check':'regional actual equals all observed presentations','month':r.month,'region_code':r.region_code,
                     'expected':float(r.prescription_items),'observed':float(observed),'difference':float(observed-r.prescription_items),
                     'status':'passed' if observed==r.prescription_items else 'failed'})
    keys=['split_type','origin_date','target_date','horizon']
    a=selected[selected.aggregation_level.eq('national')][keys+['actual','prediction','mase_scale']].rename(columns={'prediction':'direct_national'})
    b=selected[selected.aggregation_level.eq('regional')].groupby(keys).agg(regional_sum=('prediction',lambda s:s.sum(min_count=7)),regions=('series_id','nunique')).reset_index()
    compare=a.merge(b,on=keys,validate='one_to_one')
    compare['coherence_gap']=compare.regional_sum-compare.direct_national
    compare['coherence_gap_pct']=100*compare.coherence_gap/compare.direct_national.where(compare.direct_national!=0)
    compare['direct_error']=compare.direct_national-compare.actual; compare['regional_sum_error']=compare.regional_sum-compare.actual
    metrics_rows=[]
    for approach,col in [('direct_national','direct_national'),('sum_all_seven_regions','regional_sum')]:
        f=compare.rename(columns={col:'prediction'})
        scores=grouped_metrics(f,['split_type','horizon']); scores['approach']=approach; metrics_rows.append(scores)
    return pd.DataFrame(rows),compare,pd.concat(metrics_rows,ignore_index=True)

def independent_validation(predictions,series,decisions,cfg,eligibility):
    """Recompute baselines and metrics without calling their production implementations."""
    checks=[]
    def check(name,expected,observed,tolerance=1e-8):
        equal=(pd.isna(expected) and pd.isna(observed)) or (not pd.isna(expected) and not pd.isna(observed) and abs(float(observed)-float(expected))<=tolerance)
        checks.append({'check_name':name,'expected':expected,'observed':observed,
                       'difference':float(observed)-float(expected) if not pd.isna(expected) and not pd.isna(observed) else np.nan,
                       'tolerance':tolerance,'status':'passed' if equal else 'failed'})
    keys=['series_id','variant','origin_date','horizon','split_type']
    check('unique prediction rows',0,predictions.duplicated(keys).sum(),0)
    check('all forecast dates strictly later than origins',0,(predictions.target_date<=predictions.origin_date).sum(),0)
    check('all holdout origins after development freeze',0,((predictions.split_type=='holdout')&(predictions.origin_date<pd.Timestamp(cfg['development_end']))).sum(),0)
    for stage,f in predictions.groupby('split_type'):
        # Enumerate allowed calendar cells independently of forecast_splits.folds.
        for sid,item in series.items():
            calendar=item['values'].index; count=0
            for n in range(cfg['initial_training_months'],len(calendar)):
                origin=calendar[n-1]
                for h in cfg['forecast_horizons']:
                    target=origin+pd.DateOffset(months=h)
                    if target not in calendar: continue
                    valid=target<=pd.Timestamp(cfg['development_end']) if stage=='development' else origin>=pd.Timestamp(cfg['development_end']) and pd.Timestamp(cfg['final_holdout_start'])<=target<=pd.Timestamp(cfg['final_holdout_end'])
                    count+=int(valid)
            subset=f[f.series_id.eq(sid)]
            check(f'forecast count:{stage}:{sid}',count*subset.variant.nunique(),len(subset),0)
    training_cache={}
    feature_cache={}
    for i,r in enumerate(predictions.itertuples()):
        sid=series[r.series_id]['values']; training=sid.loc[:r.origin_date]
        check(f'date:{i}',int(r.horizon),(r.target_date.year-r.origin_date.year)*12+r.target_date.month-r.origin_date.month,0)
        check(f'actual:{i}',float(sid.loc[r.target_date]),r.actual,0)
        cache_key=(r.series_id,r.origin_date)
        if cache_key not in training_cache:
            training_cache[cache_key]=sum(abs(float(training.iloc[j])-float(training.iloc[j-1])) for j in range(1,len(training)))/(len(training)-1)
        scale=training_cache[cache_key]
        check(f'MASE denominator:{i}',scale if scale>0 else np.nan,r.mase_scale,1e-8)
        if r.model_status!='ok': continue
        expected=None
        if r.model=='naive': expected=float(training.iloc[-1])
        elif r.model=='seasonal_naive': expected=float(training.loc[r.target_date-pd.DateOffset(months=cfg['seasonal_period'])])
        elif r.model=='drift': expected=float(training.iloc[-1])+r.horizon*(float(training.iloc[-1])-float(training.iloc[0]))/(len(training)-1)
        if expected is not None:
            check(f'{r.model} raw:{i}',expected,r.raw_prediction,1e-7)
            check(f'{r.model} final:{i}',max(expected,0) if cfg['nonnegative'] else expected,r.prediction,1e-7)
        if r.model=='ridge':
            details=json.loads(r.model_configuration)['horizons']
            detail=next(d for d in details if d['horizon']==r.horizon)
            check(f'Ridge latest label:{i}',0,int(pd.Timestamp(detail['latest_training_target'])>r.origin_date),0)
            check(f'Ridge effective rows:{i}',len(training)-r.horizon-2,detail['supervised_rows'],0)
            fk=(r.series_id,r.origin_date,r.horizon)
            if fk not in feature_cache:
                independent_rows=[]
                for pos in range(2,len(training)-r.horizon):
                    values=[float(training.iloc[pos]),float(training.iloc[pos-1]),float(training.iloc[pos-2])]
                    month=(training.index[pos]+pd.DateOffset(months=int(r.horizon))).month
                    independent_rows.append(values+[sum(values)/3,math.sin(2*math.pi*month/12),math.cos(2*math.pi*month/12)])
                feature_cache[fk]=np.asarray(independent_rows).mean(axis=0)
            difference=np.max(np.abs(feature_cache[fk]-np.asarray(detail['scaler_mean'])))
            check(f'Ridge training-only scaler:{i}',0,difference,1e-7)
    # Independent individual-error metrics for each stage/level/family on recorded common support.
    from .forecast_selection import common_support
    for (stage,level),subset in predictions.groupby(['split_type','aggregation_level']):
        comparable=common_support(subset)
        scored=grouped_metrics(comparable,['variant'])
        for r in scored.itertuples():
            f=comparable[comparable.variant.eq(r.variant)].dropna(subset=['actual','prediction'])
            errors=[float(p-a) for a,p in zip(f.actual,f.prediction)]; n=len(errors)
            if not n: continue
            denom=sum(abs(float(a)) for a in f.actual)
            values={'MAE':sum(abs(e) for e in errors)/n,'RMSE':math.sqrt(sum(e*e for e in errors)/n),
                    'WAPE':100*sum(abs(e) for e in errors)/denom if denom else np.nan,'Bias':sum(errors)/n,
                    'sMAPE':sum(0 if abs(a)+abs(p)==0 else 200*abs(p-a)/(abs(a)+abs(p)) for a,p in zip(f.actual,f.prediction))/n}
            scaled=[abs(e)/scale for e,scale in zip(errors,f.mase_scale) if pd.notna(scale) and scale>0]
            values['MASE']=sum(scaled)/len(scaled) if scaled else np.nan
            for metric,value in values.items(): check(f'metric:{stage}:{level}:{r.variant}:{metric}',value,getattr(r,metric),1e-7)
    # Independent development ranking/tie preference, with model-family availability guard.
    development=predictions[predictions.split_type.eq('development')]
    for level,f in development.groupby('aggregation_level'):
        good=f.groupby('variant').model_status.apply(lambda s:s.eq('ok').all()); valid=good[good].index
        f=f[f.variant.isin(valid)]; scores=[]
        for variant,g in f.groupby('variant'):
            score=sum(abs(p-a)/scale for a,p,scale in zip(g.actual,g.prediction,g.mase_scale))/len(g)
            scores.append((variant,g.model.iloc[0],score))
        best=min(s[2] for s in scores)
        near=[s for s in scores if s[2]<=best*(1+cfg['selection_tie_relative'])+1e-12]
        chosen=sorted(near,key=lambda x:(cfg['simplicity_order'].index(x[1]),-float(x[0].split('_')[-1]) if x[1]=='ridge' else 0,x[0]))[0]
        actual=decisions[decisions.aggregation_level.eq(level)]
        check(f'selection:{level}',0,int((actual.selected_variant!=chosen[0]).sum()),0)
        check(f'selection score:{level}',chosen[2],actual.development_score.iloc[0],1e-10)
    # Candidate membership from the initial window only, ignoring full-history inventory labels.
    for sid,item in series.items():
        training=item['values'].iloc[:cfg['initial_training_months']]
        check(f'eligible contiguous:{sid}',cfg['initial_training_months'],int(training.notna().sum()),0)
        if item['metadata']['aggregation_level']=='region_presentation':
            check(f'eligible volume:{sid}',1,int(training.sum()>=cfg['minimum_training_total_items']),0)
    result=pd.DataFrame(checks)
    if result.status.ne('passed').any(): raise AssertionError('Independent forecast checks failed: '+str(result[result.status.ne('passed')].head().to_dict('records')))
    return result

def operational_validation(frame,model_records,ets_states,series,cfg):
    """Use fitted state/linear coefficients to check predictions through separate equations."""
    parameters={r['series_id']:r['parameters'] for r in model_records}; rows=[]
    for r in frame.itertuples():
        train=series[r.series_id]['values']; p=parameters[r.series_id]
        if r.model=='damped_ets':
            state=ets_states[ets_states.series_id.eq(r.series_id)].sort_values('month').iloc[-1]
            expected=float(state.level)+float(state.trend)*sum(float(p['damping_trend'])**i for i in range(1,r.horizon+1))
        elif r.model=='ridge':
            d=next(item for item in p['horizons'] if item['horizon']==r.horizon)
            lag=[float(train.iloc[-1]),float(train.iloc[-2]),float(train.iloc[-3])]
            month=r.forecast_month.month
            x=np.asarray(lag+[sum(lag)/3,math.sin(2*math.pi*month/12),math.cos(2*math.pi*month/12)])
            expected=float(d['intercept'])+float(np.dot((x-np.asarray(d['scaler_mean']))/np.asarray(d['scaler_scale']),d['coefficients']))
        elif r.model=='naive': expected=float(train.iloc[-1])
        elif r.model=='seasonal_naive': expected=float(train.loc[r.forecast_month-pd.DateOffset(months=cfg['seasonal_period'])])
        elif r.model=='drift': expected=float(train.iloc[-1])+r.horizon*(float(train.iloc[-1])-float(train.iloc[0]))/(len(train)-1)
        else: raise ValueError('Unexpected operational model')
        if cfg['nonnegative']: expected=max(0,expected)
        difference=float(r.point_forecast)-expected
        rows.append({'check_name':f'operational equation:{r.series_id}:{r.horizon}','expected':expected,'observed':r.point_forecast,
                     'difference':difference,'tolerance':1e-6,'status':'passed' if abs(difference)<=1e-6 else 'failed'})
    result=pd.DataFrame(rows)
    if result.status.ne('passed').any(): raise AssertionError('Independent operational equation failed')
    return result
