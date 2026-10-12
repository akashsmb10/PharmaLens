"""Deterministic sensitivities; exclusions apply to diagnostic copies only."""
import numpy as np
import pandas as pd
from .statistical_analysis import calendar_series, describe_series, METRICS
from .trend_analysis import estimate_trend
from .seasonality_analysis import seasonality

def robustness(populations, flags, coverage, calendar):
    nat=populations['national'][0]; rows=[]
    # A: largest five original flags by within-series IQR-distance (not mixed-unit magnitude).
    f=flags.copy(); width=f.q3-f.q1
    f['scaled_excess']=np.maximum(f.value-f.upper_fence,f.lower_fence-f.value)/width.where(width>0)
    selected=f.sort_values(['scaled_excess','month','region_code','presentation_key','metric'],ascending=[False,True,True,True,True]).drop_duplicates(['month','region_code','presentation_key']).head(5)
    detail=populations['region_presentation'][0].copy()
    exclusions=selected[['month','region_code','presentation_key']].assign(excluded=True)
    marked=detail.merge(exclusions,on=['month','region_code','presentation_key'],how='left',validate='one_to_one')
    for metric in METRICS:
        s=calendar_series(nat,metric,calendar); reference=estimate_trend(s)
        for lag,controls in [(1,False),(3,False),(6,False),(12,False),(3,True)]:
            result=estimate_trend(s,hac_lags=lag,month_controls=controls)
            rows.append({'analysis':'trend specification','metric':metric,'scenario':f'HAC {lag}; month controls {controls}',
                         'estimate':result['ols_slope_per_month'],'ci_low':result['hac_ci_low'],'ci_high':result['hac_ci_high'],
                         'reference_estimate':reference['ols_slope_per_month'],'unit':'metric units/month'})
        rows.append({'analysis':'robust trend','metric':metric,'scenario':'Theil-Sen',
                     'estimate':reference['theil_sen_slope_per_month'],'reference_estimate':reference['ols_slope_per_month'],'unit':'metric units/month'})
        for stat in ['mean','median']:
            rows.append({'analysis':'mean versus median','metric':metric,'scenario':stat,'estimate':getattr(s,stat)(),
                         'reference_estimate':s.mean(),'unit':'metric units'})
        reduced=marked[marked.excluded.isna()].groupby('month')[METRICS[:2]].sum(min_count=1)
        reduced[METRICS[2]]=reduced[METRICS[1]]/reduced[METRICS[0]].where(reduced[METRICS[0]]!=0)
        result=estimate_trend(reduced[metric].reindex(calendar))
        rows.append({'analysis':'extreme exclusion diagnostic only','metric':metric,'scenario':'five largest IQR-scaled flagged rows omitted',
                     'estimate':result['ols_slope_per_month'],'reference_estimate':reference['ols_slope_per_month'],'unit':'metric units/month',
                     'excluded_rows':len(selected)})
        annual=nat.assign(year=nat.month.dt.year).groupby('year')[METRICS[:2]].sum()
        annual[METRICS[2]]=annual[METRICS[1]]/annual[METRICS[0]]
        rows.append({'analysis':'annual aggregation','metric':metric,'scenario':'2025 vs 2024',
                     'estimate':100*(annual.loc[2025,metric]/annual.loc[2024,metric]-1),
                     'reference_estimate':100*(s[s.index.year==2025].mean()/s[s.index.year==2024].mean()-1),
                     'unit':'percent; annual ratio weighted, monthly reference unweighted'})
    # B,D,E: do not let available-case composition masquerade as fixed-cohort growth.
    for threshold in [75,90,100]:
        cohort=coverage[coverage.full_window_coverage_pct>=threshold][['region_code','presentation_key']]
        fixed=detail.merge(cohort,on=['region_code','presentation_key'],validate='many_to_one')
        annual=fixed.assign(year=fixed.month.dt.year).groupby('year').prescription_items.sum(min_count=1)
        rows.append({'analysis':'coverage cohort','metric':'prescription_items','scenario':f'coverage >= {threshold}%',
                     'estimate':100*(annual.loc[2025]/annual.loc[2024]-1),'selected_series':len(cohort),
                     'unit':'percent observed-sum annual growth; absent cells unknown'})
    joined=coverage.merge(detail.groupby(['region_code','presentation_key']).prescription_items.sum().rename('total_items').reset_index(),how='left')
    for threshold in [75,90,100]:
        for gaps in [0,36]:
            eligible=(joined.full_window_coverage_pct.ge(threshold)&joined.observed_month_count.ge(24)&joined.total_items.ge(36000)&joined.internal_missing_month_count.le(gaps))
            rows.append({'analysis':'coverage eligibility','metric':'prescription_items','scenario':f'coverage {threshold}; internal gaps <= {gaps}',
                         'estimate':int(eligible.sum()),'unit':'candidate series count'})
    pre=populations['presentation'][0]; biggest=pre.groupby('presentation_key').prescription_items.sum().idxmax()
    for scenario,subset in [('all presentations',pre),('without largest presentation',pre[pre.presentation_key!=biggest])]:
        annual=subset.assign(year=subset.month.dt.year).groupby('year')[METRICS[:2]].sum()
        for metric in METRICS[:2]:
            rows.append({'analysis':'dominant presentation sensitivity','metric':metric,'scenario':scenario,
                         'estimate':100*(annual.loc[2025,metric]/annual.loc[2024,metric]-1),'unit':'percent annual growth'})
    for region,f in populations['regional'][0].groupby('region_name'):
        for metric in METRICS[:2]:
            s=calendar_series(f,metric,calendar); result=estimate_trend(s)
            rows.append({'analysis':'regional consistency','metric':metric,'scenario':region,
                         'estimate':result['ols_slope_per_month'],'unit':'metric units/month'})
    for status,cohort in [('complete',coverage[coverage.observed_month_count==len(calendar)]),('incomplete',coverage[(coverage.observed_month_count>0)&(coverage.observed_month_count<len(calendar))])]:
        subset=detail.merge(cohort[['region_code','presentation_key']],on=['region_code','presentation_key'])
        stats=[]
        for _,f in subset.groupby(['region_code','presentation_key']):
            stats.append(describe_series(calendar_series(f,'prescription_items',calendar))['coefficient_of_variation'])
        rows.append({'analysis':'history cohorts','metric':'prescription_items','scenario':status,
                     'estimate':np.nanmedian(stats) if stats else np.nan,'selected_series':len(cohort),'unit':'median observed-month CV'})
    results=pd.DataFrame(rows)
    summary=[]
    for (analysis,metric),f in results.groupby(['analysis','metric'],sort=True):
        summary.append({'analysis':analysis,'metric':metric,'scenarios':len(f),'minimum_estimate':f.estimate.min(),
                        'maximum_estimate':f.estimate.max(),'all_positive':bool(f.estimate.gt(0).all()),
                        'all_negative':bool(f.estimate.lt(0).all()),'unit':f.unit.iloc[0],
                        'interpretation':'Sensitivity range, not sampling confidence interval'})
    return pd.DataFrame(summary),results,selected

