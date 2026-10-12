"""Exact symmetric Shapley identity for C = V sum(s_j p_j), not causal prices."""
import itertools
import numpy as np
import pandas as pd
from .statistical_analysis import safe_ratio

def shapley_cost(volume0, shares0, costs0, volume1, shares1, costs1):
    v=[float(volume0),float(volume1)]
    s=[np.asarray(shares0,dtype=float),np.asarray(shares1,dtype=float)]
    p=[np.asarray(costs0,dtype=float),np.asarray(costs1,dtype=float)]
    if not all(np.isfinite(a).all() for a in s+p) or not all(np.isfinite(v)):
        raise ValueError('Positive comparable item denominators required')
    if not all(np.isclose(a.sum(),1,atol=1e-12) for a in s):
        raise ValueError('Presentation shares must sum to one')
    def value(state):
        return v[state[0]]*np.dot(s[state[1]],p[state[2]])
    contributions=np.zeros(3)
    for order in itertools.permutations(range(3)):
        state=[0,0,0]
        for factor in order:
            old=value(state); state[factor]=1
            contributions[factor]+=(value(state)-old)/6
    observed=value([1,1,1])-value([0,0,0])
    return {'item_volume_effect_gbp':contributions[0],'presentation_mix_effect_gbp':contributions[1],
            'within_presentation_cost_per_item_effect_gbp':contributions[2],
            'observed_cost_change_gbp':observed,'reconciliation_residual_gbp':observed-contributions.sum()}

def annual_contributions(monthly, keys, year0=2024, year1=2025):
    f=monthly.copy(); f['year']=pd.to_datetime(f.month).dt.year
    annual=f.groupby(keys+['year'],sort=True)[['prescription_items','net_ingredient_cost_gbp']].sum(min_count=1).reset_index()
    count=f.groupby(keys+['year']).month.nunique().rename('observed_months').reset_index()
    annual=annual.merge(count,on=keys+['year'],validate='one_to_one')
    a=annual[annual.year==year0].drop(columns='year')
    b=annual[annual.year==year1].drop(columns='year')
    out=a.merge(b,on=keys,suffixes=('_baseline','_current'),how='outer',validate='one_to_one')
    for period in ['baseline','current']:
        out['cost_per_item_'+period]=safe_ratio(out['net_ingredient_cost_gbp_'+period],out['prescription_items_'+period])
    out['items_change']=out.prescription_items_current-out.prescription_items_baseline
    out['nic_change_gbp']=out.net_ingredient_cost_gbp_current-out.net_ingredient_cost_gbp_baseline
    out['nic_change_contribution_pct']=100*safe_ratio(out.nic_change_gbp,out.nic_change_gbp.sum())
    out['items_change_contribution_pct']=100*safe_ratio(out.items_change,out.items_change.sum())
    out['cost_per_item_change_pct']=100*safe_ratio(out.cost_per_item_current-out.cost_per_item_baseline,out.cost_per_item_baseline)
    out['item_share_baseline']=safe_ratio(out.prescription_items_baseline,out.prescription_items_baseline.sum())
    out['item_share_current']=safe_ratio(out.prescription_items_current,out.prescription_items_current.sum())
    out['item_share_change_pp']=100*(out.item_share_current-out.item_share_baseline)
    out['comparison']=f'{year1} vs {year0}'
    return out

def cost_outputs(populations, phase2_decomposition):
    presentation=annual_contributions(populations['presentation'][0],['presentation_key','presentation_name','unit_of_measure'])
    regional=annual_contributions(populations['regional'][0],['region_code','region_name'])
    monthly=[]
    for level in ['national','regional','presentation']:
        f,keys=populations[level]
        columns=['month']+keys+['prescription_items','net_ingredient_cost_gbp','ingredient_cost_per_item_gbp']
        monthly.append(f[columns].assign(level=level))
    rows=[]
    for year0,year1 in [(2023,2024),(2024,2025),(2023,2025)]:
        c=annual_contributions(populations['presentation'][0],['presentation_key'],year0,year1)
        complete=(c.observed_months_baseline.eq(12)&c.observed_months_current.eq(12)&c.prescription_items_baseline.gt(0)&c.prescription_items_current.gt(0)).all()
        if not complete:
            rows.append({'comparison':f'{year1} vs {year0}','status':'skipped: missing/new/zero-denominator categories; prices unidentified'})
            continue
        result=shapley_cost(c.prescription_items_baseline.sum(),c.item_share_baseline,c.cost_per_item_baseline,
                            c.prescription_items_current.sum(),c.item_share_current,c.cost_per_item_current)
        actual=float(c.nic_change_gbp.sum())
        if not np.isclose(sum(result[k] for k in ['item_volume_effect_gbp','presentation_mix_effect_gbp','within_presentation_cost_per_item_effect_gbp']),actual,atol=.01,rtol=0):
            raise AssertionError('Three-factor decomposition failed')
        result['observed_cost_change_gbp']=actual
        result['reconciliation_residual_gbp']=actual-sum(result[k] for k in ['item_volume_effect_gbp','presentation_mix_effect_gbp','within_presentation_cost_per_item_effect_gbp'])
        p0=c.net_ingredient_cost_gbp_baseline.sum()/c.prescription_items_baseline.sum()
        p1=c.net_ingredient_cost_gbp_current.sum()/c.prescription_items_current.sum()
        v0=c.prescription_items_baseline.sum(); v1=c.prescription_items_current.sum()
        result['phase2_two_factor_volume_gbp']=(v1-v0)*(p1+p0)/2
        result['phase2_two_factor_cost_and_mix_gbp']=(p1-p0)*(v1+v0)/2
        if year1==year0+1:
            check=phase2_decomposition[(phase2_decomposition.comparison_type=='annual') & (pd.to_datetime(phase2_decomposition.period).dt.year==year1)]
            if len(check)!=1 or not np.isclose(check.iloc[0].item_volume_effect_gbp,result['phase2_two_factor_volume_gbp'],atol=.01,rtol=0):
                raise AssertionError('Independent Phase 2 cost decomposition mismatch')
        rows.append({'comparison':f'{year1} vs {year0}','status':'reconciled','categories':len(c),
                     'method':'Symmetric Shapley average over all six factor orders',**result})
    return pd.concat(monthly,ignore_index=True),presentation,regional,pd.DataFrame(rows)
