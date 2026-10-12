"""Eighteen forecasting figures. Rolling origins are explicitly identified, never spliced silently."""
import textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from .common import ROOT
from .forecast_selection import selected_rows

NOTE='NHSBSA PCA atorvastatin, England. Items, not patients/revenue. Holdout Jul-Dec 2025; overlapping errors are descriptive.'

def charts(tables,series,cfg,root=ROOT):
    folder=root/'outputs/phase4/charts'; folder.mkdir(parents=True,exist_ok=True); paths=[]
    plt.rcParams.update({'font.family':'DejaVu Sans','axes.spines.top':False,'axes.spines.right':False,'font.size':10,'axes.titleweight':'bold'})
    def save(fig,name):
        fig.text(.012,.01,NOTE,fontsize=7,color='#555555'); fig.tight_layout(rect=(0,.06,1,1))
        path=folder/f'{name}.png'; fig.savefig(path,dpi=180,facecolor='white',metadata={'Software':'Pharma Phase 4'}); plt.close(fig)
        paths.append(str(path.relative_to(root)).replace('\\','/'))
    predictions=tables['backtest_predictions']; decisions=tables['model_selection_decisions']
    selected=selected_rows(predictions,decisions); national=series['England']['values']; hold=predictions[predictions.split_type.eq('holdout')]
    fig,ax=plt.subplots(figsize=(12,5)); ax.plot(national.index,national/1e6,color='#555555',label='Observed items')
    for origin in [pd.Timestamp(cfg['development_end']),pd.Timestamp('2025-09-01')]:
        f=selected[(selected.series_id=='England')&(selected.origin_date==origin)&(selected.split_type=='holdout')].sort_values('horizon')
        ax.plot([origin]+f.target_date.tolist(),[national.loc[origin]/1e6]+(f.prediction/1e6).tolist(),marker='o',linestyle='--',label=f'Single-origin forecast: {origin:%b %Y}')
    ax.axvspan(pd.Timestamp(cfg['final_holdout_start']),national.index[-1],alpha=.1,color='#176B87',label='Final evaluation period')
    ax.set(title='National history and separate fixed-origin forecast paths',ylabel='Items (millions)',xlabel='Month'); ax.legend(fontsize=8)
    save(fig,'01_national_history_origins')
    one=selected[(selected.series_id=='England')&(selected.split_type=='holdout')&(selected.horizon==1)].sort_values('target_date')
    fig,ax=plt.subplots(figsize=(11,5)); ax.plot(one.target_date,one.actual/1e6,marker='o',label='Actual'); ax.plot(one.target_date,one.prediction/1e6,marker='s',label='Frozen selected model; rolling h=1')
    ax.set(title='National holdout: rolling one-month forecasts from different origins',ylabel='Items (millions)',xlabel='Target month'); ax.legend(); save(fig,'02_holdout_actual_prediction')
    fig,ax=plt.subplots(figsize=(12,5)); ax.plot(one.target_date,one.actual/1e6,color='black',linewidth=2,label='Actual')
    for model,f in hold[(hold.series_id=='England')&(hold.horizon==1)].groupby('model'):
        ax.plot(f.target_date,f.prediction/1e6,marker='.',label=model)
    ax.set(title='National model comparison: rolling h=1, different origins',ylabel='Items (millions)',xlabel='Target month'); ax.legend(fontsize=8); save(fig,'03_national_models')
    scores=tables['holdout_model_metrics']; n=scores[scores.aggregation_level=='national'].sort_values('MASE')
    for metric,name,label in [('MAE','04_mae_by_model','Mean absolute error (items)'),('MASE','05_mase_by_model','Mean absolute scaled error')]:
        fig,ax=plt.subplots(figsize=(10,5)); ax.bar(n.model,n[metric],color='#176B87'); ax.set(title=f'National final holdout {metric}: common forecast support',ylabel=label,xlabel='Model'); save(fig,name)
    horizons=tables['horizon_metrics']; f=horizons[(horizons.split_type=='holdout')&(horizons.aggregation_level=='national')]
    fig,ax=plt.subplots(figsize=(10,5))
    for model,g in f.groupby('model'): ax.plot(g.horizon,g.MASE,marker='o',label=model)
    ax.set(title='National final holdout accuracy by horizon',ylabel='MASE',xlabel='Horizon (months)',xticks=[1,2,3]); ax.legend(fontsize=8); save(fig,'06_accuracy_horizon')
    f=tables['regional_forecast_metrics']; f=f[f.split_type=='holdout']
    matrix=f.pivot(index='region_name',columns='model',values='MASE')
    fig,ax=plt.subplots(figsize=(12,6)); matrix.plot.barh(ax=ax); ax.set(title='Regional final holdout MASE: common support within each region',xlabel='MASE',ylabel=''); ax.legend(fontsize=8); save(fig,'07_regional_models')
    regselected=selected[(selected.aggregation_level=='regional')&(selected.split_type=='holdout')].copy()
    regselected['scaled_error']=(regselected.prediction-regselected.actual).abs()/regselected.mase_scale
    matrix=regselected.groupby(['region_name','horizon']).scaled_error.mean().unstack()
    fig,ax=plt.subplots(figsize=(10,6)); im=ax.imshow(matrix.values,aspect='auto',cmap='YlOrRd')
    ax.set_yticks(range(len(matrix)),matrix.index); ax.set_xticks(range(3),[1,2,3]); ax.set(title='Frozen regional model: final holdout error by horizon',xlabel='Horizon (months)')
    for i in range(len(matrix)):
        for j in range(3): ax.text(j,i,f'{matrix.iloc[i,j]:.2f}',ha='center',va='center')
    fig.colorbar(im,ax=ax,label='MASE'); save(fig,'08_regional_error_heatmap')
    fig,ax=plt.subplots(figsize=(10,5)); ax.bar(n.model,n.Bias,color=np.where(n.Bias<0,'#D95D39','#218380')); ax.axhline(0,color='black',lw=.8)
    ax.set(title='National final holdout forecast bias',ylabel='Prediction minus actual (items)'); save(fig,'09_bias_by_model')
    nh=selected[(selected.series_id=='England')&(selected.split_type=='holdout')].copy(); nh['error']=nh.prediction-nh.actual
    fig,ax=plt.subplots(figsize=(10,5)); ax.hist(nh.error/1e3,bins=7,color='#176B87',edgecolor='white'); ax.set(title='National selected-model holdout errors: 15 overlapping forecasts',xlabel='Prediction minus actual (thousand items)',ylabel='Forecast rows'); save(fig,'10_residual_distribution')
    fig,ax=plt.subplots(figsize=(10,5)); ax.boxplot([nh[nh.horizon==h].error.abs()/1e3 for h in [1,2,3]],tick_labels=[1,2,3],showmeans=True)
    ax.set(title='National absolute errors by horizon (n=6, 5, 4)',xlabel='Horizon (months)',ylabel='Absolute error (thousand items)'); save(fig,'11_error_horizon')
    dev=tables['development_model_metrics']; dev=dev[dev.aggregation_level=='national']
    matrix=dev[['model','MASE']].merge(n[['model','MASE']],on='model',suffixes=('_development','_holdout')).set_index('model')
    fig,ax=plt.subplots(figsize=(11,5)); matrix.plot.bar(ax=ax,color=['#176B87','#E09F3E']); ax.set(title='National development versus final holdout (no holdout tuning)',ylabel='MASE',xlabel='Model'); save(fig,'12_development_holdout')
    states=tables['ets_fitted_states']; states=states[states.series_id=='England']
    fig,axes=plt.subplots(2,1,figsize=(12,7),sharex=True)
    axes[0].plot(states.month,states.actual/1e6,label='Actual'); axes[0].plot(states.month,states.fitted/1e6,label='ETS fitted (in-sample)'); axes[0].plot(states.month,states.level/1e6,label='ETS level')
    axes[0].set(title='National damped ETS demonstration refit through Dec 2025',ylabel='Items (millions)'); axes[0].legend(fontsize=8)
    axes[1].plot(states.month,states.trend/1e3,color='#176B87'); axes[1].set(ylabel='ETS trend (thousand items)',xlabel='Month'); save(fig,'13_ets_fitted_trend')
    co=tables['ridge_coefficients']; co=co[co.series_id=='England']
    matrix=co.pivot(index='feature',columns='horizon',values='coefficient_per_standardized_feature')/1e3
    fig,ax=plt.subplots(figsize=(12,6)); matrix.plot.barh(ax=ax); ax.set(title='National frozen-alpha Ridge refit: coefficients, not causal importance',xlabel='Items per one training SD of feature (thousands)',ylabel='Feature'); ax.legend(title='Direct horizon'); save(fig,'14_ridge_coefficients')
    calibration=tables['interval_calibration']; nationalcal=calibration[calibration.series_id=='England']
    fig,ax=plt.subplots(figsize=(10,5)); ax.bar(nationalcal.horizon,nationalcal.calibration_n,color='#176B87'); ax.axhline(cfg['minimum_interval_residuals'],color='#D95D39',linestyle='--',label='Minimum residual count')
    ax.set(title='Interval coverage unavailable: insufficient development residuals',xlabel='Horizon (months)',ylabel='National calibration residual count',xticks=[1,2,3]); ax.legend(); save(fig,'15_interval_support')
    aggregate=tables['aggregate_forecast_comparison']; f=aggregate[(aggregate.split_type=='holdout')&(aggregate.horizon==1)].sort_values('target_date')
    fig,ax=plt.subplots(figsize=(12,5))
    for col,label in [('actual','Actual'),('direct_national','Direct national selected'),('regional_sum','Sum of all seven regional forecasts')]: ax.plot(f.target_date,f[col]/1e6,marker='.',label=label)
    ax.set(title='Direct national versus regional sum: rolling h=1, different origins',ylabel='Items (millions)',xlabel='Target month'); ax.legend(fontsize=8); save(fig,'16_direct_regional_sum')
    counts=decisions.groupby(['aggregation_level','selected_model']).size().unstack(fill_value=0)
    fig,ax=plt.subplots(figsize=(10,5)); counts.plot.barh(ax=ax,stacked=True); ax.set(title='Frozen development-selected models: shared policy by aggregation level',xlabel='Eligible series',ylabel='Aggregation level'); save(fig,'17_selected_models')
    op=tables['operational_forecasts']; op=op[op.series_id=='England'].sort_values('horizon')
    fig,ax=plt.subplots(figsize=(12,5)); last=national.iloc[-12:]
    ax.plot(last.index,last/1e6,color='#555555',label='Historical observations')
    ax.plot([last.index[-1]]+op.forecast_month.tolist(),[last.iloc[-1]/1e6]+(op.point_forecast/1e6).tolist(),marker='o',linestyle='--',color='#176B87',label='Frozen selected model, Dec 2025 origin')
    ax.set(title='Jan-Mar 2026 retrospective as-of-Dec-2025 national forecasts',ylabel='Items (millions)',xlabel='Month'); ax.legend(fontsize=8); save(fig,'18_operational_forecasts')
    return paths
