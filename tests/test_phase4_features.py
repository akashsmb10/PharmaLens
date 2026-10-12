import numpy as np
import pandas as pd
import pytest
from src.forecast_config import configuration
from src.forecast_features import origin_features,supervised_pairs
from src.forecast_models import fit_forecast

def source(): return pd.Series(np.arange(1.,37.),index=pd.date_range('2023-01-01',periods=36,freq='MS'))

def test_lags_and_rolling_mean():
    f=origin_features(source(),10,3,configuration())
    assert f['lag_1']==11 and f['lag_2']==10 and f['lag_3']==9
    assert f['prior_rolling_mean']==10
    assert f['target_month_sin']==pytest.approx(np.sin(2*np.pi*2/12))

@pytest.mark.parametrize('h',[1,2,3])
def test_direct_targets_available_at_training_cutoff(h):
    train=source().iloc[:24]; x,y,p=supervised_pairs(train,h,configuration())
    assert len(y)==24-h-2
    assert p.target_date.max()==train.index[-1]
    for i,r in enumerate(p.itertuples()):
        assert r.target_date==r.feature_origin+pd.DateOffset(months=h)
        assert y[i]==train.loc[r.target_date]

def test_features_ignore_future_values():
    a=source(); b=a.copy(); b.iloc[15:]=999999
    assert origin_features(a,14,3,configuration())==origin_features(b,14,3,configuration())

def test_training_only_scaler_mean():
    train=source().iloc[:24]; cfg=configuration(); x,_,_=supervised_pairs(train,3,cfg)
    _,_,metadata,_=fit_forecast(train,[3],{'model':'ridge','variant':'ridge_alpha_1','alpha':1},cfg)
    np.testing.assert_allclose(metadata['horizons'][0]['scaler_mean'],x.mean().values)
    assert metadata['horizons'][0]['supervised_rows']==19
