"""Independent loops and algebra, not repeat calls to production calculations."""
import json
import math
import numpy as np
import pandas as pd

def validate(tables,inputs,cfg,contracts):
    rows=[]
    def check(name,expected,observed,tolerance=1e-6):
        if pd.isna(expected) and pd.isna(observed): diff=0.; passed=True
        elif isinstance(expected,(str,bool)) or isinstance(observed,str): diff=0. if expected==observed else 1.; passed=diff==0
        else: diff=float(observed)-float(expected); passed=bool(np.isfinite(diff) and abs(diff)<=tolerance)
        rows.append({'check_name':name,'expected':str(expected),'observed':str(observed),'difference':diff,'tolerance':tolerance,'status':'passed' if passed else 'failed'})
    fact=inputs['p2/cost_analytics']
    # Independent reconstruction from the fixed dimensions, rather than invoking coverage_grid.
    dimensions=inputs['p2/series_coverage'][['region_code','presentation_key']]
    months=inputs['p2/national_monthly_trends'][['month']]
    grid=dimensions.merge(months,how='cross').merge(fact[['month','region_code','presentation_key']].assign(is_observed=True),
         on=['month','region_code','presentation_key'],how='left',validate='one_to_one')
    grid['is_observed']=grid.is_observed.eq(True)
    for name in ['regional_decision_features','presentation_decision_features','region_presentation_decision_features','national_decision_summary']:
        for r in tables[name].to_dict('records'):
            f=fact; g=grid
            for key in ['region_code','presentation_key']:
                if key in r: f=f[f[key].eq(r[key])]; g=g[g[key].eq(r[key])]
            item_values=list(f.prescription_items); cost_values=list(f.net_ingredient_cost_gbp)
            items=sum(item_values) if item_values else np.nan; cost=math.fsum(cost_values) if cost_values else np.nan
            prefix=name+':'+r['entity_id']
            check(prefix+':items',items,r['historical_items'],0)
            check(prefix+':NIC',cost,r['historical_nic_gbp'],.01)
            check(prefix+':weighted ratio',cost/items if items>0 else np.nan,r['historical_nic_per_item_gbp'],1e-10)
            check(prefix+':item share',100*items/sum(fact.prescription_items),r['historical_item_share_pct'],1e-10)
            check(prefix+':missing cells',sum(not bool(x) for x in g.is_observed),r['missing_cells'],0)
            yearly={}
            for year in [cfg['baseline_year'],cfg['recent_year']]:
                part=f[f.month.dt.year.eq(year)]
                yearly[year]=(sum(part.prescription_items) if len(part) else np.nan,math.fsum(part.net_ingredient_cost_gbp) if len(part) else np.nan,part.month.nunique())
            a,b=yearly[cfg['baseline_year']],yearly[cfg['recent_year']]
            check(prefix+':recent items',b[0],r['recent_items'],0)
            check(prefix+':recent NIC',b[1],r['recent_nic_gbp'],.01)
            check(prefix+':item growth',100*(b[0]/a[0]-1) if a[0]>0 and a[2]==b[2]==12 else np.nan,r['item_growth_pct'])
            check(prefix+':cost ratio change',100*((b[1]/b[0])/(a[1]/a[0])-1) if a[0]>0 and b[0]>0 and a[1]>0 and a[2]==b[2]==12 else np.nan,r['nic_per_item_change_pct'])
    for name in ['regional_decision_features','presentation_decision_features']:
        check(name+':total items',sum(fact.prescription_items),sum(tables[name].historical_items),0)
        check(name+':total NIC',math.fsum(fact.net_ingredient_cost_gbp),math.fsum(tables[name].historical_nic_gbp),.01)
        check(name+':share sum',100,sum(tables[name].historical_item_share_pct),1e-9)
    decisions=inputs['p4/model_selection_decisions']; back=inputs['p4/backtest_predictions']
    for r in tables['forecast_reliability_profiles'].to_dict('records'):
        choice=decisions[decisions.series_id.eq(r['series_id'])].iloc[0]
        check(r['series_id']+':frozen variant',choice.selected_variant,r['selected_variant'],0)
        for split in ['development','holdout']:
            part=back[(back.series_id==r['series_id'])&(back.variant==choice.selected_variant)&(back.split_type==split)]
            good=[x for x in part.itertuples() if x.model_status=='ok' and pd.notna(x.prediction) and pd.notna(x.actual)]
            errors=[x.prediction-x.actual for x in good]; n=len(good)
            expected={'n':n,'MAE':math.fsum(abs(x) for x in errors)/n,'RMSE':math.sqrt(math.fsum(x*x for x in errors)/n),
                      'MASE':math.fsum(abs(x.prediction-x.actual)/x.mase_scale for x in good)/n,
                      'WAPE':100*math.fsum(abs(x) for x in errors)/math.fsum(abs(x.actual) for x in good),'Bias':math.fsum(errors)/n}
            for key,value in expected.items(): check(r['series_id']+':'+split+':'+key,value,r[split+'_'+key])
    for name in ['regional_priority_scores','presentation_priority_scores','region_presentation_priority_scores']:
        frame=tables[name]
        for r in frame.to_dict('records'):
            weights=json.loads(r['weight_configuration'])
            expected=math.fsum(r[k+'_score']*v for k,v in weights.items()) if r['rank_eligible'] else np.nan
            check(name+':'+r['entity_id']+':weighted arithmetic',expected,r['composite_score'])
            rank=1+sum(x>r['composite_score'] for x in frame.composite_score.dropna()) if r['rank_eligible'] else np.nan
            check(name+':'+r['entity_id']+':rank',rank,r['rank'],0)
    mix=tables['presentation_mix_scenarios']
    for sid,part in mix.groupby('scenario_id'):
        check(sid+':baseline shares',1,math.fsum(part.baseline_share),1e-10)
        check(sid+':scenario shares',1,math.fsum(part.scenario_share),1e-10)
        check(sid+':item conservation',tables['national_decision_summary'].recent_items.iloc[0],math.fsum(part.hypothetical_items),1e-6)
        check(sid+':nonnegative',True,bool(part.hypothetical_items.ge(0).all()),0)
    for r in tables['scenario_results'].to_dict('records'):
        expected_items=r['reference_items']*(1+r['volume_change_pct']/100)
        expected_nic=expected_items*r['reference_nic_per_item_gbp']*(1+r['nic_per_item_change_pct']/100)
        if r['scenario_name'].startswith('D:'):
            m=mix[mix.scenario_id.eq(r['scenario_id'])]
            expected_nic=math.fsum(x.scenario_share*r['reference_items']*x.recent_nic_per_item_gbp for x in m.itertuples())
        check(r['scenario_id']+':items',expected_items,r['hypothetical_items'])
        check(r['scenario_id']+':NIC',expected_nic,r['hypothetical_nic_gbp'],.01)
        check(r['scenario_id']+':delta',expected_nic-r['reference_nic_gbp'],r['nic_difference_gbp'],.01)
        if r['baseline_type']=='Model forecast baseline':
            check(r['scenario_id']+':as of',cfg['forecast_as_of'],r['forecast_as_of'].strftime('%Y-%m-%d'),0)
            check(r['scenario_id']+':no later baseline',True,r['baseline_end_date']<=r['forecast_as_of'],0)
    for r in tables['accounting_break_even_analysis'].itertuples():
        check('break even:'+str(r.volume_change_pct),r.reference_nic_gbp,r.reference_items*(1+r.volume_change_pct/100)*r.reference_nic_per_item_gbp*(1+r.offsetting_nic_per_item_change_pct/100),.01)
    for i,r in tables['forecast_hierarchy_gap_analysis'].iterrows():
        gap=r.regional_sum_forecast-r.direct_forecast
        check('hierarchy:'+str(i),gap,r.signed_gap_items)
        check('hierarchy pct:'+str(i),100*abs(gap)/r.direct_forecast,r.absolute_gap_pct)
    for r in tables['executive_recommendations'].to_dict('records'):
        source=tables[r['source_output']]; f=source[source[r['source_key']].astype(str).eq(r['source_key_value'])]
        check(r['recommendation_id']+':source unique',1,len(f),0)
        if len(f)==1: check(r['recommendation_id']+':metric',str(f[r['triggering_metric']].iloc[0]),r['observed_value'])
    for name,keys in contracts.items():
        check(name+':unique key',0,int(tables[name].duplicated(keys).sum()),0)
        if 'evidence_class' in tables[name]: check(name+':evidence classes',True,bool(tables[name].evidence_class.isin(cfg['evidence_classes']).all()),0)
    # Dashboard counts are derived independently from their source grains.
    for name,expected in [('regional_dashboard',grid.region_code.nunique()),('presentation_dashboard',grid.presentation_key.nunique()),
                           ('region_presentation_dashboard',len(grid[['region_code','presentation_key']].drop_duplicates())),
                           ('forecast_dashboard',len(inputs['p4/operational_forecasts']))]: check(name+':rows',expected,len(tables[name]),0)
    frame=pd.DataFrame(rows)
    if frame.status.ne('passed').any():
        return frame,False
    return frame,True
