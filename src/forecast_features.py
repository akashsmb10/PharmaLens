"""Compact direct-horizon features; origin includes y(t), target is y(t+h)."""
import numpy as np
import pandas as pd

def origin_features(series,position,horizon,cfg):
    lags=cfg['ridge_lags']; window=cfg['ridge_rolling_months']
    if position<max(max(lags)-1,window-1): raise ValueError('Insufficient lag history')
    history=series.iloc[:position+1]
    # lag_1 means the last observation before the h=1 target; shared origin features for h>1.
    row={f'lag_{lag}':float(history.iloc[-lag]) for lag in lags}
    row['prior_rolling_mean']=float(history.iloc[-window:].mean())
    target=series.index[position]+pd.DateOffset(months=horizon)
    row['target_month_sin']=float(np.sin(2*np.pi*target.month/12))
    row['target_month_cos']=float(np.cos(2*np.pi*target.month/12))
    return row

def supervised_pairs(training,horizon,cfg):
    rows=[]; targets=[]; provenance=[]
    first=max(max(cfg['ridge_lags'])-1,cfg['ridge_rolling_months']-1)
    for position in range(first,len(training)-horizon):
        rows.append(origin_features(training,position,horizon,cfg)); targets.append(float(training.iloc[position+horizon]))
        provenance.append({'feature_origin':training.index[position],'target_date':training.index[position+horizon]})
    return pd.DataFrame(rows),np.asarray(targets),pd.DataFrame(provenance)
