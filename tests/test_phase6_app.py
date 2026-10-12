import pytest
import pandas as pd
from streamlit.testing.v1 import AppTest
from dashboard.navigation import PAGES
from dashboard.data_loader import load
from dashboard.metrics import totals
from dashboard.formatting import number
from src.common import ROOT

def page(name):
    return AppTest.from_string('from dashboard.pages.'+name+' import render\nrender()',default_timeout=60).run()

def healthy(a):
    assert not a.exception, [x.message for x in a.exception]
    assert not a.error, [x.value for x in a.error]

@pytest.mark.parametrize('name,title',PAGES)
def test_six_pages_render(name,title):
    a=page(name); healthy(a)
    assert a.header[0].value==title
    assert len(a.get('plotly_chart'))>=2
    assert len(a.get('download_button'))>=1
    assert len(a.dataframe)>=1

def test_main_entry_native_navigation_renders():
    a=AppTest.from_file(str(ROOT/'app.py'),default_timeout=60).run(); healthy(a)
    assert a.header[0].value=='Executive Overview' and len(a.metric)==7

def test_executive_partial_window_reconciles_and_has_no_annual_growth():
    a=page('executive')
    start=pd.Timestamp('2025-01-01'); end=pd.Timestamp('2025-06-01')
    a.select_slider(key='exec_period').set_value((start,end)).run(); healthy(a)
    f=load('p2/cost_analytics'); f=f[f.month.between(start,end)]
    assert next(m.value for m in a.metric if m.label=='Prescription items')==number(f.prescription_items.sum(),'count')
    assert next(m.value for m in a.metric if m.label=='Latest annual item growth')=='Unavailable'

def test_regional_filter_and_empty_state():
    a=page('regional'); f=load('p2/cost_analytics'); code=f.region_code.iloc[0]
    a.multiselect(key='region_selection').set_value([code]).run(); healthy(a)
    expected=totals(f[f.region_code.eq(code)&f.month.dt.year.eq(2025)])
    assert next(m.value for m in a.metric if m.label=='Selected-region items')==number(expected['items'],'count')
    a.multiselect(key='region_selection').set_value([]).run(); healthy(a)
    assert not a.metric and any('No observations' in x.value for x in a.info)

def test_presentation_filters_and_year():
    a=page('presentations'); a.selectbox(key='presentation_year').set_value(2024).run(); healthy(a)
    a.multiselect(key='presentation_selection').set_value([]).run(); healthy(a)
    assert not a.metric

def test_forecast_filters_interval_status_and_failures():
    a=page('forecasting'); a.selectbox(key='forecast_horizon').set_value(3).run(); healthy(a)
    assert any('Prediction intervals are unavailable' in x.value for x in a.info)
    assert next(m.value for m in a.metric if m.label=='Paired forecast cells')=='4'
    a.selectbox(key='forecast_level').set_value('regional').run(); healthy(a)
    a.selectbox(key='forecast_stage').set_value('development').run(); healthy(a)
    a.selectbox(key='forecast_level').set_value('region_presentation').run(); healthy(a)
    a.multiselect(key='forecast_models').set_value([]).run(); healthy(a)
    assert not a.metric

def test_unscored_presentations_and_search():
    a=page('decision_intelligence'); a.selectbox(key='decision_level').set_value('presentation').run(); healthy(a)
    assert any('Not scored' in x.value for x in a.info)
    assert any(len(x.value)==13 for x in a.dataframe)
    a.text_input(key='decision_search').set_value('no_matching_investigation_xyz').run(); healthy(a)
    a.multiselect(key='decision_entities').set_value([]).run(); healthy(a)
    assert not a.dataframe

def test_scenario_controls_mix_and_forecast_baseline():
    a=page('scenario_simulator'); baseline=next(m.value for m in a.metric if m.label=='Baseline NIC')
    a.slider(key='scenario_volume').set_value(5.).run(); healthy(a)
    a.slider(key='scenario_cost').set_value(-5.).run(); healthy(a)
    f=load('p2/cost_analytics'); f=f[f.month.dt.year.eq(2025)]; k=totals(f)
    assert next(m.value for m in a.metric if m.label=='Hypothetical NIC')==number(k['nic_gbp']*1.05*.95,'gbp')
    a.number_input(key='mix_transfer').set_value(5.).run(); healthy(a)
    donor_key=f.groupby('presentation_key').prescription_items.sum().idxmin()
    a.selectbox(key='mix_donor').set_value(donor_key).run(); healthy(a)
    a.selectbox(key='scenario_baseline_type').set_value(a.selectbox(key='scenario_baseline_type').options[1]).run(); healthy(a)
    assert len(a.metric)==6 and any('No future actuals' in x.value for x in a.caption)

def test_scenario_region_and_presentation_baselines():
    a=page('scenario_simulator'); f=load('p2/cost_analytics'); f=f[f.month.dt.year.eq(2025)]
    code=f.region_code.iloc[0]; key=f.presentation_key.iloc[0]
    a.selectbox(key='scenario_region').set_value(code).run(); healthy(a)
    a.selectbox(key='scenario_presentation').set_value(key).run(); healthy(a)
    expected=totals(f[f.region_code.eq(code)&f.presentation_key.eq(key)])
    assert next(m.value for m in a.metric if m.label=='Baseline items')==number(expected['items'],'count')
