import pandas as pd
import streamlit as st
from dashboard.data_loader import load
from dashboard.filters import apply
from dashboard.metrics import totals,monthly,summarize,shares,annual_growth
from dashboard.components import cards,plot,table,empty,context
from dashboard.chart_factory import trend,bars,heatmap
from dashboard.evidence import explain

def render():
    st.header('Presentation Intelligence')
    fact=load('p2/cost_analytics'); products=fact[['presentation_key','presentation_name']].drop_duplicates().set_index('presentation_key').presentation_name.to_dict()
    labels=fact[['region_code','region_name']].drop_duplicates().set_index('region_code').region_name.to_dict()
    choices=st.multiselect('Presentations',list(products),default=list(products),format_func=products.get,key='presentation_selection')
    regions=st.multiselect('Reported regions',list(labels),default=list(labels),format_func=labels.get,key='presentation_regions')
    years=sorted(fact.month.dt.year.unique()); year=st.selectbox('Presentation calendar year',years,index=len(years)-1,key='presentation_year')
    metric=st.selectbox('Presentation trend metric',['prescription_items','net_ingredient_cost_gbp','nic_per_item_gbp'],key='presentation_metric')
    denominator=apply(fact,regions=regions); denominator=denominator[denominator.month.dt.year.eq(year)]
    f=apply(denominator,presentations=choices)
    context(f'{year}; {len(regions)} selected regions; {len(choices)} selected presentations. Shares use all presentations in those regions/year.')
    st.caption('Prescription-item counts; tablet and liquid physical quantities are never combined.')
    if empty(f): return
    k=totals(f); cards([('Selected presentation items',k['items'],'count'),('Selected presentation NIC',k['nic_gbp'],'gbp'),('Weighted NIC/item',k['nic_per_item_gbp'],'gbp')])
    summary=shares(summarize(f,['presentation_key','presentation_name','unit_of_measure']),denominator)
    growth=annual_growth(apply(fact,regions=regions,presentations=choices),int(year),['presentation_key'])
    summary=summary.merge(growth[['presentation_key','item_growth_pct','nic_growth_pct','status']],on='presentation_key',validate='one_to_one').sort_values('prescription_items',ascending=False)
    plot(bars(summary,'presentation_name','prescription_items','Selected-year presentation item contribution','Prescription items'),'presentation_contribution')
    plot(trend(monthly(f,['presentation_key','presentation_name']),'month',metric,'Selected presentation trends','presentation_name',metric.replace('_',' ')),'presentation_trend')
    with st.expander('Item / NIC trends, weighted cost and regional distribution',expanded=False):
        m=monthly(f,['presentation_key','presentation_name'])
        plot(trend(m,'month','prescription_items','Observed monthly items','presentation_name','Prescription items'),'presentation_items')
        plot(trend(m,'month','net_ingredient_cost_gbp','Observed monthly NIC','presentation_name','NIC (GBP)'),'presentation_nic')
        plot(bars(summary,'presentation_name','nic_per_item_gbp','Selected-year weighted NIC/item','GBP/item'),'presentation_ratio')
        mix=summarize(f,['region_code','region_name','presentation_key','presentation_name'])
        plot(bars(mix,'region_name','prescription_items','Observed regional distribution','Prescription items','presentation_name'),'presentation_mix')
    table(summary,'filtered presentation summary','presentation_summary')
    absent=load('p2/missing_series_months'); grid=pd.concat([fact[['month','region_code','presentation_key']].assign(observed=True),absent[['month','region_code','presentation_key']].assign(observed=False)],ignore_index=True)
    grid=apply(grid,regions=regions,presentations=choices); grid=grid[grid.month.dt.year.eq(year)]
    grid['presentation_name']=grid.presentation_key.map(products)
    coverage=grid.groupby(['presentation_name','month'])['observed'].mean().mul(100).unstack('month')
    coverage.columns=coverage.columns.strftime('%b')
    plot(heatmap(coverage,'Observed-cell coverage across selected regions','% observed'),'presentation_coverage')
    st.caption('Coverage uses observed plus absence-only cells. Unknown applicability remains a caveat; an absence is not a known zero.')
    priorities=load('p5/presentation_priority_scores'); statuses=priorities[priorities.presentation_key.isin(choices)]
    st.subheader('Validated Phase 5 monitoring evidence · fixed 2023–2025 scope')
    unscored=statuses[~statuses.rank_eligible]
    if len(unscored): st.info(f'{len(unscored)} selected presentations: Not scored — insufficient required forecast evidence.')
    st.dataframe(statuses[['presentation_key','presentation_name','rank_eligible','monitoring_tier','missing_components']],hide_index=True,use_container_width=True)
    explain('Phase 2 cost_analytics and missing_series_months; Phase 5 presentation_priority_scores',f'{year}; annual change {year} versus {year-1}; priorities remain fixed-window evidence',
        'Selected-region/year observed sums; shares divide by all presentations in the same regions/year; weighted ratios; absence-only cells included in coverage. Unscored presentations have no invented rank.')
