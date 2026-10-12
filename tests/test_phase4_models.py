import numpy as np
import pandas as pd
import pytest
from src.forecast_config import configuration
from src.forecast_models import fit_forecast

def source(n=24): return pd.Series(np.arange(1.,n+1.),index=pd.date_range('2023-01-01',periods=n,freq='MS'))
def predict(model,s=None,cfg=None):
    return fit_forecast(source() if s is None else s,[1,2,3],{'model':model,'variant':model,'alpha':1},configuration() if cfg is None else cfg)

def test_naive_definition(): np.testing.assert_equal(predict('naive')[1],[24,24,24])
def test_seasonal_month_alignment(): np.testing.assert_equal(predict('seasonal_naive')[1],[13,14,15])
def test_drift_definition(): np.testing.assert_equal(predict('drift')[1],[25,26,27])

def test_drift_negative_constraints_record_raw():
    s=source(); s[:]=np.linspace(24,1,24)
    raw,final,_,_=predict('drift',s)
    np.testing.assert_allclose(raw,[0,-1,-2]); np.testing.assert_allclose(final,[0,0,0])
    np.testing.assert_allclose(predict('drift',s,{**configuration(),'nonnegative':False})[1],raw)

def test_zero_values_valid_naive(): np.testing.assert_equal(predict('naive',source()*0)[1],[0,0,0])

def test_ets_minimum_history():
    with pytest.raises(ValueError,match='minimum'): predict('damped_ets',source(12))

def test_ets_real_fit_metadata():
    raw,_,p,a=predict('damped_ets')
    assert np.isfinite(raw).all() and p['optimization_success']
    assert p['damped'] and p['seasonal'] is None and len(a['ets_fitted'])==24

def test_ets_convergence_failure(monkeypatch):
    import src.forecast_models as module
    class Failed:
        mle_retvals={'success':False,'message':'test nonconvergence'}
    class Fake:
        def __init__(self,*args,**kwargs): pass
        def fit(self,**kwargs): return Failed()
    monkeypatch.setattr(module,'ExponentialSmoothing',Fake)
    with pytest.raises(RuntimeError,match='optimization failed'): predict('damped_ets')

def test_no_gap_imputation():
    s=source(); s.iloc[10]=np.nan
    with pytest.raises(ValueError,match='gaps'): predict('naive',s)

def test_seasonal_short_unavailable():
    with pytest.raises(ValueError,match='unavailable'): predict('seasonal_naive',source(6))

def test_ridge_short_effective_rows():
    with pytest.raises(ValueError,match='effective'): predict('ridge',source(12))
