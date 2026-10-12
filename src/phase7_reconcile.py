"""Independent arithmetic from immutable records; never fits or selects a model."""
from decimal import Decimal
import json
import math
import re
import numpy as np
import pandas as pd
from .common import ROOT,write_json,sha256

def reconcile(root=ROOT):
    rows=[]
    def check(name,expected,recomputed,tolerance,source):
        a=float(expected); b=float(recomputed)
        passed=(math.isnan(a) and math.isnan(b)) or (math.isfinite(a) and math.isfinite(b) and abs(a-b)<=tolerance)
        rows.append({'metric':name,'expected':a,'recomputed':b,'difference':b-a,'tolerance':tolerance,'status':'PASS' if passed else 'FAIL','source':source})
    def table(phase,name):
        path=f'outputs/{"tables" if phase==2 else "phase"+str(phase)+"/tables"}/{name}.parquet'
        return pd.read_parquet(root/path)
    fact=table(2,'cost_analytics'); source=pd.read_parquet(root/'data/processed/source_rows.parquet')
    monthly=pd.read_parquet(root/'data/processed/monthly_prescribing.parquet')
    raw=[]
    for path in sorted((root/'data/raw').glob('pca_*.json')):
        if re.fullmatch(r'pca_\d{6}_[a-f0-9]{10}_\d{6}\.json',path.name): raw.extend(json.loads(path.read_text())['result']['records'])
    raw_items=sum(Decimal(str(r['ITEMS'])) for r in raw); raw_nic=sum(Decimal(str(r['NIC'])) for r in raw)
    check('raw source records',len(raw),len(source),0,'API snapshots → source_rows')
    check('source-to-clean items',raw_items,monthly['items'].sum(),0,'raw API ITEMS → monthly_prescribing.items')
    check('source-to-clean NIC',raw_nic,monthly.nic_gbp.sum(),.01,'raw API NIC → monthly_prescribing.nic_gbp')
    check('historical items',raw_items,fact.prescription_items.sum(),0,'raw API → Phase 2 cost_analytics')
    check('historical NIC',raw_nic,fact.net_ingredient_cost_gbp.sum(),.01,'raw API → Phase 2 cost_analytics')
    national=table(2,'national_monthly_trends')
    for r in national.itertuples():
        f=fact[fact.month.eq(r.month)]
        check(f'{r.month:%Y-%m} items',r.prescription_items,sum(float(x) for x in f.prescription_items),0,'Phase 2 national_monthly_trends vs fact rows')
        check(f'{r.month:%Y-%m} NIC',r.net_ingredient_cost_gbp,sum(float(x) for x in f.net_ingredient_cost_gbp),.01,'Phase 2 national_monthly_trends vs fact rows')
    for group in ['region_code','presentation_key']:
        totals=fact.groupby(group)[['prescription_items','net_ingredient_cost_gbp']].sum()
        check(group+' item aggregate identity',raw_items,totals.prescription_items.sum(),0,'Phase 2 fact grouping')
        check(group+' NIC aggregate identity',raw_nic,totals.net_ingredient_cost_gbp.sum(),.01,'Phase 2 fact grouping')
        shares=[100*x/float(raw_items) for x in totals.prescription_items]
        check(group+' item shares sum',100,sum(shares),1e-9,'independent group / full observed items')
    annual=fact.groupby(fact.month.dt.year)[['prescription_items','net_ingredient_cost_gbp']].sum()
    annual_saved=table(2,'national_annual_trends')
    for r in annual_saved.itertuples():
        check(str(r.calendar_year)+' weighted NIC/item',r.ingredient_cost_per_item_gbp,
            annual.loc[r.calendar_year,'net_ingredient_cost_gbp']/annual.loc[r.calendar_year,'prescription_items'],1e-10,'annual observed sum ratio')
        if pd.notna(r.prior_year_items):
            check(str(r.calendar_year)+' item annual growth',r.items_annual_growth_pct,100*(annual.loc[r.calendar_year,'prescription_items']/annual.loc[r.calendar_year-1,'prescription_items']-1),1e-8,'national_annual_trends vs fact annual sums')
            check(str(r.calendar_year)+' NIC annual growth',r.cost_annual_growth_pct,100*(annual.loc[r.calendar_year,'net_ingredient_cost_gbp']/annual.loc[r.calendar_year-1,'net_ingredient_cost_gbp']-1),1e-8,'national_annual_trends vs fact annual sums')
    decomposition=table(3,'cost_decomposition_diagnostics')
    for r in decomposition.itertuples():
        y1,y0=[int(x) for x in r.comparison.split(' vs ')]
        p0=fact[fact.month.dt.year.eq(y0)].groupby('presentation_key')[['prescription_items','net_ingredient_cost_gbp']].sum().sort_index()
        p1=fact[fact.month.dt.year.eq(y1)].groupby('presentation_key')[['prescription_items','net_ingredient_cost_gbp']].sum().sort_index()
        v0=p0.prescription_items.sum(); v1=p1.prescription_items.sum(); dv=v1-v0
        s0=p0.prescription_items/v0; ds=p1.prescription_items/v1-s0
        c0=p0.net_ingredient_cost_gbp/p0.prescription_items; dc=p1.net_ingredient_cost_gbp/p1.prescription_items-c0
        dot=lambda a,b:sum(float(x)*float(y) for x,y in zip(a,b))
        interaction=dv*dot(ds,dc)/3
        volume=dv*dot(s0,c0)+dv*(dot(ds,c0)+dot(s0,dc))/2+interaction
        mix=v0*dot(ds,c0)+(dv*dot(ds,c0)+v0*dot(ds,dc))/2+interaction
        within=v0*dot(s0,dc)+(dv*dot(s0,dc)+v0*dot(ds,dc))/2+interaction
        for name,value in [('item_volume_effect_gbp',volume),('presentation_mix_effect_gbp',mix),('within_presentation_cost_per_item_effect_gbp',within)]:
            check(r.comparison+' '+name,getattr(r,name),value,.01,'closed-form interaction allocation; independent of permutation implementation')
        check(r.comparison+' decomposition sum',r.observed_cost_change_gbp,volume+mix+within,.01,'three-factor closed-form identity')
    back=table(4,'backtest_predictions'); saved=table(4,'holdout_model_metrics')
    support={}
    for x in back[back.split_type.eq('holdout')].itertuples():
        key=(x.series_id,x.origin_date,x.horizon)
        if x.model_status=='ok' and pd.notna(x.prediction): support.setdefault(key,set()).add(x.variant)
    complete={key for key,variants in support.items() if len(variants)==5}
    for r in saved.itertuples():
        g=back[back.split_type.eq('holdout')&back.aggregation_level.eq(r.aggregation_level)&back.variant.eq(r.variant)&back.model_status.eq('ok')].dropna(subset=['prediction','actual'])
        g=g[[ (x.series_id,x.origin_date,x.horizon) in complete for x in g.itertuples() ]]
        errors=[float(x.prediction-x.actual) for x in g.itertuples()]
        values={'MAE':sum(abs(e) for e in errors)/len(errors),'RMSE':math.sqrt(sum(e*e for e in errors)/len(errors)),
            'WAPE':100*sum(abs(e) for e in errors)/sum(abs(float(a)) for a in g.actual),
            'MASE':sum(abs(float(x.prediction-x.actual))/float(x.mase_scale) for x in g.itertuples())/len(g),'Bias':sum(errors)/len(errors)}
        for name,value in values.items(): check(r.aggregation_level+'/'+r.variant+'/'+name,getattr(r,name),value,1e-6,'stored origin/horizon prediction rows; independent Python reductions')
    alignment=[(x.target_date.year-x.origin_date.year)*12+x.target_date.month-x.origin_date.month==x.horizon for x in back.itertuples()]
    check('forecast origin-target alignment',len(back),sum(alignment),0,'backtest_predictions date arithmetic')
    decisions=table(4,'model_selection_decisions'); check('holdout selection is frozen',len(decisions),int(decisions.frozen_at.eq(pd.Timestamp('2025-06-01')).sum()),0,'model_selection_decisions frozen_at')
    # Independently verify every stored origin-specific scaling denominator from observed history.
    for (sid,origin),g in back.groupby(['series_id','origin_date']):
        f=fact[fact.month.le(origin)]
        if sid!='England': f=f[f.region_code.eq(sid.split('::')[0])]
        if '::' in sid: f=f[f.presentation_key.eq(sid.split('::',1)[1])]
        y=f.groupby('month').prescription_items.sum().tolist(); scale=sum(abs(b-a) for a,b in zip(y,y[1:]))/(len(y)-1)
        check(sid+'/'+str(origin.date())+' train-only MASE scale',g.mase_scale.iloc[0],scale,1e-7,'observed history through origin only')
    cfg=json.loads((root/'config/decision_intelligence.yaml').read_text())
    for level in ['regional','presentation','region_presentation']:
        features=table(5,level+'_decision_features').set_index('entity_id'); scores=table(5,level+'_priority_scores').set_index('entity_id')
        raw_components={'activity':features.recent_items,'change':features.item_growth_pct.abs(),'cost':features.nic_per_item_change_pct.abs(),
            'forecast':features.holdout_MASE,'quality':features.missing_cell_pct+features.extreme_flags_per_1000_observed_cells}
        normalized={}
        for component,values in raw_components.items():
            valid=values.dropna().tolist(); normalized[component]={}
            for sid,value in values.items():
                if pd.isna(value): expected=np.nan
                elif len(set(valid))==1: expected=50.
                else: expected=100*(sum(v<value for v in valid)+(sum(v==value for v in valid)-1)/2)/(len(valid)-1)
                normalized[component][sid]=expected
                check(level+'/'+str(sid)+'/'+component+' component',scores.loc[sid,component+'_score'],expected,1e-8,'pairwise midrank independent of pandas.rank')
        for sid in features.index:
            parts=[normalized[c][sid] for c in cfg['weights']]; value=sum(normalized[c][sid]*weight for c,weight in cfg['weights'].items()) if all(pd.notna(parts)) else np.nan
            check(level+'/'+str(sid)+' composite',scores.loc[sid,'composite_score'],value,1e-8,'weighted independent component scores; complete required evidence only')
    scenarios=table(5,'scenario_results')
    for r in scenarios.itertuples():
        if r.scenario_id.startswith('D_'): continue
        check(r.scenario_id+' NIC',r.hypothetical_nic_gbp,r.reference_items*r.reference_nic_per_item_gbp*(1+r.volume_change_pct/100)*(1+r.nic_per_item_change_pct/100),.01,'independent multiplicative accounting')
    for r in table(5,'accounting_break_even_analysis').itertuples():
        check('accounting offset '+str(r.volume_change_pct),r.offsetting_nic_per_item_change_pct,100*(1/(1+r.volume_change_pct/100)-1),1e-10,'reciprocal multiplicative offset')
    for sid,g in table(5,'presentation_mix_scenarios').groupby('scenario_id'):
        check(sid+' mix item conservation',g.baseline_items_at_total.sum(),g.hypothetical_items.sum(),1e-6,'baseline and transferred shares')
        check(sid+' mix shares',1,g.scenario_share.sum(),1e-10,'constrained transfer shares')
    from dashboard.metrics import totals
    for year in [2023,2024,2025]:
        f=fact[fact.month.dt.year.eq(year)]; display=totals(f)
        check(str(year)+' dashboard items',annual.loc[year,'prescription_items'],display['items'],0,'dashboard totals vs independent grouped fact')
        check(str(year)+' dashboard weighted NIC/item',annual.loc[year,'net_ingredient_cost_gbp']/annual.loc[year,'prescription_items'],display['nic_per_item_gbp'],1e-10,'dashboard totals vs independent aggregate ratio')
    frame=pd.DataFrame(rows); out=root/'outputs/phase7/validation'; out.mkdir(parents=True,exist_ok=True)
    frame.to_csv(out/'numerical_reconciliation.csv',index=False)
    facts={'source_records':len(source),'analytical_rows':len(monthly),'months':fact.month.nunique(),'regions':fact.region_code.nunique(),'presentations':fact.presentation_key.nunique(),
        'historical_items':int(raw_items),'historical_nic_gbp':float(raw_nic),'items_2025':int(annual.loc[2025,'prescription_items']),
        'nic_2025_gbp':float(annual.loc[2025,'net_ingredient_cost_gbp']),
        'item_growth_2025_pct':100*(annual.loc[2025,'prescription_items']/annual.loc[2024,'prescription_items']-1),
        'nic_growth_2025_pct':100*(annual.loc[2025,'net_ingredient_cost_gbp']/annual.loc[2024,'net_ingredient_cost_gbp']-1),
        'selected_national_model':decisions[decisions.series_id.eq('England')].selected_variant.iloc[0],
        'national_holdout_models':saved[saved.aggregation_level.eq('national')].replace({np.nan:None}).to_dict('records'),
        'operational_forecasts':table(5,'forecast_dashboard').query("series_id=='England'")[['forecast_month','point_forecast']].assign(forecast_month=lambda f:f.forecast_month.dt.strftime('%Y-%m')).to_dict('records'),
        'unscored_presentations':int((~table(5,'presentation_priority_scores').rank_eligible).sum()),'regional_unstable_ranks':int(table(5,'priority_rank_instability').query("aggregation_level=='regional'").unstable_rank.sum()),
        'manual_review_series':int(table(5,'forecast_risk_register').manual_review.sum()),'scenarios':len(scenarios),'investigations':len(table(5,'recommendations_dashboard')),
        'decomposition_2025':decomposition.query("comparison=='2025 vs 2024'").replace({np.nan:None}).to_dict('records')[0]}
    write_json(out/'verified_facts.json',facts)
    result={'checks':len(frame),'failed':int(frame.status.eq('FAIL').sum()),'sha256':sha256(out/'numerical_reconciliation.csv')}
    write_json(out/'numerical_summary.json',result)
    print(json.dumps(result),flush=True)
    if result['failed']: raise AssertionError('Independent reconciliation discrepancy')
    return result

if __name__=='__main__': reconcile()
