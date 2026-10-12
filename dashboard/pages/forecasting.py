import streamlit as st
from dashboard.data_loader import load
from dashboard.filters import apply
from dashboard.metrics import comparisons,history_for_series
from dashboard.components import cards,plot,table,empty,context
from dashboard.chart_factory import forecast_points,actual_predicted,bars,trend
from dashboard.evidence import explain,methodology

def render():
    st.header('Forecasting & Model Evaluation')
    decisions=load('p4/model_selection_decisions'); levels=sorted(decisions.aggregation_level.unique())
    level=st.selectbox('Aggregation level',levels,index=levels.index('national'),key='forecast_level')
    options=decisions[decisions.aggregation_level.eq(level)].series_id.tolist()
    profiles=load('p5/forecast_risk_dashboard')
    labels={r.series_id:('England' if r.aggregation_level=='national' else r.region_name if r.aggregation_level=='regional' else r.region_name+' · '+r.presentation_name) for r in profiles.itertuples()}
    sid=st.selectbox('Forecast series',options,format_func=labels.get,key='forecast_series')
    choice=decisions[decisions.series_id.eq(sid)].iloc[0]
    stage=st.selectbox('Evaluation stage',['holdout','development'],format_func=lambda x:'Final holdout · Jul–Dec 2025' if x=='holdout' else 'Development · Jan–Jun 2025',key='forecast_stage')
    horizon=st.selectbox('Forecast horizon (months)',[1,2,3],key='forecast_horizon')
    families=load('p4/frozen_family_configurations'); variants=families[families.aggregation_level.eq(level)].variant.tolist()
    selected=st.multiselect('Models shown',variants,default=[choice.selected_variant],key='forecast_models')
    context(f'{sid}; {stage}; horizon {horizon} months; models '+', '.join(selected))
    st.success('Frozen operational selection: '+choice.selected_variant+' · selected using development evidence only.')
    st.info('Prediction intervals are unavailable because the development calibration sample was insufficient.')
    back=load('p4/backtest_predictions'); f=back[back.series_id.eq(sid)]
    same=apply(f,horizon=horizon,stage=stage)
    comparison,paired=comparisons(same,variants)
    visible=apply(same,models=selected)
    if empty(visible): return
    metric=comparison[comparison.variant.eq(choice.selected_variant)]
    st.caption('Selected-model cards retain the frozen operational choice. Comparison charts/tables follow Models shown; common support includes all five frozen families before display filtering.')
    if len(metric):
        r=metric.iloc[0]; cards([('Selected-model MASE',r.MASE,'ratio'),('Selected-model MAE',r.MAE,'count'),('Selected-model RMSE',r.RMSE,'count'),('Selected-model WAPE',r.WAPE,'percent'),('Selected-model signed bias',r.Bias,'count'),('Paired forecast cells',r.n,'count')])
    else:
        st.info('Selected-model metrics are unavailable: no common successful forecast support for this scope.')
    history=history_for_series(load('p2/cost_analytics'),choice)
    plot(forecast_points(history,visible,'Observed history and origin-labelled prediction points'),'forecast_predictions')
    st.caption('Prediction points are not joined across different origins. Hover shows origin, target, true horizon and failure status.')
    plot(actual_predicted(visible,stage.title()+' actual versus predicted · selected horizon'),'forecast_actual_predicted')
    shown=comparison[comparison.variant.isin(selected)]
    plot(bars(shown,'variant','MASE','Model comparison on common successful forecast cells','MASE'),'forecast_comparison')
    plot(bars(shown,'variant','Bias','Mean prediction minus actual','Prescription items'),'forecast_bias')
    table(shown,'filtered forecast comparisons','forecast_comparison_table')
    columns=['series_id','variant','origin_date','target_date','horizon','split_type','actual','prediction','model_status','failure_reason']
    table(visible[columns],'origin-specific forecast rows','forecast_rows')
    failures=visible[visible.model_status.ne('ok')]
    if len(failures): st.warning(f'{len(failures)} displayed forecast rows failed. Missing predictions are not substituted.')
    with st.expander('Horizon, regional accuracy and hierarchy diagnostics',expanded=False):
        hr=load('p5/forecast_horizon_risk'); hr=hr[hr.series_id.eq(sid)&hr.split_type.eq(stage)]
        plot(bars(hr,'horizon','MASE','Frozen selected model by horizon · differing target support','MASE'),'forecast_horizons')
        risk=load('p5/forecast_risk_dashboard'); reg=risk[risk.aggregation_level.eq('regional')]
        plot(bars(reg,'region_name','holdout_MASE','Selected regional models · fixed final holdout','MASE'),'forecast_regions')
        gaps=load('p5/forecast_hierarchy_gap_analysis'); gaps=gaps[gaps.context.eq(stage)&gaps.horizon.eq(horizon)]
        plot(bars(gaps,'forecast_month','signed_gap_items','National-system sum seven regions minus direct national','Prescription items'),'forecast_gaps')
        st.caption('Regional and hierarchy panels use their explicitly stated system-level scope; they are not forecasts of the selected presentation subset.')
    st.subheader('As-of December 2025 retrospective forecasts')
    op=load('p5/forecast_dashboard'); op=op[op.series_id.eq(sid)]
    plot(trend(op,'forecast_month','point_forecast','Three forecasts issued from one December 2025 observation cutoff',unit='Prescription items'),'forecast_operational')
    table(op,'selected retrospective forecasts','forecast_operational_table')
    st.caption('These are historical as-of forecasts, not current forecasts. No 2026 actuals are used. Publication timing and revisions are not reconstructed.')
    explain('Frozen Phase 4 predictions, selections and family configurations; Phase 5 forecast_dashboard',f'{stage}, selected horizon {horizon}; retrospective forecast cutoff Dec 2025',
        'Metrics computed from successful paired origin/horizon cells. MASE uses each origin’s training-only naive scale. Bias=prediction−actual. Display filtering never changes model selection.',
        'Validated historical model result','Short overlapping evaluation; unavailable intervals; missing failed forecasts remain null.')
    methodology(['PHASE4_MODEL_CARD.md','PHASE4_MODEL_COMPARISON.md'])
