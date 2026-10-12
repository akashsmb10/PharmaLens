import pandas as pd
import pytest
from src.forecast_config import configuration
from src.forecast_splits import folds

def test_expanding_development_folds():
    c=configuration(); f=folds(pd.date_range('2023-01-01',periods=36,freq='MS'),c,'development')
    assert len(f)==15
    assert f.origin_date.min()==pd.Timestamp('2024-12-01')
    assert f.target_date.max()==pd.Timestamp('2025-06-01')
    assert f.groupby('horizon').size().to_dict()=={1:6,2:5,3:4}
    assert f.train_observations.min()==24

@pytest.mark.parametrize('h',[1,2,3])
def test_horizon_dates(h):
    f=folds(pd.date_range('2023-01-01',periods=36,freq='MS'),configuration(),'holdout')
    for r in f[f.horizon.eq(h)].itertuples(): assert r.target_date==r.origin_date+pd.DateOffset(months=h)

def test_holdout_boundary_no_prefreeze_origins():
    f=folds(pd.date_range('2023-01-01',periods=36,freq='MS'),configuration(),'holdout')
    assert len(f)==15 and f.origin_date.min()==pd.Timestamp('2025-06-01')
    assert f.target_date.min()==pd.Timestamp('2025-07-01')
    assert f.target_date.max()==pd.Timestamp('2025-12-01')

def test_missing_calendar_rejected():
    c=pd.date_range('2023-01-01',periods=36,freq='MS').delete(10)
    with pytest.raises(ValueError): folds(c,configuration(),'development')
