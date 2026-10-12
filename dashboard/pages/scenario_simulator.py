import pandas as pd
import streamlit as st
from dashboard.data_loader import load
from dashboard.filters import apply
from dashboard.metrics import totals,summarize
from dashboard.scenarios import simulate,two_way,mix_simulation
from dashboard.components import cards,plot,table,empty,context
from dashboard.chart_factory import bars,heatmap
from dashboard.evidence import explain,methodology

def render():
    st.header('Scenario Simulator')
    st.info('Scenario outputs are hypothetical accounting sensitivities, not forecasts, clinical recommendations, or realized financial outcomes.')
    fact=load('p2/cost_analytics'); kind=st.selectbox('Baseline type',['Observed calendar year','Frozen national forecast · Dec 2025 cutoff'],key='scenario_baseline_type')
    products=fact[['presentation_key','presentation_name']].drop_duplicates().set_index('presentation_key').presentation_name.to_dict()
    labels=fact[['region_code','region_name']].drop_duplicates().set_index('region_code').region_name.to_dict()
    if kind=='Observed calendar year':
        years=sorted(fact.month.dt.year.unique()); year=st.selectbox('Scenario baseline year',years,index=len(years)-1,key='scenario_year')
        region=st.selectbox('Scenario region',['All reported regions']+list(labels),format_func=lambda x:labels.get(x,x),key='scenario_region')
        presentation=st.selectbox('Scenario presentation',['All presentations']+list(products),format_func=lambda x:products.get(x,x),key='scenario_presentation')
        f=fact[fact.month.dt.year.eq(year)]; f=apply(f,regions=None if region=='All reported regions' else [region],presentations=None if presentation=='All presentations' else [presentation])
        if empty(f): return
        k=totals(f); baseline_items=k['items']; baseline_nic=k['nic_gbp']; description=f'Observed {year}; {labels.get(region,region)}; {products.get(presentation,presentation)}'
    else:
        op=load('p5/forecast_dashboard'); op=op[op.series_id.eq('England')]
        date=st.selectbox('Retrospective forecast month',op.forecast_month.tolist(),format_func=lambda x:x.strftime('%b %Y'),key='scenario_forecast_month')
        selected=op[op.forecast_month.eq(date)].iloc[0]
        baseline_items=selected.point_forecast
        reference=fact[fact.month.le(selected.training_end_date)&fact.month.dt.year.eq(selected.training_end_date.year)]
        if reference.month.nunique()!=12: st.info('Complete historical cost reference is unavailable.'); return
        unit=totals(reference)['nic_per_item_gbp']; baseline_nic=baseline_items*unit
        description=f'As-of December 2025 retrospective forecast for {date:%b %Y}; fixed {selected.training_end_date.year} weighted NIC/item assumption'
        st.caption('Cost is a hypothetical conversion at a fixed historical ratio, not a cost forecast. No future actuals are used.')
    context(description)
    volume=st.slider('Hypothetical prescription-item change (%)',-20.,20.,0.,step=1.,key='scenario_volume')
    cost=st.slider('Hypothetical NIC-per-item change (%)',-20.,20.,0.,step=1.,key='scenario_cost')
    try: result=simulate(baseline_items,baseline_nic,volume,cost,description)
    except ValueError as exc: st.info(str(exc)); return
    r=result.iloc[0]
    cards([('Baseline items',r.baseline_items,'count'),('Baseline NIC',r.baseline_nic_gbp,'gbp'),('Baseline NIC/item',r.baseline_nic_per_item_gbp,'gbp'),
           ('Hypothetical items',r.hypothetical_items,'count'),('Hypothetical NIC',r.hypothetical_nic_gbp,'gbp'),('NIC difference',r.nic_difference_gbp,'gbp')])
    st.write(f'Hypothetical NIC difference: {r.nic_difference_pct:+.2f}%. Accounting offset for {volume:+.0f}% items: {r.break_even_cost_change_pct:+.6f}% NIC/item.')
    st.caption('Hypothetical NIC = baseline items × (1 + item change) × baseline NIC/item × (1 + NIC/item change). Accounting break-even is not profitability.')
    plot(bars(pd.DataFrame({'case':['Baseline','Hypothetical'],'nic_gbp':[baseline_nic,r.hypothetical_nic_gbp]}),'case','nic_gbp','Baseline and hypothetical NIC','GBP'),'scenario_comparison')
    sensitivity=two_way(baseline_items,baseline_nic)
    plot(heatmap(sensitivity.pivot(index='cost_pct',columns='volume_pct',values='hypothetical_nic_gbp'),'Two-way sensitivity · assumed cost rows and volume columns','GBP NIC'),'scenario_heatmap')
    table(result,'current scenario assumptions and results','scenario_result')
    table(sensitivity,'two-way accounting sensitivity','scenario_sensitivity')
    if kind=='Observed calendar year' and presentation=='All presentations':
        with st.expander('Optional mix-only accounting redistribution',expanded=False):
            p=summarize(f,['presentation_key','presentation_name']).rename(columns={'prescription_items':'recent_items','nic_per_item_gbp':'recent_nic_per_item_gbp'})
            if len(p)<2: st.info('At least two observed presentations are required for a mix transfer.'); return
            names=p.set_index('presentation_key').presentation_name.to_dict(); ordered=p.sort_values(['recent_items','presentation_key'],ascending=[False,True]).presentation_key.tolist()
            donor=st.selectbox('Mix donor presentation',ordered,format_func=names.get,key='mix_donor')
            receivers=[x for x in ordered if x!=donor]; receiver=st.selectbox('Mix receiver presentation',receivers,format_func=names.get,key='mix_receiver')
            max_transfer=min(20.,float(100*p[p.presentation_key.eq(donor)].recent_items.iloc[0]/baseline_items))
            if 'mix_transfer' in st.session_state:
                st.session_state.mix_transfer=min(max_transfer,max(0.,st.session_state.mix_transfer))
            transfer=st.number_input('Item-share transfer (percentage points)',min_value=0.,max_value=max_transfer,value=min(1.,max_transfer),step=.1,key='mix_transfer')
            try: mix=mix_simulation(p,baseline_items,donor,receiver,transfer)
            except ValueError as exc: st.info(str(exc)); return
            st.write(f'Mix-only items: {mix.hypothetical_items.sum():,.0f}; hypothetical NIC £{mix.hypothetical_nic_gbp.sum():,.2f}. Volume/cost sliders do not apply to this separate mix-only simulation.')
            st.caption('Nonnegative shares sum to 100%; total items preserved. Fixed presentation NIC/item; accounting redistribution, not clinical substitution advice.')
            table(mix,'current mix-only scenario','scenario_mix')
    explain('Phase 2 cost_analytics; frozen Phase 5 forecast_dashboard',description,'Observed weighted cost reference or frozen point forecast; explicit hypothetical multiplicative item/cost changes; constrained mix shares.',
        'Hypothetical scenario','No probabilities, calibrated uncertainty, observed savings, manufacturer profit or treatment recommendation.')
    methodology(['PHASE5_SCENARIO_METHODOLOGY.md'])
