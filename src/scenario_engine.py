"""Deterministic NIC accounting scenarios; assumptions are never probabilities."""
import json
import numpy as np
import pandas as pd

LIMIT='Hypothetical accounting sensitivity; fixed NIC/item assumptions, not observed savings, profitability, clinical substitution or attainable outcomes'

def accounting(items,unit_cost,volume_pct=0,cost_pct=0):
    if not all(np.isfinite(x) for x in [items,unit_cost,volume_pct,cost_pct]) or items<0 or unit_cost<0 or volume_pct<=-100 or cost_pct<=-100:
        raise ValueError('Invalid nonnegative scenario inputs')
    hypothetical_items=items*(1+volume_pct/100)
    hypothetical_cost=unit_cost*(1+cost_pct/100)
    return hypothetical_items,hypothetical_cost,hypothetical_items*hypothetical_cost

def break_even(volume_pct):
    if not np.isfinite(volume_pct) or volume_pct<=-100: raise ValueError('Invalid volume')
    return 100*(1/(1+volume_pct/100)-1)

def mix_simulation(presentations,total_items,donor,receiver,transfer_pp):
    if donor==receiver or not np.isfinite(transfer_pp) or transfer_pp<0 or not np.isfinite(total_items) or total_items<=0: raise ValueError('Invalid mix transfer')
    p=presentations[['presentation_key','presentation_name','recent_items','recent_nic_per_item_gbp']].copy()
    if p.presentation_key.duplicated().any() or p.recent_items.isna().any() or p.recent_items.lt(0).any() or p.recent_items.sum()<=0 or p.recent_nic_per_item_gbp.isna().any() or p.recent_nic_per_item_gbp.lt(0).any(): raise ValueError('Incomplete mix baseline')
    if donor not in set(p.presentation_key) or receiver not in set(p.presentation_key): raise ValueError('Unknown presentation')
    p['baseline_share']=p.recent_items/p.recent_items.sum()
    p['scenario_share']=p.baseline_share
    p.loc[p.presentation_key.eq(donor),'scenario_share']-=transfer_pp/100
    p.loc[p.presentation_key.eq(receiver),'scenario_share']+=transfer_pp/100
    if p.scenario_share.lt(-1e-12).any() or not np.isclose(p.scenario_share.sum(),1): raise ValueError('Infeasible mix')
    p['hypothetical_items']=p.scenario_share*total_items
    p['hypothetical_nic_gbp']=p.hypothetical_items*p.recent_nic_per_item_gbp
    p['baseline_items_at_total']=p.baseline_share*total_items
    p['baseline_nic_at_total_gbp']=p.baseline_items_at_total*p.recent_nic_per_item_gbp
    p['transfer_pp']=transfer_pp; p['donor']=donor; p['receiver']=receiver
    return p

