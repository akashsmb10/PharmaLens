"""Pure scope-aware dashboard arithmetic and frozen-model comparisons."""
import numpy as np
import pandas as pd
from src.forecast_metrics import metrics as forecast_metrics

def ratio(cost,items): return cost/items if pd.notna(items) and items>0 else np.nan

def totals(f):
    items=f.prescription_items.sum(min_count=1); nic=f.net_ingredient_cost_gbp.sum(min_count=1)
    return {'items':items,'nic_gbp':nic,'nic_per_item_gbp':ratio(nic,items),'regions':f.region_code.nunique(),'presentations':f.presentation_key.nunique()}

def monthly(f,keys=None):
    keys=(keys or [])+['month']
    out=f.groupby(keys,dropna=False,sort=True)[['prescription_items','net_ingredient_cost_gbp']].sum(min_count=1).reset_index()
    out['nic_per_item_gbp']=[ratio(c,i) for c,i in zip(out.net_ingredient_cost_gbp,out.prescription_items)]
    return out

def summarize(f,keys):
    out=f.groupby(keys,dropna=False,sort=True).agg(prescription_items=('prescription_items',lambda s:s.sum(min_count=1)),
        net_ingredient_cost_gbp=('net_ingredient_cost_gbp',lambda s:s.sum(min_count=1)),observed_months=('month','nunique')).reset_index()
    out['nic_per_item_gbp']=[ratio(c,i) for c,i in zip(out.net_ingredient_cost_gbp,out.prescription_items)]
    return out

def annual_growth(f,year,keys=None):
    keys=keys or []; rows=[]
    groups=f.groupby(keys,dropna=False,sort=True) if keys else [('all',f)]
    for identity,g in groups:
        identity=identity if isinstance(identity,tuple) else (identity,)
        current=g[g.month.dt.year.eq(year)]; old=g[g.month.dt.year.eq(year-1)]
        valid=current.month.nunique()==old.month.nunique()==12
        a=totals(current); b=totals(old)
        growth=lambda x,y:100*(x/y-1) if valid and pd.notna(y) and y>0 else np.nan
        rows.append({**dict(zip(keys,identity)),'year':year,'baseline_year':year-1,
                     'item_growth_pct':growth(a['items'],b['items']),'nic_growth_pct':growth(a['nic_gbp'],b['nic_gbp']),
                     'current_items':a['items'],'current_nic_gbp':a['nic_gbp'],'baseline_items':b['items'],'baseline_nic_gbp':b['nic_gbp'],
                     'status':'Complete aggregate-year comparison' if valid else 'Unavailable: incomplete comparison years'})
    return pd.DataFrame(rows)

def latest_growth(f):
    if f.empty: return {'year':None,'item_growth_pct':np.nan,'nic_growth_pct':np.nan}
    return annual_growth(f,int(f.month.dt.year.max())).iloc[0].to_dict()

def shares(summary,denominator):
    out=summary.copy(); a=totals(denominator)
    out['item_share_pct']=100*out.prescription_items/a['items'] if a['items']>0 else np.nan
    out['nic_share_pct']=100*out.net_ingredient_cost_gbp/a['nic_gbp'] if a['nic_gbp']>0 else np.nan
    return out

def indexed(frame,value,group):
    out=frame.copy().sort_values([group,'month'])
    base=out.groupby(group)[value].transform('first').replace(0,np.nan)
    out['index_100']=100*out[value]/base
    return out

def comparisons(backtest,variants):
    f=backtest[backtest.variant.isin(variants)].copy(); keys=['origin_date','horizon']
    good=f[f.model_status.eq('ok') & f.prediction.notna() & f.actual.notna()]
    complete=good.groupby(keys).variant.nunique(); support=complete[complete.eq(len(variants))].reset_index()[keys]
    good=good.merge(support,on=keys,validate='many_to_one')
    rows=[{'variant':variant,**forecast_metrics(g)} for variant,g in good.groupby('variant',sort=True)]
    return pd.DataFrame(rows,columns=['variant','n','MAE','RMSE','WAPE','sMAPE','MASE','Bias','mase_defined_rows']),good

def history_for_series(fact,choice):
    out=fact.copy()
    if choice.aggregation_level!='national': out=out[out.region_code.eq(choice.series_id.split('::')[0])]
    if choice.aggregation_level=='region_presentation': out=out[out.presentation_key.eq(choice.series_id.split('::',1)[1])]
    return monthly(out)
