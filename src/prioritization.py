"""Policy-driven monitoring priorities, not estimates of commercial opportunity."""
import json
import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from .decision_features import validate_weights

COMPONENTS=['activity','change','cost','forecast','quality']

def normalize(values,method='percentile'):
    s=pd.Series(values,dtype=float).replace([np.inf,-np.inf],np.nan); out=pd.Series(np.nan,index=s.index)
    valid=s.dropna(); n=len(valid)
    if not n: return out
    if valid.nunique()==1: out.loc[valid.index]=50.; return out
    if method=='percentile': out.loc[valid.index]=100*(valid.rank(method='average')-1)/(n-1)
    elif method=='minmax': out.loc[valid.index]=100*(valid-valid.min())/(valid.max()-valid.min())
    else: raise ValueError('Unknown normalization')
    return out

def tier(score,cfg):
    if pd.isna(score): return 'Insufficient evidence'
    return 'High review priority' if score>=cfg['high_priority'] else 'Moderate review priority' if score>=cfg['moderate_priority'] else 'Routine monitoring'

def priority_scores(features,cfg,weights=None,method='percentile'):
    weights=cfg['weights'] if weights is None else weights; validate_weights(weights)
    if not set(weights)<=set(COMPONENTS): raise ValueError('Unknown component')
    f=features.copy()
    raw={'activity':f.recent_items,'change':f.item_growth_pct.abs(),
         'cost':f.nic_per_item_change_pct.abs(),'forecast':f.holdout_MASE,
         'quality':f.missing_cell_pct+f.extreme_flags_per_1000_observed_cells}
    for name in COMPONENTS: f[f'{name}_score']=normalize(raw[name],method)
    required=[k for k,v in weights.items() if v>0]
    f['missing_components']=f.apply(lambda r:';'.join(k for k in required if pd.isna(r[f'{k}_score'])),axis=1)
    f['rank_eligible']=f.missing_components.eq('')
    f['composite_score']=sum(f[f'{k}_score']*v for k,v in weights.items() if v>0)
    f.loc[~f.rank_eligible,'composite_score']=np.nan
    f['rank']=f.composite_score.rank(method='min',ascending=False).astype('Int64')
    f['monitoring_tier']=[tier(s,cfg) for s in f.composite_score]
    f['weight_configuration']=json.dumps(weights,sort_keys=True,separators=(',',':'))
    f['normalization']=method
    f['evidence_class']=np.where(f.rank_eligible,'Exploratory signal','Insufficient evidence')
    f['interpretation']='Monitoring/investigation policy only; higher quality concern is not greater commercial opportunity'
    return f.sort_values(['rank','entity_id'],na_position='last').reset_index(drop=True)

def sensitivity(features,base,cfg):
    schemes={'default':cfg['weights'],'equal':dict.fromkeys(COMPONENTS,.2),
             'activity_heavy':dict(zip(COMPONENTS,[.5,.125,.125,.125,.125])),
             'forecast_heavy':dict(zip(COMPONENTS,[.125,.125,.125,.5,.125])),
             'quality_heavy':dict(zip(COMPONENTS,[.125,.125,.125,.125,.5]))}
    for excluded in COMPONENTS:
        schemes['leave_out_'+excluded]={k:(0 if k==excluded else cfg['weights'][k]/(1-cfg['weights'][excluded])) for k in COMPONENTS}
    details=[]; summaries=[]; thresholds=[]
    for level,features_one in features.items():
        if level=='national': continue
        reference=base[level][['entity_id','rank','monitoring_tier']].rename(columns={'rank':'baseline_rank','monitoring_tier':'baseline_tier'})
        scored_ids=set(reference[reference.baseline_rank.notna()].entity_id)
        for scheme,weights in schemes.items():
            for method in (['percentile','minmax'] if scheme=='default' else ['percentile']):
                result=priority_scores(features_one,cfg,weights,method).merge(reference,on='entity_id',validate='one_to_one')
                result['scheme']=scheme; result['normalization']=method
                result['rank_change']=result['rank'].astype(float)-result.baseline_rank.astype(float)
                result['tier_changed']=result.monitoring_tier.ne(result.baseline_tier)
                details.append(result[['aggregation_level','entity_id','scheme','normalization','composite_score','rank','baseline_rank','rank_change','monitoring_tier','baseline_tier','tier_changed','rank_eligible','weight_configuration','evidence_class']])
                pair=result.dropna(subset=['rank','baseline_rank']); n=len(pair)
                corr=float(spearmanr(pair['rank'].astype(float),pair.baseline_rank.astype(float)).statistic) if n>=3 and pair['rank'].nunique()>1 and pair.baseline_rank.nunique()>1 else np.nan
                k=min(3,len(scored_ids)); tops=set(reference[reference.baseline_rank.le(k)].entity_id); alt=set(result[result['rank'].le(k)&result.entity_id.isin(scored_ids)].entity_id)
                summaries.append({'aggregation_level':level,'scheme':scheme,'normalization':method,'paired_scored_entities':n,
                                  'spearman_rank_correlation':corr,'top_k':k,'top_priority_overlap_pct':100*len(tops&alt)/len(tops) if tops else np.nan,
                                  'tier_changes':int(result.tier_changed.sum()),'newly_scored_entities':int((result['rank'].notna()&result.baseline_rank.isna()).sum()),
                                  'evidence_class':'Exploratory signal'})
        for high,moderate in [(60,30),(70,40),(80,50)]:
            x=base[level].copy(); custom={**cfg,'high_priority':high,'moderate_priority':moderate}
            x['alternative_tier']=[tier(s,custom) for s in x.composite_score]
            x['tier_changed']=x.alternative_tier.ne(x.monitoring_tier)
            x['high_threshold']=high; x['moderate_threshold']=moderate
            thresholds.append(x[['aggregation_level','entity_id','composite_score','monitoring_tier','alternative_tier','high_threshold','moderate_threshold','tier_changed','evidence_class']])
    details=pd.concat(details,ignore_index=True)
    instability=details.groupby(['aggregation_level','entity_id']).rank_change.agg(lambda s:float(s.abs().max()) if s.notna().any() else np.nan).rename('max_absolute_rank_change').reset_index()
    counts={k:int(v.rank_eligible.sum()) for k,v in base.items()}
    instability['instability_threshold_ranks']=instability.aggregation_level.map(lambda k:max(1,counts[k]*cfg['rank_instability_fraction']))
    instability['unstable_rank']=instability.max_absolute_rank_change.ge(instability.instability_threshold_ranks)
    instability['evidence_class']='Exploratory signal'
    return details,pd.DataFrame(summaries),pd.concat(thresholds,ignore_index=True),instability
