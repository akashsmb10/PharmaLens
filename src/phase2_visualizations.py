"""Descriptive figures from executed reporting Parquet; no models or population adjustments."""
import textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
from .common import ROOT

SOURCE_NOTE = 'Source: NHSBSA PCA monthly; selected atorvastatin, England community dispensing, Jan 2023–Dec 2025. Unadjusted.'

def charts(root=ROOT):
    out = root / 'outputs/charts/phase2'
    out.mkdir(parents=True,exist_ok=True)
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','font.size':10})
    def read(name):
        return pd.read_parquet(root / f'outputs/tables/{name}.parquet')
    created = []
    def save(fig,name):
        fig.text(.01,.012,SOURCE_NOTE,fontsize=7,color='#555555')
        fig.tight_layout(rect=(0,.055,1,1))
        path = out / f'{name}.png'
        fig.savefig(path,dpi=160,facecolor='white')
        plt.close(fig)
        created.append(str(path.relative_to(root)).replace('\\','/'))
    def trend(frame,col,title,ylabel,name,scale=1):
        fig,ax=plt.subplots(figsize=(11,4.5))
        ax.plot(frame.month,frame[col]/scale,color='#176B87',marker='.',linewidth=2)
        ax.set(title=title,ylabel=ylabel,xlabel='Month')
        ax.grid(axis='y',alpha=.2)
        save(fig,name)
    nat = read('national_monthly_trends').sort_values('month')
    trend(nat,'prescription_items','Monthly atorvastatin prescription-item activity','Prescription items (millions)','01_monthly_items',1e6)
    trend(nat,'net_ingredient_cost_gbp','Monthly atorvastatin net ingredient cost','Net ingredient cost (£ millions)','02_monthly_ingredient_cost',1e6)
    reg = read('regional_performance')
    for col,title,ylabel,name in [('prescription_items','Regional prescription-item distribution','Prescription items (millions)','03_region_items'),
                                   ('net_ingredient_cost_gbp','Regional net ingredient cost distribution','Net ingredient cost (£ millions)','04_region_cost')]:
        ranked=reg.sort_values(col)
        fig,ax=plt.subplots(figsize=(10,5))
        ax.barh(ranked.region_name,ranked[col]/1e6,color='#176B87')
        ax.set(title=title,xlabel=ylabel)
        ax.grid(axis='x',alpha=.2)
        save(fig,name)
    pre=read('presentation_performance')
    for col,title,label,name in [('prescription_items','Top 10 presentations by prescription items','Prescription items (millions)','05_top_presentation_items'),
                                 ('net_ingredient_cost_gbp','Top 10 presentations by net ingredient cost','Net ingredient cost (£ millions)','06_top_presentation_cost')]:
        top=pre.nlargest(10,col).sort_values(col)
        fig,ax=plt.subplots(figsize=(12,6))
        ax.barh(top.presentation_name,top[col]/1e6,color='#218380')
        ax.set(title=title,xlabel=label)
        save(fig,name)
    annual=read('regional_annual_trends')
    growth=annual.pivot(index='region_name',columns='calendar_year',values='items_annual_growth_pct').dropna(axis=1,how='all')
    fig,ax=plt.subplots(figsize=(11,5))
    growth.plot.barh(ax=ax,color=['#176B87','#E09F3E'])
    ax.set(title='Regional annual prescription-item growth (complete calendar years)',xlabel='Growth (%)',ylabel='')
    ax.legend(title='Calendar year')
    save(fig,'07_regional_yoy_growth')
    pareto=read('presentation_concentration').sort_values('pareto_position')
    fig,ax=plt.subplots(figsize=(14,7))
    ax.bar(pareto.pareto_position,pareto.items_share_pct,color='#176B87')
    right=ax.twinx()
    right.plot(pareto.pareto_position,pareto.cumulative_items_share_pct,color='#D95D39',marker='.')
    right.set_ylabel('Cumulative item share (%)')
    right.set_ylim(0,105)
    ax.set_xticks(pareto.pareto_position, [textwrap.fill(x,25) for x in pareto.presentation_name],rotation=90,fontsize=8)
    ax.set(title='Presentation concentration: observed prescription items',ylabel='Item share (%)',xlabel='Presentation, ranked by observed items')
    save(fig,'08_presentation_pareto')
    trend(nat,'ingredient_cost_per_item_gbp','Weighted ingredient cost per prescription item','Ingredient cost per item (£)','09_cost_per_item')
    def heatmap(frame,value,title,colorbar,name):
        matrix=frame.pivot(index='region_name',columns='presentation_name',values=value)
        fig,ax=plt.subplots(figsize=(15,7))
        im=ax.imshow(np.ma.masked_invalid(matrix.to_numpy(dtype=float)),aspect='auto',cmap='viridis')
        ax.set_yticks(range(len(matrix)),matrix.index)
        ax.set_xticks(range(len(matrix.columns)),[textwrap.fill(x,25) for x in matrix.columns],rotation=90,fontsize=8)
        ax.set_title(title)
        fig.colorbar(im,ax=ax,label=colorbar,shrink=.65)
        save(fig,name)
    mix=read('region_presentation_mix')
    mix['log10_items']=np.log10(mix.prescription_items.where(mix.prescription_items>0))
    heatmap(mix,'log10_items','Region × presentation activity (blank cells = not observed)','log10(prescription items)','10_activity_heatmap')
    heatmap(read('series_coverage'),'full_window_coverage_pct','Region × presentation monthly coverage','Observed fraction of 36 months (%)','11_series_coverage')
    extremes=read('extreme_value_review')
    focus=extremes.groupby(['region_code','presentation_key']).size().idxmax()
    flagged=extremes[(extremes.region_code==focus[0])&(extremes.presentation_key==focus[1])]
    cost=read('cost_analytics')
    selected=cost[(cost.region_code==focus[0])&(cost.presentation_key==focus[1])].sort_values('month')
    selected_label = selected.iloc[0]
    selected = selected.set_index('month').reindex(pd.DatetimeIndex(nat.month)).rename_axis('month').reset_index()
    fig,axes=plt.subplots(3,1,figsize=(11,8),sharex=True)
    for ax,(metric,col,label) in zip(axes,[('items','prescription_items','Items'),('nic_gbp','net_ingredient_cost_gbp','NIC (£)'),('total_quantity','total_quantity',f'Quantity ({selected_label.unit_of_measure})')]):
        ax.plot(selected.month,selected[col],color='#176B87',marker='.',label='Original observed values')
        hit=flagged[flagged.metric==metric]
        ax.scatter(hit.month,hit.value,color='#D95D39',marker='x',s=45,label='Three-IQR review flag')
        ax.set_ylabel(label)
    axes[0].set_title(f"Extreme-value review: {selected_label.presentation_name} — {selected_label.region_name}")
    axes[0].legend(fontsize=8)
    axes[-1].set_xlabel('Month; gaps are not filled')
    save(fig,'12_extreme_value_review')
    fig,ax=plt.subplots(figsize=(10,6))
    ax.scatter(reg.items_share_pct,reg.first_to_last_annual_items_growth_pct,s=reg.items_share_pct*15,color='#176B87',alpha=.75)
    for _,r in reg.iterrows():
        ax.annotate(r.region_name,(r.items_share_pct,r.first_to_last_annual_items_growth_pct),xytext=(4,4),textcoords='offset points',fontsize=8)
    ax.set(title='Regional activity size versus annual growth',xlabel='Share of observed 2023–2025 items (%)',ylabel='2025 versus 2023 annual items growth (%)')
    save(fig,'13_regional_growth_vs_size')
    return created

if __name__=='__main__':
    print('\n'.join(charts()))
