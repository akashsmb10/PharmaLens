"""Development-only pooled-level selection and strict common support."""
import numpy as np
import pandas as pd
from .forecast_metrics import grouped_metrics

def common_support(frame):
    keys=['series_id','origin_date','target_date','horizon']
    variants=frame.variant.unique()
    counts=frame[frame.model_status.eq('ok')&frame.prediction.notna()].groupby(keys).variant.nunique()
    good=counts[counts==len(variants)].reset_index()[keys]
    return frame.merge(good,on=keys,how='inner',validate='many_to_one')

def select_models(development,cfg,eligibility):
    if not development.split_type.eq('development').all() or (development.target_date>pd.Timestamp(cfg['development_end'])).any():
        raise ValueError('Selection accepts development observations only')
    rows=[]
    for level,f in development.groupby('aggregation_level',sort=True):
        complete=f.groupby('variant').model_status.apply(lambda s:s.eq('ok').all())
        eligible=complete[complete].index.tolist()
        comparable=common_support(f[f.variant.isin(eligible)])
        scores=grouped_metrics(comparable,['variant','model'])
        scores=scores[scores.MASE.notna()].sort_values(['MASE','MAE','variant'])
        if scores.empty: raise ValueError('No comparable models for '+level)
        best=scores.iloc[0]; near=scores[scores.MASE<=best.MASE*(1+cfg['selection_tie_relative'])+1e-12].copy()
        near['simplicity']=near.model.map({m:i for i,m in enumerate(cfg['simplicity_order'])})
        # Larger Ridge alpha gets deterministic preference for otherwise equal family scores.
        near['ridge_alpha']=near.variant.map(lambda name:float(name.split('_')[-1]) if name.startswith('ridge_alpha_') else 0.)
        selected=near.sort_values(['simplicity','ridge_alpha','variant'],ascending=[True,False,True]).iloc[0]
        runners=scores[scores.variant!=selected.variant]
        for item in eligibility[eligibility.eligible & eligibility.aggregation_level.eq(level)].itertuples():
            rows.append({'series_id':item.series_id,'aggregation_level':level,'selected_model':selected.model,
                         'selected_variant':selected.variant,'selection_metric':'MASE','development_score':float(selected.MASE),
                         'runner_up':runners.iloc[0].variant if len(runners) else None,
                         'eligible_models':';'.join(eligible),'selection_sample_size':int(selected.n),
                         'series_sample_size':int(len(comparable[comparable.series_id.eq(item.series_id)&comparable.variant.eq(selected.variant)])),
                         'selection_scope':'Shared by aggregation level; pooled mean scaled absolute error',
                         'tie_threshold_relative':cfg['selection_tie_relative'],
                         'tie_breaking_reason':'Simplicity preference within relative MASE tolerance; deterministic alpha tie break',
                         'frozen_at':pd.Timestamp(cfg['development_end'])})
    return pd.DataFrame(rows)

def selected_rows(frame,decisions):
    return frame.merge(decisions[['series_id','selected_variant']],on='series_id',validate='many_to_one').query('variant == selected_variant').drop(columns='selected_variant')
