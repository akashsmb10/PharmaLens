"""Five actual families. Failures remain unavailable; no label-preserving fallbacks."""
import json
import warnings
import numpy as np
import pandas as pd
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from .forecast_features import origin_features,supervised_pairs

class ForecastFitFailure(RuntimeError):
    def __init__(self,message,metadata):
        super().__init__(message); self.metadata=metadata

def variants(cfg):
    return [{'model':m,'variant':m,'alpha':None} for m in cfg['models'] if m!='ridge']+[
        {'model':'ridge','variant':f'ridge_alpha_{alpha:g}','alpha':alpha} for alpha in cfg['ridge_alphas']]

def fit_forecast(training,horizons,variant,cfg):
    s=training.sort_index().astype(float)
    if s.index.has_duplicates or s.isna().any() or not np.isfinite(s).all(): raise ValueError('Complete finite training history required; gaps are not imputed')
    if not pd.DatetimeIndex(s.index).as_unit('ns').equals(pd.date_range(s.index.min(),s.index.max(),freq='MS')):
        raise ValueError('Contiguous monthly training history required')
    model=variant['model']; h=np.asarray(horizons,dtype=int); artifacts={}
    if model=='naive':
        raw=np.repeat(s.iloc[-1],len(h)); parameters={'last':float(s.iloc[-1])}
    elif model=='seasonal_naive':
        if len(s)<cfg['seasonal_period']: raise ValueError('Seasonal lag unavailable')
        values=[]
        for horizon in h:
            lag_date=s.index[-1]+pd.DateOffset(months=int(horizon)-cfg['seasonal_period'])
            if lag_date not in s.index or lag_date>s.index[-1]: raise ValueError('Seasonal target lag unavailable at origin')
            values.append(float(s.loc[lag_date]))
        raw=np.asarray(values); parameters={'seasonal_period':cfg['seasonal_period']}
    elif model=='drift':
        if len(s)<2: raise ValueError('At least two observations needed for drift')
        slope=(s.iloc[-1]-s.iloc[0])/(len(s)-1)
        raw=s.iloc[-1]+h*slope; parameters={'drift':float(slope)}
    elif model=='damped_ets':
        if len(s)<cfg['ets_minimum_months']: raise ValueError('Damped ETS history below configured minimum')
        # Scaling reduces numerical conditioning differences across series; inverse is exact.
        scale=float(s.mean()) if s.mean()>0 else 1.
        with warnings.catch_warnings(record=True) as messages:
            warnings.simplefilter('always')
            fit=ExponentialSmoothing(s/scale,trend='add',damped_trend=True,seasonal=None,
                initialization_method='estimated',bounds={'damping_trend':tuple(cfg['ets_damping_bounds'])}).fit(
                optimized=True,method='L-BFGS-B',use_brute=False,minimize_kwargs={'options':{'maxiter':cfg['ets_max_iterations']}})
        success=bool(fit.mle_retvals.get('success',False))
        if not success:
            raise ForecastFitFailure('ETS optimization failed: '+str(fit.mle_retvals.get('message','unknown')),
                                     {'trend':'add','damped':True,'seasonal':None,'scale':scale,'optimization_success':False,
                                      'warnings':[str(w.message) for w in messages]})
        raw=np.asarray(fit.forecast(int(h.max())))[h-1]*scale
        parameters={k:float(fit.params[k]) for k in ['smoothing_level','smoothing_trend','damping_trend','initial_level','initial_trend']}
        parameters.update(trend='add',damped=True,seasonal=None,scale=scale,optimization_success=success,
                          warnings=[str(w.message) for w in messages])
        artifacts['ets_fitted']=np.asarray(fit.fittedvalues)*scale
        artifacts['ets_level']=np.asarray(fit.level)*scale; artifacts['ets_trend']=np.asarray(fit.trend)*scale
    elif model=='ridge':
        raw=[]; details=[]; coefficients=[]
        for horizon in h:
            x,y,provenance=supervised_pairs(s,int(horizon),cfg)
            if len(y)<cfg['ridge_minimum_rows']: raise ValueError('Ridge effective supervised rows below configured minimum')
            if provenance.target_date.max()>s.index[-1]: raise AssertionError('Direct target leaks beyond training cutoff')
            pipe=make_pipeline(StandardScaler(),Ridge(alpha=float(variant['alpha']),solver='svd'))
            pipe.fit(x,y)
            future=pd.DataFrame([origin_features(s,len(s)-1,int(horizon),cfg)],columns=x.columns)
            raw.append(float(pipe.predict(future)[0]))
            scaler=pipe.named_steps['standardscaler']; estimator=pipe.named_steps['ridge']
            details.append({'horizon':int(horizon),'supervised_rows':len(y),'feature_count':len(x.columns),
                            'latest_training_target':str(provenance.target_date.max().date()),'scaler_mean':scaler.mean_.tolist(),
                            'scaler_scale':scaler.scale_.tolist(),'intercept':float(estimator.intercept_),
                            'features':x.columns.tolist(),'coefficients':estimator.coef_.tolist()})
            coefficients.extend({'horizon':int(horizon),'feature':name,'coefficient_per_standardized_feature':float(value)} for name,value in zip(x.columns,estimator.coef_))
        raw=np.asarray(raw); parameters={'alpha':float(variant['alpha']),'strategy':'direct','horizons':details}
        artifacts['ridge_coefficients']=coefficients
    else: raise ValueError('Unknown model '+model)
    if not np.isfinite(raw).all(): raise RuntimeError('Nonfinite model prediction')
    prediction=np.maximum(raw,0) if cfg['nonnegative'] else np.asarray(raw)
    return np.asarray(raw),prediction,parameters,artifacts