def forecast_diagnostics(populations, calendar, eligible_pairs):
    rows=[]
    for level,(frame,keys) in populations.items():
        if level=='region_presentation':
            frame=frame.merge(eligible_pairs[['region_code','presentation_key']],on=['region_code','presentation_key'],validate='many_to_one')
        if level=='presentation':
            totals=frame.groupby('presentation_key').prescription_items.sum()
            frame=frame[frame.presentation_key.isin(totals[totals>=36000].index)]
        groups=frame.groupby(keys,sort=True) if keys else [('England',frame)]
        for key,f in groups:
            key=key if isinstance(key,tuple) else (key,); identity=dict(zip(keys,key)) if keys else {}
            for metric in METRICS[:2]:
                s=calendar_series(f,metric,calendar); stats=describe_series(s); trend=estimate_trend(s)
                seasonal,_,acf_table,_=seasonality(s)
                prior=s.shift(1); changes=100*(s-prior)/prior.where(prior!=0)
                mean0=s[s.index.year==2024].mean(); mean1=s[s.index.year==2025].mean()
                shift=100*(mean1/mean0-1) if mean0!=0 else np.nan
                rows.append({'level':level,**identity,'metric':metric,**stats,
                             'zero_observed_months':int(s.eq(0).sum()),'observed_zero_fraction':s.eq(0).sum()/s.notna().sum(),
                             'trend_slope':trend.get('ols_slope_per_month',np.nan),'detrended_cv':trend.get('residual_cv',np.nan),
                             'acf_lag1':acf_table.acf.iloc[1] if len(acf_table)>1 else np.nan,
                             'detrended_acf_lag12':seasonal.get('detrended_acf_lag12',np.nan),
                             'stl_seasonal_strength_exploratory':seasonal.get('stl_seasonal_strength',np.nan),
                             'absolute_mom_50pct_count':int(changes.abs().ge(50).sum()),'annual_mean_shift_pct':shift,
                             'shift_review_required':bool(abs(shift)>=20) if np.isfinite(shift) else True,
                             'initial_horizons_months':'1, 2, 3',
                             'shortlist':'Naive; seasonal naive (benchmark); drift; damped ETS; regularized lag regression',
                             'interpretation':'Diagnostic eligibility, not proven accuracy. Only three annual cycles; refit selection within training folds.'})
    return pd.DataFrame(rows)
