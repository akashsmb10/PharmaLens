import streamlit as st
from dashboard.data_loader import load
from dashboard.filters import apply
from dashboard.metrics import totals,monthly,summarize,shares,annual_growth,indexed
from dashboard.components import cards,plot,table,empty,context
from dashboard.chart_factory import trend,bars,scatter
from dashboard.evidence import explain,methodology

def render():
    st.header('Regional Intelligence')
    fact=load('p2/cost_analytics'); labels=fact[['region_code','region_name']].drop_duplicates().set_index('region_code').region_name.to_dict()
    regions=st.multiselect('Regions',list(labels),default=list(labels),format_func=labels.get,key='region_selection')
    year=st.selectbox('Calendar year',sorted(fact.month.dt.year.unique()),index=len(fact.month.dt.year.unique())-1,key='region_year')
    metric=st.selectbox('Trend metric',['prescription_items','net_ingredient_cost_gbp','nic_per_item_gbp'],key='region_metric')
    indexed_view=st.checkbox('Index trends to first selected month = 100',key='region_index')
    all_selected=apply(fact,regions=regions); f=all_selected[all_selected.month.dt.year.eq(year)].copy()
    context(f'{year}; '+', '.join(labels[x] for x in regions)+'; annual growth compares with '+str(year-1))
    st.caption('Unadjusted observed totals, not population-normalized prescribing rates or healthcare efficiency.')
    if empty(f): return
    k=totals(f); cards([('Selected-region items',k['items'],'count'),('Selected-region NIC',k['nic_gbp'],'gbp'),('Weighted NIC/item',k['nic_per_item_gbp'],'gbp')])
    m=monthly(f,['region_code','region_name']); value=metric
    if indexed_view: m=indexed(m,metric,'region_code'); value='index_100'
    plot(trend(m,'month',value,'Regional monthly comparison',color='region_name',unit='First-month index = 100' if indexed_view else metric.replace('_',' ')),'regional_trend')
    # Denominators include all seven regions in the selected year, independent of selected subset.
    denominator=fact[fact.month.dt.year.eq(year)]
    summary=shares(summarize(f,['region_code','region_name']),denominator)
    growth=annual_growth(all_selected,int(year),['region_code','region_name'])
    summary=summary.merge(growth[['region_code','item_growth_pct','nic_growth_pct','status']],on='region_code',validate='one_to_one')
    left,right=st.columns(2)
    with left: plot(bars(summary,'region_name','item_growth_pct',f'Annual item growth · {year} versus {year-1}','Change (%)'),'regional_growth')
    with right: plot(bars(summary,'region_name','nic_per_item_gbp',f'Weighted NIC/item · {year}','GBP/item'),'regional_ratio')
    plot(scatter(summary,'prescription_items','item_growth_pct','Observed activity and annual growth','region_name'),'regional_scatter')
    with st.expander('Regional presentation mix and contribution',expanded=False):
        mix=summarize(f,['region_code','region_name','presentation_key','presentation_name'])
        mix['regional_share_pct']=100*mix.prescription_items/mix.groupby('region_code').prescription_items.transform('sum')
        plot(bars(mix,'region_name','regional_share_pct','Presentation mix within each selected region','Share (%)',color='presentation_name'),'regional_mix')
        plot(bars(summary,'region_name','item_share_pct','Contribution to all-region observed items in selected year','Share (%)'),'regional_contribution')
    table(summary,'filtered regional summary','regional_summary')
    selected=st.selectbox('Regional detail',regions,format_func=labels.get,key='region_detail')
    detail=summary[summary.region_code.eq(selected)]; table(detail,'selected regional detail','regional_detail')
    profile=load('p5/regional_dashboard'); profile=profile[profile.region_code.eq(selected)]
    st.caption('Separate validated profile: January 2023–December 2025 coverage/concentration; forecast errors July–December 2025. These fixed evidence periods do not change with the trend-year selector.')
    st.dataframe(profile[['region_name','concentration_hhi','holdout_n','holdout_MASE','holdout_WAPE','missing_cells','expected_cells','coverage_interpretation']],hide_index=True,use_container_width=True)
    explain('Phase 2 cost_analytics; Phase 5 regional_dashboard',f'{year}; growth {year} versus {year-1}; fixed profile periods stated above',
        'Sum observed selected-region rows; NIC/item=sum NIC/sum items. Annual growth uses the same selected regions in the current and preceding complete year; shares use all-region totals in the selected year.')
    methodology(['METRIC_DEFINITIONS.md','PHASE5_DECISION_FRAMEWORK.md'])
