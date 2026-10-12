"""Within-series diagnostics retain every observation and original IQR flag."""
import numpy as np
import pandas as pd
from .statistical_analysis import calendar_series, growth

def robust_z(series):
    s=series.astype(float)
    if s.notna().sum()==0: return pd.Series(np.nan,index=s.index),np.nan
    median=s.median(); mad=(s-median).abs().median()
    if len(s.dropna())<12 or not np.isfinite(mad) or mad==0:
        return pd.Series(np.nan,index=s.index),mad
    return .6744897501960817*(s-median)/mad,mad

def diagnostics(detail, original_flags, calendar):
    lookup={(pd.Timestamp(r.month),r.region_code,r.presentation_key,r.metric):r for r in original_flags.itertuples()}
    rows=[]
    mapping={'items':'prescription_items','nic_gbp':'net_ingredient_cost_gbp','total_quantity':'total_quantity',
             'cost_per_item':'ingredient_cost_per_item_gbp'}
    for (region,key),f in detail.groupby(['region_code','presentation_key'],sort=True):
        for metric,column in mapping.items():
            s=calendar_series(f,column,calendar); z,mad=robust_z(s); mom=growth(s)
            # Prior six calendar months; at least four observed. Baseline excludes current point.
            baseline=s.shift(1).rolling(6,min_periods=4).median()
            relative=100*(s-baseline)/baseline.where(baseline!=0)
            for i,(month,value) in enumerate(s.items()):
                if pd.isna(value): continue
                legacy=lookup.get((month,region,key,metric))
                methods=[]
                if legacy is not None: methods.append('Phase 2 three-IQR')
                if np.isfinite(z.iloc[i]) and abs(z.iloc[i])>3.5: methods.append('MAD robust z > 3.5')
                if np.isfinite(mom.iloc[i]) and abs(mom.iloc[i])>=50: methods.append('absolute calendar MoM >= 50%')
                if np.isfinite(relative.iloc[i]) and abs(relative.iloc[i])>=50: methods.append('prior rolling-median deviation >= 50%')
                if not methods: continue
                prev=s.iloc[i-1] if i else np.nan; nxt=s.iloc[i+1] if i+1<len(s) else np.nan
                following=s.iloc[i+1:i+4]
                sustained=(len(following)==3 and following.notna().all() and np.isfinite(baseline.iloc[i]) and baseline.iloc[i]>0
                           and ((following/baseline.iloc[i]-1)*np.sign(value-baseline.iloc[i])>=.3).all())
                if value<0 or not np.isfinite(value):
                    classification='Potential data issue'
                elif len(s.dropna())<12 or pd.isna(prev) or pd.isna(nxt) or mad==0:
                    classification='Insufficient evidence'
                elif sustained:
                    classification='Potential structural shift'
                else:
                    classification='Unusual but plausible activity'
                rows.append({'month':month,'region_code':region,'region_name':f.region_name.iloc[0],
                             'presentation_key':key,'presentation_name':f.presentation_name.iloc[0],
                             'unit_of_measure':f.unit_of_measure.iloc[0],'metric':metric,'observed_value':value,
                             'detection_method':'; '.join(methods),'robust_z':z.iloc[i],'mad':mad,
                             'mom_change_pct':mom.iloc[i],'prior_rolling_median':baseline.iloc[i],
                             'rolling_median_change_pct':relative.iloc[i],'previous_calendar_value':prev,'next_calendar_value':nxt,
                             'phase2_flag':legacy is not None,'classification':classification,
                             'threshold':'|z|>3.5; |MoM|>=50%; |rolling deviation|>=50%; original IQR fences retained',
                             'phase2_lower_fence':legacy.lower_fence if legacy is not None else np.nan,
                             'phase2_upper_fence':legacy.upper_fence if legacy is not None else np.nan,
                             'evidence_limit':'Heuristic review category; sustained=three subsequent observations >=30% same-direction from prior median. No verified error or causal attribution.'})
    out=pd.DataFrame(rows).sort_values(['month','region_code','presentation_key','metric']).reset_index(drop=True)
    retained=out[out.phase2_flag].copy()
    if len(retained)!=len(original_flags): raise AssertionError('Original flags not retained one-to-one')
    return out,retained
