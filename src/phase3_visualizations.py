"""Source-noted Phase 3 figures drawn exclusively from measured tables."""
import textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import ROOT

NOTE='Source: NHSBSA PCA, selected atorvastatin, England, Jan 2023-Dec 2025. Unadjusted; NIC is ingredient cost.'

def charts(tables, populations, root=ROOT):
    out=root/'outputs/phase3/charts'; out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'font.size':10,'axes.titleweight':'bold'})
    files=[]
    def save(fig,name):
        fig.text(.012,.012,NOTE,fontsize=7,color='#555555')
        fig.tight_layout(rect=(0,.055,1,1)); path=out/f'{name}.png'
        fig.savefig(path,dpi=180,facecolor='white',metadata={'Software':'Pharma Phase 3'})
        plt.close(fig); files.append(str(path.relative_to(root)).replace('\\','/'))
    nat=populations['national'][0].sort_values('month')
    for metric,title,label,scale,name in [
        ('prescription_items','National prescription-item trend','Items (millions)',1e6,'01_national_items'),
        ('net_ingredient_cost_gbp','National net ingredient cost trend','NIC (GBP millions)',1e6,'02_national_nic'),
        ('ingredient_cost_per_item_gbp','National weighted NIC per item','NIC/item (GBP)',1,'03_cost_per_item')]:
        fig,ax=plt.subplots(figsize=(11,4.5)); ax.plot(nat.month,nat[metric]/scale,color='#176B87',marker='.',label='Observed')
        ax.plot(nat.month,nat[metric].rolling(3,min_periods=3).mean()/scale,color='#E09F3E',label='Complete 3-month mean')
        ax.set(title=title,ylabel=label,xlabel='Month'); ax.grid(alpha=.2); ax.legend(); save(fig,name)
    reg=populations['regional'][0]
    fig,ax=plt.subplots(figsize=(12,5))
    for name,f in reg.groupby('region_name'):
        f=f.sort_values('month'); ax.plot(f.month,100*f.prescription_items/f.prescription_items.iloc[0],label=name)
    ax.set(title='Regional prescribing activity indexed to January 2023',ylabel='January 2023 = 100',xlabel='Month')
    ax.legend(fontsize=8,ncol=2); save(fig,'04_regional_indexed_growth')
    fig,ax=plt.subplots(figsize=(11,5))
    values=[]; labels=[]
    for name,f in reg.groupby('region_name'):
        values.append(f.items_yoy_growth_pct.dropna()); labels.append(textwrap.fill(name,16))
    ax.boxplot(values,tick_labels=labels,showmeans=True)
    ax.set(title='Regional calendar YoY item-growth distributions (2024-2025)',ylabel='YoY (%)')
    save(fig,'05_regional_growth_distribution')
    pre=populations['presentation'][0]
    contrib=tables['presentation_cost_change_contributions'].sort_values('items_change').tail(10)
    fig,ax=plt.subplots(figsize=(12,6)); ax.barh(contrib.presentation_name,contrib.items_change/1e6,color='#176B87')
    ax.set(title='Presentation contributions to item change: 2025 vs 2024',xlabel='Change in prescription items (millions)')
    save(fig,'06_presentation_item_contributions')
    top=pre.groupby('presentation_name').prescription_items.sum().nlargest(4).index
    matrix=pre[pre.presentation_name.isin(top)].pivot(index='month',columns='presentation_name',values='items_share_pct').sort_index()
    fig,ax=plt.subplots(figsize=(11,5)); matrix.plot.area(ax=ax,stacked=True)
    ax.set(title='Leading presentation item-share evolution',ylabel='Share of all observed items (%)',xlabel='Month',ylim=(0,100))
    ax.legend(fontsize=8,loc='lower left'); save(fig,'07_presentation_mix')
    idx=tables['monthly_seasonal_indices']; idx=idx[idx.metric=='prescription_items']
    fig,ax=plt.subplots(figsize=(11,5))
    for year,f in idx.groupby('calendar_year'):
        ax.plot(f.calendar_month,f.annual_mean_index,marker='.',label=str(year))
    ax.plot(idx.groupby('calendar_month').day_adjusted_index.mean(),linestyle='--',color='black',label='Calendar-day adjusted mean')
    ax.set(title='Month profiles: exploratory evidence from three years',xlabel='Calendar month',ylabel='Within-year mean = 100',xticks=range(1,13))
    ax.legend(); save(fig,'08_monthly_seasonal_profile')
    stl=tables['stl_components']; stl=stl[stl.metric=='prescription_items']
    fig,axes=plt.subplots(4,1,figsize=(11,9),sharex=True)
    for ax,col in zip(axes,['observed','trend','seasonal','residual']):
        ax.plot(stl.month,stl[col]/1e6,color='#176B87'); ax.set_ylabel(f'{col}\n(million items)')
    axes[0].set_title('Robust STL, period 12: displayed component is not proof of stable seasonality')
    save(fig,'09_stl_items')
    ac=tables['autocorrelation_diagnostics']; ac=ac[ac.metric=='prescription_items']
    fig,ax=plt.subplots(figsize=(10,5)); ax.bar(ac.lag-.15,ac.acf,width=.3,label='Raw'); ax.bar(ac.lag+.15,ac.detrended_acf,width=.3,label='Linear detrended')
    ax.set(title='Prescription-item autocorrelation: descriptive, no iid significance bounds',xlabel='Calendar lag (months)',ylabel='ACF',ylim=(-1,1)); ax.legend()
    save(fig,'10_autocorrelation')
    d=tables['cost_decomposition_diagnostics']; d=d[d.comparison=='2025 vs 2024'].iloc[0]
    fields=['item_volume_effect_gbp','presentation_mix_effect_gbp','within_presentation_cost_per_item_effect_gbp']
    values=[d[x]/1e6 for x in fields]; cumulative=0
    fig,ax=plt.subplots(figsize=(11,5))
    for i,v in enumerate(values):
        ax.bar(i,abs(v),bottom=min(cumulative,cumulative+v),color='#218380' if v>=0 else '#D95D39')
        ax.text(i,cumulative+v if v>=0 else cumulative+v/2,f'{v:+.2f}',ha='center',va='bottom' if v>=0 else 'center'); cumulative+=v
    ax.bar(3,cumulative,color='#176B87'); ax.text(3,cumulative/2,f'{cumulative:+.2f}',ha='center',va='center')
    ax.set_xticks(range(4),['Item volume','Presentation mix','Within-presentation\nNIC per item','Observed NIC change'])
    ax.axhline(0,color='black',linewidth=.8); ax.set(title='Exact symmetric NIC decomposition: 2025 vs 2024',ylabel='NIC change (GBP millions)',ylim=(min(0,cumulative)-5,max(0,*np.cumsum(values))+5))
    save(fig,'11_nic_decomposition')
    for stem,label,name in [('presentation_cost_change_contributions','presentation_name','12_presentation_cost_per_item'),('regional_cost_change_contributions','region_name','13_regional_cost_per_item')]:
        f=tables[stem].sort_values('cost_per_item_change_pct')
        fig,ax=plt.subplots(figsize=(12,7)); ax.barh(f[label],f.cost_per_item_change_pct,color=np.where(f.cost_per_item_change_pct<0,'#D95D39','#218380'))
        ax.set(title='Weighted NIC/item change: 2025 vs 2024',xlabel='Change (%)'); save(fig,name)
    anomalies=tables['anomaly_diagnostics']
    counts=anomalies.groupby(['month','classification']).size().unstack(fill_value=0).reindex(nat.month,fill_value=0)
    fig,ax=plt.subplots(figsize=(12,5)); counts.plot(ax=ax,marker='.')
    ax.set(title='Review-flag timeline: method unions, no observations removed',ylabel='Flagged series-metric observations',xlabel='Month'); ax.legend(fontsize=8)
    save(fig,'14_anomaly_timeline')
    ext=tables['extreme_value_review_phase3']; fig,ax=plt.subplots(figsize=(10,5))
    ext.groupby(['metric','classification']).size().unstack(fill_value=0).plot.barh(ax=ax,stacked=True)
    ax.set(title='Original Phase 2 IQR flags: Phase 3 review classifications',xlabel='Retained metric flags'); ax.legend(fontsize=8)
    save(fig,'15_extreme_value_distribution')
    sensitivity=tables['sensitivity_results']; f=sensitivity[(sensitivity.metric=='prescription_items') & sensitivity.analysis.isin(['trend specification','robust trend','extreme exclusion diagnostic only'])].copy()
    fig,ax=plt.subplots(figsize=(12,5)); ax.barh(f.scenario,f.estimate,color='#176B87'); ax.set(title='National item-trend sensitivity',xlabel='Items/month slope')
    save(fig,'16_trend_sensitivity')
    summary=tables['descriptive_statistics']; f=summary[(summary.level=='region_presentation')&(summary.metric=='prescription_items')]
    fig,ax=plt.subplots(figsize=(10,5)); ax.scatter(f.coverage_pct,f.coefficient_of_variation,alpha=.65,color='#176B87')
    ax.set(title='Observed history coverage versus monthly item variability',xlabel='Observed months / 36 (%)',ylabel='Observed-month CV (includes trend)')
    save(fig,'17_coverage_volatility')
    f=tables['forecasting_diagnostics']; f=f[(f.level.isin(['national','regional'])) & (f.metric=='prescription_items')].copy()
    f['label']=f.region_name.fillna('England')
    matrix=f.set_index('label')[['coefficient_of_variation','detrended_cv','acf_lag1','detrended_acf_lag12']]
    fig,ax=plt.subplots(figsize=(11,5)); im=ax.imshow(matrix.values,aspect='auto',cmap='coolwarm',vmin=-1,vmax=1)
    ax.set_yticks(range(len(matrix)),matrix.index); ax.set_xticks(range(4),['Raw CV','Detrended CV','ACF lag 1','Detrended ACF lag 12'])
    for i in range(len(matrix)):
        for j in range(4): ax.text(j,i,f'{matrix.iloc[i,j]:.2f}',ha='center',va='center',fontsize=9)
    fig.colorbar(im,ax=ax,label='Diagnostic value'); ax.set_title('Forecast-readiness diagnostics: no accuracy claim or composite score')
    save(fig,'18_forecasting_readiness')
    return files
