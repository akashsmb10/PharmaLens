"""Three-cycle seasonality diagnostics, not confirmation of stable annual seasonality."""
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import acf
from statsmodels.tsa.seasonal import STL
from .statistical_analysis import calendar_series, METRICS

def seasonal_indices(series):
    s=series.sort_index()
    means=s.groupby(s.index.year).transform('mean')
    normalized=100*s/means.where(means!=0)
    f=pd.DataFrame({'month':s.index,'calendar_year':s.index.year,'calendar_month':s.index.month,
                    'value':s.values,'annual_mean_index':normalized.values})
    f['per_calendar_day']=f.value/f.month.dt.days_in_month
    day_mean=f.groupby('calendar_year').per_calendar_day.transform('mean')
    f['day_adjusted_index']=100*f.per_calendar_day/day_mean.where(day_mean!=0)
    return f

def seasonality(series):
    s=series.sort_index()
    indices=seasonal_indices(s)
    summary={'observed_months':int(s.notna().sum()),'annual_cycles':len(s)/12,
             'interpretation':'Exploratory: only three annual cycles; indices retain within-year trend'}
    diagnostics=[]; components=pd.DataFrame()
    if s.isna().any() or len(s)<24:
        summary['status']='ACF/STL skipped: incomplete or short calendar history'
        return summary,indices,pd.DataFrame(columns=['lag','acf']),components
    values=acf(s.to_numpy(dtype=float),nlags=min(24,len(s)-1),fft=False)
    fit=STL(s,period=12,robust=True).fit()
    residual=np.asarray(fit.resid); seasonal=np.asarray(fit.seasonal)
    denominator=np.var(residual+seasonal)
    strength=max(0,1-np.var(residual)/denominator) if denominator>0 else np.nan
    # Remove linear trend before inspecting annual autocorrelation.
    x=np.arange(len(s)); detrended=s.values-np.polyval(np.polyfit(x,s.values,1),x)
    adjusted=acf(detrended,nlags=min(24,len(s)-1),fft=False)
    for lag,value in enumerate(values):
        diagnostics.append({'lag':lag,'acf':value,'detrended_acf':adjusted[lag],
                            'interpretation':'Descriptive autocorrelation; no iid significance bounds'})
    matrix=indices.pivot(index='calendar_month',columns='calendar_year',values='annual_mean_index')
    corr=matrix.corr().to_numpy(); off=corr[np.triu_indices(len(corr),1)]
    summary.update(status='exploratory complete series',acf_lag12=values[12],
                   detrended_acf_lag12=adjusted[12],stl_seasonal_strength=strength,
                   mean_year_profile_correlation=np.nanmean(off),
                   raw_seasonal_index_range=indices.groupby('calendar_month').annual_mean_index.mean().max()-indices.groupby('calendar_month').annual_mean_index.mean().min(),
                   day_adjusted_index_range=indices.groupby('calendar_month').day_adjusted_index.mean().max()-indices.groupby('calendar_month').day_adjusted_index.mean().min())
    components=pd.DataFrame({'month':s.index,'observed':s.values,'trend':fit.trend.values,
                             'seasonal':fit.seasonal.values,'residual':fit.resid.values})
    return summary,indices,pd.DataFrame(diagnostics),components

def seasonality_tables(national, calendar):
    summaries=[]; indices=[]; correlations=[]; decompositions=[]
    for metric in METRICS:
        summary,index,correlation,components=seasonality(calendar_series(national,metric,calendar))
        summaries.append({'metric':metric,**summary})
        for f,out in [(index,indices),(correlation,correlations),(components,decompositions)]:
            f['metric']=metric; out.append(f)
    return pd.DataFrame(summaries),pd.concat(indices,ignore_index=True),pd.concat(correlations,ignore_index=True),pd.concat(decompositions,ignore_index=True)
