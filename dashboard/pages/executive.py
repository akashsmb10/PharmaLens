import pandas as pd
import streamlit as st
from dashboard.data_loader import load
from dashboard.filters import apply
from dashboard.metrics import totals,monthly,summarize,shares,latest_growth
from dashboard.components import cards,plot,table,empty,context
from dashboard.chart_factory import trend,bars
from dashboard.evidence import explain,methodology

def render():
    st.header('Executive Overview')
    st.info('Historical observations · Retrospective forecasts and hypothetical scenarios have separate pages.')
    st.caption('NIC is NHS net ingredient cost, not manufacturer sales revenue.')
    fact=load('p2/cost_analytics'); dates=sorted(fact.month.unique())
    start,end=st.select_slider('Historical month range',options=dates,value=(dates[0],dates[-1]),format_func=lambda x:pd.Timestamp(x).strftime('%b %Y'),key='exec_period')
    f=apply(fact,start=start,end=end); context(f'{pd.Timestamp(start):%b %Y}–{pd.Timestamp(end):%b %Y}; all reported regions and presentations')
    if empty(f): return
    k=totals(f); g=latest_growth(f)
    cards([('Prescription items',k['items'],'count'),('Net ingredient cost',k['nic_gbp'],'gbp'),('Weighted NIC per item',k['nic_per_item_gbp'],'gbp'),
           ('Latest annual item growth',g['item_growth_pct'],'percent'),('Latest annual NIC growth',g['nic_growth_pct'],'percent'),('Reported regions',k['regions'],'count'),('Observed presentations',k['presentations'],'count')])
    st.caption(f"{k['presentations']} observed presentations. Annual growth requires twelve observed months in both comparison years inside the selected range.")
    m=monthly(f); left,right=st.columns(2)
    with left: plot(trend(m,'month','prescription_items','Observed prescription-item activity',unit='Prescription items'),'exec_items')
    with right: plot(trend(m,'month','net_ingredient_cost_gbp','Observed net ingredient cost',unit='NIC (GBP)'),'exec_nic')
    plot(trend(m,'month','nic_per_item_gbp','Weighted NIC per item',unit='GBP/item'),'exec_ratio')
    r=shares(summarize(f,['region_code','region_name']),f).sort_values('prescription_items',ascending=False)
    p=shares(summarize(f,['presentation_key','presentation_name']),f).sort_values('prescription_items',ascending=False)
    with st.expander('Regional contribution and presentation concentration',expanded=False):
        plot(bars(r,'region_name','item_share_pct','Regional observed item shares','Share (%)'),'exec_region')
        plot(bars(p,'presentation_name','item_share_pct','Presentation concentration in the selected window','Share (%)'),'exec_mix')
        table(p,'presentation shares','exec_presentation')
    st.subheader('Evidence-based findings')
    st.write(f"Largest observed regional share: {r.region_name.iloc[0]} ({r.item_share_pct.iloc[0]:.2f}%).")
    st.write(f"Largest presentation: {p.presentation_name.iloc[0]} ({p.item_share_pct.iloc[0]:.2f}% of observed items).")
    if pd.notna(g['item_growth_pct']): st.write(f"{g['year']} versus {g['baseline_year']}: items {g['item_growth_pct']:+.2f}%; NIC {g['nic_growth_pct']:+.2f}%.")
    st.write('NIC/item is an accounting ratio affected by presentation mix and within-presentation patterns; these data do not establish a causal price change.')
    decomposition=load('p3/cost_decomposition_diagnostics')
    eligible=[]
    years=set(f.month.dt.year)
    for x in decomposition.itertuples():
        a,b=map(int,x.comparison.split(' vs '))
        if a in years and b in years and f[f.month.dt.year.eq(a)].month.nunique()==f[f.month.dt.year.eq(b)].month.nunique()==12: eligible.append(x.comparison)
    if eligible:
        comparison=st.selectbox('Complete-year cost decomposition',eligible,index=len(eligible)-1)
        d=decomposition[decomposition.comparison.eq(comparison)]
        long=d[['item_volume_effect_gbp','presentation_mix_effect_gbp','within_presentation_cost_per_item_effect_gbp']].melt(var_name='component',value_name='GBP')
        plot(bars(long,'component','GBP','Exact accounting decomposition · '+comparison,'GBP'),'exec_decomposition')
        st.caption('Symmetric three-factor accounting identity; no causal or savings attribution.')
    else: st.info('Full-year decomposition is unavailable for this selected period.')
    explain('outputs/tables/cost_analytics.parquet; Phase 3 cost_decomposition_diagnostics',f'{pd.Timestamp(start):%Y-%m}–{pd.Timestamp(end):%Y-%m}',
        'Sum observed items/NIC; weighted NIC/item=sum NIC/sum items. Annual comparison requires complete years in the active window. Shares use active-window observed totals.')
    methodology(['METRIC_DEFINITIONS.md','PHASE3_STATISTICAL_FINDINGS.md'])
