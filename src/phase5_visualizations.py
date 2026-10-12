"""Source-noted static charts distinguish observations, model results and scenarios."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from .common import ROOT

def generate(t,root=ROOT):
    directory=root/'outputs/phase5/charts'; directory.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.size':10,'axes.titlesize':14,'axes.spines.top':False,'axes.spines.right':False})
    saved=[]; blue='#186b98'; orange='#bf7422'
    def save(name,title,source,evidence='Observed history / exploratory monitoring policy'):
        fig=plt.gcf(); fig.suptitle(title,x=.04,ha='left',fontweight='bold')
        fig.text(.04,.015,f'{evidence}\nSource: outputs/phase5/tables/{source}.csv · NHSBSA atorvastatin, England; no population adjustment',fontsize=8,color='#555555')
        fig.tight_layout(rect=[.02,.075,.98,.92]); path=directory/(name+'.png'); fig.savefig(path,dpi=180); plt.close(fig)
        saved.append(str(path.relative_to(root)).replace('\\','/'))
    r=t['regional_priority_scores']; p=t['presentation_priority_scores']; rp=t['forecast_reliability_profiles']; regions=rp[rp.aggregation_level.eq('regional')]
    fig,ax=plt.subplots(figsize=(11,6)); scatter=ax.scatter(r.item_growth_pct,r.composite_score,s=50+r.historical_item_share_pct*15,c=r.holdout_MASE,cmap='viridis')
    for x in r.itertuples():
        right=x.item_growth_pct>r.item_growth_pct.quantile(.75)
        ax.annotate(x.region_name,(x.item_growth_pct,x.composite_score),xytext=(-5 if right else 5,8),ha='right' if right else 'left',textcoords='offset points',fontsize=8)
    ax.set(xlabel='2025 versus 2024 item growth (%)',ylabel='Monitoring score (0–100)'); fig.colorbar(scatter,ax=ax,label='Holdout MASE'); ax.set_ylim(0,105)
    save('01_regional_priority_matrix','Regional monitoring priorities','regional_priority_scores')
    fig,ax=plt.subplots(figsize=(11,6)); valid=p[p.rank_eligible].sort_values('composite_score'); ax.barh(valid.presentation_name,valid.composite_score,color=blue); ax.set_xlim(0,100); ax.set_xlabel('Policy monitoring score (0–100)')
    ax.text(.98,.03,f'{(~p.rank_eligible).sum()} presentations unscored: required evidence missing',transform=ax.transAxes,ha='right',fontsize=9)
    save('02_presentation_priority','Scored presentation priorities; omissions are explicit','presentation_priority_scores')
    fig,ax=plt.subplots(figsize=(11,6)); columns=[k+'_score' for k in ['activity','change','cost','forecast','quality']]
    x=np.arange(len(r)); width=.16
    for i,c in enumerate(columns): ax.bar(x+(i-2)*width,r[c],width,label=c.replace('_score',''))
    ax.set_xticks(x,r.region_name.str.replace(' AND ',' & '),rotation=25,ha='right',fontsize=8); ax.set_ylim(0,105); ax.set_ylabel('Component percentile score'); ax.legend(ncol=5,fontsize=8)
    save('03_component_scores','Five retained components; consistent review direction','regional_priority_scores')
    s=t['priority_sensitivity_results']; s=s[s.aggregation_level.eq('regional') & s.normalization.eq('percentile')]
    pivot=s.pivot(index='entity_id',columns='scheme',values='rank_change')
    fig,ax=plt.subplots(figsize=(12,5)); im=ax.imshow(pivot.to_numpy(float),cmap='RdBu_r',vmin=-6,vmax=6,aspect='auto'); ax.set_yticks(range(len(pivot)),pivot.index); ax.set_xticks(range(len(pivot.columns)),pivot.columns,rotation=35,ha='right'); fig.colorbar(im,ax=ax,label='Alternative minus baseline rank')
    save('04_priority_sensitivity','Regional ranking sensitivity to policy weights','priority_sensitivity_results')
    st=t['priority_rank_instability']; st=st[st.aggregation_level.eq('regional')]
    fig,ax=plt.subplots(figsize=(10,5)); ax.bar(st.entity_id,st.max_absolute_rank_change,color=orange); ax.axhline(st.instability_threshold_ranks.iloc[0],color='#555',linestyle='--',label='Configured instability threshold'); ax.set_ylabel('Maximum absolute rank movement'); ax.legend()
    save('05_rank_stability','Rank stability across documented alternatives','priority_rank_instability')
    fig,ax=plt.subplots(figsize=(11,6)); ax.scatter(r.item_growth_pct,r.holdout_MASE,s=90,color=blue)
    for x in r.itertuples():
        right=x.item_growth_pct>r.item_growth_pct.quantile(.75)
        ax.annotate(x.region_name,(x.item_growth_pct,x.holdout_MASE),xytext=(-5 if right else 5,8),ha='right' if right else 'left',textcoords='offset points',fontsize=8)
    ax.set(xlabel='2025 versus 2024 item growth (%)',ylabel='Holdout selected-model MASE'); ax.axhline(1,color='#999',linestyle='--')
    save('06_growth_forecast_risk','Historical regional growth and selected-model error','regional_growth_risk_matrix','Observed change and validated historical model results')
    z=t['presentation_decision_features'].dropna(subset=['item_growth_pct','concentration_hhi'])
    fig,ax=plt.subplots(figsize=(10,6)); ax.scatter(z.concentration_hhi,z.item_growth_pct,s=30+z.historical_item_share_pct*5,color=blue)
    for x in z[z.historical_item_share_pct>5].itertuples(): ax.annotate(x.presentation_name,(x.concentration_hhi,x.item_growth_pct),fontsize=8)
    ax.set(xlabel='Regional concentration HHI (0–1)',ylabel='2025 versus 2024 item growth (%)'); ax.text(.02,.98,f'{len(z)} complete annual comparisons',transform=ax.transAxes,va='top')
    save('07_presentation_concentration_growth','Presentation concentration and observed growth','presentation_concentration_risk')
    z=t['presentation_decision_features'].dropna(subset=['nic_per_item_change_pct']).sort_values('nic_per_item_change_pct')
    fig,ax=plt.subplots(figsize=(11,8)); ax.barh(z.presentation_name,z.nic_per_item_change_pct,color=blue); ax.axvline(0,color='#888'); ax.set_xlabel('2025 versus 2024 weighted NIC/item change (%)')
    save('08_nic_per_item_change','Presentation NIC/item changes; no causal price claim','presentation_decision_features','Verified descriptive finding')
    fig,ax=plt.subplots(figsize=(11,6)); ax.barh(regions.region_name,regions.holdout_MASE,color=blue); ax.axvline(1,color='#888',linestyle='--'); ax.set_xlabel('Holdout MASE'); ax.text(.98,.03,'15 overlapping forecasts per region; intervals unavailable',transform=ax.transAxes,ha='right')
    save('09_regional_reliability','Selected regional forecast error','forecast_reliability_profiles','Validated historical model result')
    h=t['forecast_horizon_risk']; h=h[h.series_id.eq('England') & h.split_type.eq('holdout')].sort_values('horizon')
    fig,ax=plt.subplots(figsize=(9,5)); ax.bar(h.horizon,h.MASE,color=blue)
    for x in h.itertuples(): ax.annotate(f'n={x.n}',(x.horizon,x.MASE),xytext=(0,5),textcoords='offset points',ha='center')
    ax.set_xticks([1,2,3]); ax.set(xlabel='True forecast horizon (months)',ylabel='National selected ETS holdout MASE')
    save('10_horizon_reliability','Horizon-specific error with different target support','forecast_horizon_risk','Validated historical model result')
    fig,ax=plt.subplots(figsize=(11,6)); ax.barh(regions.region_name,regions.bias_pct,color=blue); ax.axvline(0,color='#888'); ax.set_xlabel('Mean prediction minus actual / mean actual (%)')
    save('11_forecast_bias','Signed regional forecast bias','forecast_reliability_profiles','Validated historical model result')
    g=t['forecast_hierarchy_gap_analysis']; g=g[g.context.eq('operational')]
    fig,ax=plt.subplots(figsize=(9,5)); ax.bar(g.forecast_month.dt.strftime('%b %Y'),g.signed_gap_items/1000,color=blue); ax.axhline(0,color='#888'); ax.set_ylabel('Sum seven regions minus direct national (thousand items)')
    save('12_hierarchy_gaps','Retrospective forecast coherence gaps; no rescaling','forecast_hierarchy_gap_analysis','As-of-December-2025 model forecasts; coherence is not accuracy')
    scenarios=t['scenario_results']
    for prefix,name,title in [('A:','13_volume_sensitivity','Hypothetical volume sensitivity'),('B:','14_cost_sensitivity','Hypothetical NIC/item sensitivity')]:
        z=scenarios[scenarios.scenario_name.str.startswith(prefix)].sort_values('volume_change_pct' if prefix=='A:' else 'nic_per_item_change_pct')
        column='volume_change_pct' if prefix=='A:' else 'nic_per_item_change_pct'
        fig,ax=plt.subplots(figsize=(9,5)); ax.plot(z[column],z.hypothetical_nic_gbp/1e6,'o-',color=orange); ax.set(xlabel=column.replace('_',' ')+' (assumption)',ylabel='Hypothetical annual NIC (GBP million)')
        save(name,title+' at fixed remaining assumptions','scenario_results','Hypothetical scenario; 2025 observed accounting baseline')
    c=scenarios[scenarios.scenario_name.str.startswith('C:')].pivot(index='nic_per_item_change_pct',columns='volume_change_pct',values='hypothetical_nic_gbp')/1e6
    fig,ax=plt.subplots(figsize=(8,6)); im=ax.imshow(c,cmap='YlOrBr',origin='lower'); ax.set_xticks(range(len(c.columns)),c.columns); ax.set_yticks(range(len(c)),c.index); ax.set(xlabel='Assumed item volume change (%)',ylabel='Assumed NIC/item change (%)')
    for i in range(len(c)):
        for j in range(len(c.columns)): ax.text(j,i,f'{c.iloc[i,j]:.2f}',ha='center',va='center',fontsize=9)
    fig.colorbar(im,ax=ax,label='Hypothetical annual NIC (GBP million)')
    save('15_two_way_sensitivity','Combined accounting sensitivity','scenario_results','Hypothetical scenario; not probabilities or realized savings')
    mix=scenarios[scenarios.scenario_name.str.startswith('D:')]
    fig,ax=plt.subplots(figsize=(9,5)); ax.bar(mix.scenario_id,mix.nic_difference_gbp/1e6,color=orange); ax.set_ylabel('Hypothetical NIC difference (GBP million)'); ax.axhline(0,color='#888')
    save('16_mix_sensitivity','Mix-only item conservation; configured 1/2/5 percentage-point transfers','presentation_mix_scenarios','Hypothetical accounting redistribution; no clinical recommendation')
    be=t['accounting_break_even_analysis'].sort_values('volume_change_pct')
    fig,ax=plt.subplots(figsize=(9,5)); ax.plot(be.volume_change_pct,be.offsetting_nic_per_item_change_pct,'o-',color=orange); ax.axhline(0,color='#888'); ax.set(xlabel='Assumed item volume change (%)',ylabel='NIC/item change maintaining baseline NIC (%)')
    save('17_accounting_break_even','Algebraic NIC equality; not financial profitability','accounting_break_even_analysis','Hypothetical scenario')
    count=t['executive_recommendations'].groupby(['priority','evidence_class']).size().unstack(fill_value=0)
    fig,ax=plt.subplots(figsize=(10,5)); count.plot.bar(stacked=True,ax=ax,colormap='viridis'); ax.set(xlabel='Proposed investigation priority',ylabel='Recommendation count'); ax.tick_params(axis='x',rotation=0); ax.legend(fontsize=8)
    save('18_recommendation_priorities','Rule-based analyst investigations by evidence class','executive_recommendations','Proposed investigations; no actions or benefits observed')
    return saved