def scenarios(features,inputs,cfg):
    national=features['national'].iloc[0]; recent=cfg['recent_year']; changes=cfg['scenario_changes_pct']
    rows=[]; mix_rows=[]; assumptions=[]
    def add(identifier,family,scope,items,unit,volume,cost,baseline_type,period,extra=None,baseline_date=None):
        count,ratio,nic=accounting(items,unit,volume,cost)
        assumption={'volume_change_pct':volume,'nic_per_item_change_pct':cost,**(extra or {})}
        rows.append({'scenario_id':identifier,'scenario_name':family,'scope':scope,'baseline_period':period,'baseline_type':baseline_type,
                     'baseline_end_date':pd.Timestamp(baseline_date or f'{recent}-12-01'),'forecast_as_of':pd.Timestamp(cfg['forecast_as_of']) if baseline_type=='Model forecast baseline' else pd.NaT,
                     'reference_items':items,'reference_nic_per_item_gbp':unit,'reference_nic_gbp':items*unit,
                     'assumptions':json.dumps(assumption,sort_keys=True,separators=(',',':')),
                     'volume_change_pct':volume,'nic_per_item_change_pct':cost,'hypothetical_items':count,
                     'assumed_nic_per_item_gbp':ratio,'hypothetical_nic_gbp':nic,'items_difference':count-items,'nic_difference_gbp':nic-items*unit,
                     'evidence_class':'Hypothetical scenario','limitations':LIMIT})
        assumptions.append({'scenario_id':identifier,'scenario_name':family,'assumptions':rows[-1]['assumptions'],
                            'baseline_period':period,'baseline_type':baseline_type,'evidence_class':'Hypothetical scenario','probability':np.nan})
    for v in changes: add(f'A_{v}','A: item volume','England',national.recent_items,national.recent_nic_per_item_gbp,v,0,'Observed baseline',str(recent))
    for c in changes: add(f'B_{c}','B: NIC per item','England',national.recent_items,national.recent_nic_per_item_gbp,0,c,'Observed baseline',str(recent))
    for v in changes:
        for c in changes: add(f'C_{v}_{c}','C: combined volume and NIC/item','England',national.recent_items,national.recent_nic_per_item_gbp,v,c,'Observed baseline',str(recent))
    # Explicit deterministic donors: two largest observed presentations by item count.
    products=features['presentation'].sort_values(['recent_items','presentation_key'],ascending=[False,True])
    donor,receiver=products.presentation_key.iloc[:2]
    for transfer in cfg['mix_transfer_pp']:
        m=mix_simulation(products,national.recent_items,donor,receiver,transfer)
        sid=f'D_{transfer}'; m['scenario_id']=sid; m['evidence_class']='Hypothetical scenario'; m['limitations']=LIMIT
        mix_rows.append(m)
        add(sid,'D: presentation mix','England',national.recent_items,national.recent_nic_per_item_gbp,0,0,'Observed baseline',str(recent),{'donor':donor,'receiver':receiver,'transfer_pp':transfer})
        rows[-1]['hypothetical_nic_gbp']=float(m.hypothetical_nic_gbp.sum())
        rows[-1]['assumed_nic_per_item_gbp']=rows[-1]['hypothetical_nic_gbp']/national.recent_items
        rows[-1]['nic_difference_gbp']=rows[-1]['hypothetical_nic_gbp']-rows[-1]['reference_nic_gbp']
    for region in features['regional'].itertuples():
        for v in changes:
            add(f'E_{region.region_code}_{v}','E: regional volume',region.region_code,region.recent_items,region.recent_nic_per_item_gbp,v,0,'Observed baseline',str(recent))
            rows[-1]['national_nic_difference_gbp']=rows[-1]['nic_difference_gbp']
            rows[-1]['national_hypothetical_nic_gbp']=national.recent_nic_gbp+rows[-1]['nic_difference_gbp']
    op=inputs['p4/operational_forecasts']
    op=op[op.aggregation_level.eq('national')]
    if op.training_end_date.ne(pd.Timestamp(cfg['forecast_as_of'])).any(): raise ValueError('Forecast as-of mismatch')
    reference=inputs['p2/national_monthly_trends']; reference=reference[reference.month.le(pd.Timestamp(cfg['forecast_as_of'])) & reference.month.ge(pd.Timestamp(cfg['historical_start']))]
    # Fixed latest complete calendar-year historical ratio, never later outcomes.
    cost_reference=reference[reference.month.dt.year.eq(recent)]
    if len(cost_reference)!=12 or cost_reference.month.max()>pd.Timestamp(cfg['forecast_as_of']): raise ValueError('Incomplete or future cost reference')
    unit=cost_reference.net_ingredient_cost_gbp.sum()/cost_reference.prescription_items.sum()
    for forecast in op.itertuples():
        for v in changes:
            add(f'F_{forecast.forecast_month:%Y%m}_{v}','F: forecast planning sensitivity','England',forecast.point_forecast,unit,v,0,'Model forecast baseline',f'{forecast.forecast_month:%Y-%m}',
                {'historical_cost_reference_year':recent,'fixed_cost_assumption':'2025 weighted NIC/item, no extrapolated cost trend'},cfg['forecast_as_of'])
    result=pd.DataFrame(rows)
    comparison=result[['scenario_id','scenario_name','scope','baseline_type','baseline_period','reference_nic_gbp','hypothetical_nic_gbp','nic_difference_gbp','evidence_class']].copy()
    comparison['nic_difference_pct']=100*comparison.nic_difference_gbp/comparison.reference_nic_gbp.replace(0,np.nan)
    sensitivity=result[['scenario_id','scenario_name','scope','volume_change_pct','nic_per_item_change_pct','hypothetical_items','hypothetical_nic_gbp','nic_difference_gbp','evidence_class']].copy()
    algebra=pd.DataFrame([{'volume_change_pct':v,'offsetting_nic_per_item_change_pct':break_even(v),'reference_items':national.recent_items,
                          'reference_nic_per_item_gbp':national.recent_nic_per_item_gbp,'reference_nic_gbp':national.recent_nic_gbp,
                          'hypothetical_nic_gbp':accounting(national.recent_items,national.recent_nic_per_item_gbp,v,break_even(v))[2],
                          'baseline_period':str(recent),'evidence_class':'Hypothetical scenario','limitations':'Accounting NIC equality, not financial profitability'} for v in changes])
    return {'scenario_assumptions':pd.DataFrame(assumptions),'scenario_results':result,'scenario_comparisons':comparison,
            'presentation_mix_scenarios':pd.concat(mix_rows,ignore_index=True),'scenario_sensitivity':sensitivity,'accounting_break_even_analysis':algebra}
