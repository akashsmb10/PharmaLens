import numpy as np
import pandas as pd
import pytest
from src.forecast_backtesting import backtest,training_policy
from src.forecast_models import variants
from src.forecast_config import configuration
from src.forecast_splits import folds
from src.forecast_selection import common_support,select_models

def source():
    s=pd.Series(100+np.arange(36)*2.,index=pd.date_range('2023-01-01',periods=36,freq='MS'))
    return {'x':{'values':s,'metadata':{'aggregation_level':'national'}}}

@pytest.mark.parametrize('model',['naive','seasonal_naive','drift','damped_ets','ridge'])
def test_adversarial_future_values_do_not_change_origin_forecast(model):
    a=source(); b=source(); b['x']['values'].iloc[24:]=999999
    cfg=configuration(); all_folds=folds(a['x']['values'].index,cfg,'development'); fold=all_folds[all_folds.origin_date.eq(pd.Timestamp('2024-12-01'))]
    setting=[v for v in variants(cfg) if v['model']==model][:1]
    x=backtest(a,fold,setting,cfg); y=backtest(b,fold,setting,cfg)
    np.testing.assert_allclose(x.prediction,y.prediction)
    assert not np.array_equal(x.actual,y.actual)
    assert x.model_status.eq('ok').all()

def test_failures_logged_no_substitution():
    cfg={**configuration(),'ets_minimum_months':100}
    s=source(); f=folds(s['x']['values'].index,cfg,'development')
    out=backtest(s,f,[{'model':'damped_ets','variant':'damped_ets','alpha':None}],cfg)
    assert out.prediction.isna().all() and out.model_status.eq('failed').all()
    assert out.failure_reason.str.contains('minimum').all()

def test_common_support_drops_failed_row_for_every_model():
    cfg=configuration(); s=source(); out=backtest(s,folds(s['x']['values'].index,cfg,'development'),variants(cfg)[:2],cfg)
    out.loc[out.index[0],'model_status']='failed'; out.loc[out.index[0],'prediction']=np.nan
    common=common_support(out)
    assert len(common)==len(out)-2

def test_selection_rejects_holdout():
    s=source(); cfg=configuration(); out=backtest(s,folds(s['x']['values'].index,cfg,'holdout'),variants(cfg)[:1],cfg)
    with pytest.raises(ValueError,match='development'): select_models(out,cfg,pd.DataFrame())

def test_selection_unchanged_when_holdout_values_change():
    a=source(); b=source(); b['x']['values'].iloc[30:]=999999
    cfg=configuration(); f=folds(a['x']['values'].index,cfg,'development')
    x=backtest(a,f,variants(cfg),cfg); y=backtest(b,f,variants(cfg),cfg)
    eligibility=pd.DataFrame([{'series_id':'x','aggregation_level':'national','eligible':True}])
    pd.testing.assert_frame_equal(select_models(x,cfg,eligibility),select_models(y,cfg,eligibility))

def test_training_anomaly_policy_immutable():
    s=source()['x']['values']; before=s.copy(); s.iloc[12]=10000; before=s.copy()
    altered,n=training_policy(s,configuration(),'training_mad_clip')
    pd.testing.assert_series_equal(s,before)
    assert n==1 and altered.iloc[12]<10000
