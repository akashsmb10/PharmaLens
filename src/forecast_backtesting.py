"""Origin-sliced fits; retain attempted forecasts and failures as rows."""
import json
import numpy as np
import pandas as pd
from .forecast_models import fit_forecast
from .forecast_metrics import mase_scale

def training_policy(training,cfg,policy='original',window=None):
    s=training.copy()
    if window is not None: s=s.iloc[-window:]
    altered=0
    if policy=='training_mad_clip':
        median=s.median(); mad=(s-median).abs().median()
        if len(s)>=12 and mad>0:
            distance=cfg['anomaly_sensitivity_z']*mad/.6744897501960817
            clipped=s.clip(lower=max(0,median-distance),upper=median+distance)
            altered=int((clipped!=s).sum()); s=clipped
    return s,altered

def backtest(series,folds,variants,cfg,policy='original',window=None):
    rows=[]
    for sid,item in sorted(series.items()):
        source=item['values']; metadata=item['metadata']
        for origin,group in folds.groupby('origin_date',sort=True):
            original=source.loc[:origin].copy()
            train,changed=training_policy(original,cfg,policy,window)
            scale=mase_scale(original) # Stable reference even when sensitivity changes training policy.
            horizons=sorted(group.horizon.tolist())
            for variant in variants:
                status='ok'; error=''; parameters={}; predictions=np.full(len(horizons),np.nan); raw=predictions.copy()
                try:
                    raw,predictions,parameters,_=fit_forecast(train,horizons,variant,cfg)
                except Exception as exc:
                    status='failed'; error=f'{type(exc).__name__}: {exc}'
                    parameters=getattr(exc,'metadata',{'requested_model':variant['model'],'requested_variant':variant['variant']})
                for j,h in enumerate(horizons):
                    split=group[group.horizon==h].iloc[0]
                    rows.append({'series_id':sid,'aggregation_level':metadata['aggregation_level'],'target':cfg['primary_target'],
                                 'region_code':metadata.get('region_code'),'region_name':metadata.get('region_name'),
                                 'presentation_key':metadata.get('presentation_key'),'presentation_name':metadata.get('presentation_name'),
                                 'unit_of_measure':metadata.get('unit_of_measure'),'model':variant['model'],'variant':variant['variant'],
                                 'alpha':variant['alpha'],'origin_date':origin,'target_date':split.target_date,'horizon':int(h),
                                 'actual':float(source.loc[split.target_date]),'prediction':float(predictions[j]),'raw_prediction':float(raw[j]),
                                 'train_observations':len(train),'training_start_date':train.index[0],
                                 'split_id':split.split_id,'split_type':split.split_type,'model_status':status,'failure_reason':error,
                                 'mase_scale':scale,'model_configuration':json.dumps(parameters,sort_keys=True,separators=(',',':')),
                                 'training_policy':policy,'altered_training_rows':changed,'nonnegative':cfg['nonnegative']})
    return pd.DataFrame(rows)
