"""Describe frozen-model error, without training or selecting an estimator."""
import numpy as np
import pandas as pd
from .forecast_metrics import metrics
from .decision_features import join_unique

def classify_error(mase,n,percentile,cfg):
    if pd.isna(mase) or n<cfg['minimum_holdout_forecasts']: return 'Insufficient evaluation evidence'
    return 'Lower observed error' if percentile<=1/3 else 'Moderate observed error' if percentile<=2/3 else 'Higher observed error'

def risk_tables(inputs,cfg):
    decisions=inputs['p4/model_selection_decisions']; attempts=inputs['p4/backtest_predictions']
    matched=attempts.merge(decisions[['series_id','selected_variant']],on='series_id',validate='many_to_one')
    selected=matched[matched.variant.eq(matched.selected_variant)]
    profiles=[]; horizons=[]
    for sid,f in selected.groupby('series_id',sort=True):
        decision=decisions[decisions.series_id.eq(sid)].iloc[0]
        row={'series_id':sid,'aggregation_level':decision.aggregation_level,'selected_model':decision.selected_model,'selected_variant':decision.selected_variant}
        for col in ['region_code','region_name','presentation_key','presentation_name']: row[col]=f[col].iloc[0]
        for split,g in f.groupby('split_type'):
            valid=g[g.model_status.eq('ok') & g.prediction.notna() & g.actual.notna()]
            values=metrics(valid)
            row.update({f'{split}_{k}':v for k,v in values.items()})
            for h,part in g.groupby('horizon'):
                good=part[part.model_status.eq('ok') & part.prediction.notna() & part.actual.notna()]
                horizons.append({'series_id':sid,'aggregation_level':decision.aggregation_level,'split_type':split,'horizon':h,
                                 'expected_forecasts':len(part),'missing_forecasts':len(part)-len(good),**metrics(good),
                                 'evidence_class':'Validated historical model result'})
        h=f[f.split_type.eq('holdout')]; good=h[h.model_status.eq('ok') & h.prediction.notna()]
        row['expected_holdout_forecasts']=len(h); row['missing_forecasts']=len(h)-len(good)
        row['selected_failure_count']=int(h.model_status.ne('ok').sum())
        row['selected_failure_rate_pct']=100*row['selected_failure_count']/len(h)
        row['all_family_failure_count']=int(attempts[attempts.series_id.eq(sid)].model_status.ne('ok').sum())
        row['bias_pct']=100*row['holdout_Bias']/good.actual.mean() if len(good) and good.actual.mean()>0 else np.nan
        row['interval_status']=inputs['p4/interval_calibration'].query('series_id == @sid').interval_status.iloc[0]
        e=inputs['p4/series_eligibility'].query('series_id == @sid').iloc[0]
        row['history_months']=len(inputs['p2/national_monthly_trends'])-int(e.full_history_missing_months_descriptive_only)
        row['evidence_class']='Validated historical model result'
        profiles.append(row)
    p=pd.DataFrame(profiles)
    from .prioritization import normalize
    p['within_level_error_percentile']=p.groupby('aggregation_level').holdout_MASE.transform(lambda s:normalize(s)/100)
    p['reliability_class']=[classify_error(r.holdout_MASE,r.holdout_n,r.within_level_error_percentile,cfg) for r in p.itertuples()]
    p['manual_review']=p.reliability_class.isin(['Higher observed error','Insufficient evaluation evidence']) | p.holdout_MASE.ge(1) | p.bias_pct.abs().ge(cfg['bias_review_pct']) | p.missing_forecasts.gt(0)
    p['monitoring_action']=np.where(p.manual_review,'Review errors/bias before planning use','Routine point-forecast tracking; validate manually before consequential planning')
    p['limitation']='Relative observed errors only; overlapping targets and absent calibrated intervals; no future accuracy guarantee'
    # Benchmark comparison must use exactly paired origin/horizon cells.
    paired=[]
    for sid,g in selected[selected.split_type.eq('holdout')].groupby('series_id'):
        n=attempts[(attempts.series_id==sid)&(attempts.split_type=='holdout')&(attempts.model=='naive')]
        pair=g.merge(n[['origin_date','horizon','prediction','model_status']],on=['origin_date','horizon'],suffixes=('','_naive'),validate='one_to_one')
        pair=pair[pair.model_status.eq('ok') & pair.model_status_naive.eq('ok') & pair.prediction.notna() & pair.prediction_naive.notna()]
        selected_metric=metrics(pair)['MASE']; naive_metric=metrics(pair.assign(prediction=pair.prediction_naive))['MASE']
        paired.append({'series_id':sid,'paired_n':len(pair),'paired_selected_MASE':selected_metric,'paired_naive_MASE':naive_metric,
                       'paired_MASE_improvement_pct':100*(1-selected_metric/naive_metric) if naive_metric>0 else np.nan})
    p=join_unique(p,pd.DataFrame(paired),['series_id'])
    return p,p.copy(),pd.DataFrame(horizons)

def hierarchy_gaps(inputs,cfg):
    history=inputs['p4/aggregate_forecast_comparison'].copy().rename(columns={'direct_national':'direct_forecast','regional_sum':'regional_sum_forecast','target_date':'forecast_month'})
    history['context']=history.split_type
    op=inputs['p4/operational_aggregate_comparison'].copy().rename(columns={'direct_national_forecast':'direct_forecast'})
    op['origin_date']=op.training_end_date; op['context']='operational'
    keys=['context','origin_date','forecast_month','horizon','direct_forecast','regional_sum_forecast']
    f=pd.concat([history[keys],op[keys]],ignore_index=True)
    f['signed_gap_items']=f.regional_sum_forecast-f.direct_forecast
    f['absolute_gap_items']=f.signed_gap_items.abs()
    f['signed_gap_pct']=100*f.signed_gap_items/f.direct_forecast.replace(0,np.nan)
    f['absolute_gap_pct']=f.signed_gap_pct.abs()
    f['manual_review']=f.absolute_gap_pct.ge(cfg['coherence_review_pct'])
    f['review_threshold_pct']=cfg['coherence_review_pct']
    f['evidence_class']='Validated historical model result'
    f['limitation']='Coherence is not accuracy; direct and summed forecasts are unreconciled; 28 presentations are not a complete hierarchy'
    return f
