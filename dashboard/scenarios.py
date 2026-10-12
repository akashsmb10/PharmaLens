"""Reuse validated accounting algebra; all state stays in the user's session."""
import numpy as np
import pandas as pd
from src.scenario_engine import accounting,break_even
from src.scenario_engine import mix_simulation as mix_simulation

def simulate(items,nic,volume_pct,cost_pct,context):
    if not np.isfinite(items) or items<=0 or not np.isfinite(nic) or nic<0: raise ValueError('A positive observed item baseline and nonnegative NIC are required.')
    unit=nic/items; count,price,result=accounting(items,unit,volume_pct,cost_pct)
    return pd.DataFrame([{'baseline':context,'baseline_items':items,'baseline_nic_gbp':nic,'baseline_nic_per_item_gbp':unit,
        'item_change_pct':volume_pct,'nic_per_item_change_pct':cost_pct,'hypothetical_items':count,'assumed_nic_per_item_gbp':price,
        'hypothetical_nic_gbp':result,'nic_difference_gbp':result-nic,'nic_difference_pct':100*(result/nic-1) if nic>0 else np.nan,
        'break_even_cost_change_pct':break_even(volume_pct),'evidence_class':'Hypothetical scenario'}])

def two_way(items,nic,changes=(-20,-10,0,10,20)):
    return pd.DataFrame([{ 'volume_pct':v,'cost_pct':c,'hypothetical_nic_gbp':accounting(items,nic/items,v,c)[2]} for v in changes for c in changes])
