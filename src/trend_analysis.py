"""Short-series trend effects; HAC intervals describe model uncertainty only."""
import numpy as np
import pandas as pd
from scipy.stats import theilslopes, kendalltau
import statsmodels.api as sm
from .statistical_analysis import calendar_series, METRICS

def estimate_trend(series, hac_lags=3, month_controls=False):
    s=series.sort_index()
    # Elapsed calendar time remains intact when observations are missing.
    t=np.arange(len(s),dtype=float)
    ok=s.notna().to_numpy()
    y=s.to_numpy(dtype=float)[ok]; x=t[ok]
    base={'observed_months':len(y),'missing_months':len(s)-len(y),'hac_lags':hac_lags,
          'specification':'linear + month indicators' if month_controls else 'linear',
          'interpretation':'Descriptive trend; HAC intervals conditional on short-series model, not causal'}
    if len(y)<24 or np.ptp(x)==0:
        return {**base,'status':'skipped: fewer than 24 observed months'}
    design=pd.DataFrame({'intercept':np.ones(len(y)),'elapsed_month':x})
    if month_controls:
        months=pd.get_dummies(pd.Series(s.index.month[ok]),prefix='month',drop_first=True,dtype=float)
        design=pd.concat([design,months],axis=1)
    fit=sm.OLS(y,design).fit(cov_type='HAC',cov_kwds={'maxlags':hac_lags,'use_correction':True},use_t=True)
    low,high=fit.conf_int().loc['elapsed_month']
    robust=theilslopes(y,x)
    tau=kendalltau(x,y).statistic
    result={**base,'status':'estimated','ols_slope_per_month':fit.params['elapsed_month'],
            'hac_ci_low':low,'hac_ci_high':high,'annual_linear_effect':12*fit.params['elapsed_month'],
            'annual_linear_effect_pct_of_mean':1200*fit.params['elapsed_month']/np.mean(y) if np.mean(y)>0 else np.nan,
            'theil_sen_slope_per_month':robust.slope,'kendall_tau_descriptive':tau,
            'r_squared':fit.rsquared,'residual_sd':np.std(fit.resid,ddof=1),
            'residual_cv':np.std(fit.resid,ddof=1)/np.mean(y) if np.mean(y)>0 else np.nan,
            'residual_lag1_correlation':pd.Series(fit.resid).autocorr(1) if ok.all() else np.nan}
    if not ok.all():
        # Standard HAC uses row lags. Compressing gaps would misidentify calendar lags.
        result['hac_ci_low']=np.nan; result['hac_ci_high']=np.nan
        result['interpretation']='Descriptive elapsed-calendar slope; HAC interval withheld for incomplete history'
    if (y>0).all():
        logfit=sm.OLS(np.log(y),design).fit(cov_type='HAC',cov_kwds={'maxlags':hac_lags,'use_correction':True},use_t=True)
        result['log_linear_annual_change_pct']=100*np.expm1(12*logfit.params['elapsed_month'])
    else:
        result['log_linear_annual_change_pct']=np.nan
    return result

def trend_tables(populations, calendar):
    result={}
    for level in ['national','regional','presentation']:
        frame,keys=populations[level]; rows=[]
        groups=frame.groupby(keys,sort=True) if keys else [('England',frame)]
        for key,f in groups:
            key=key if isinstance(key,tuple) else (key,)
            identity=dict(zip(keys,key)) if keys else {}
            for metric in METRICS:
                rows.append({'level':level,**identity,'metric':metric,
                             **estimate_trend(calendar_series(f,metric,calendar))})
        result[level]=pd.DataFrame(rows)
    return result
