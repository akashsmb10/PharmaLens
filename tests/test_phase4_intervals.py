import numpy as np
import pandas as pd
import pytest
from src.forecast_intervals import calibrate,add_intervals,coverage
from src.forecast_config import configuration

def frame(): return pd.DataFrame({'series_id':['X']*6,'horizon':[1]*6,'actual':[10.]*6,'prediction':[9.]*6,'aggregation_level':['national']*6,'split_type':['development']*6})

def test_short_calibration_null_bounds():
    f=frame(); c=calibrate(f,configuration()); out=add_intervals(f,c)
    assert out.lower_80.isna().all() and c.calibration_n.iloc[0]==6
    assert coverage(out).interval_rows.eq(0).all()

def test_interval_order_and_nonnegative():
    f=frame(); cfg={**configuration(),'minimum_interval_residuals':5}
    out=add_intervals(f,calibrate(f,cfg))
    assert (out.lower_95<=out.lower_80).all() and (out.upper_80<=out.upper_95).all()
    assert (out.lower_80<=out.prediction).all() and (out.prediction<=out.upper_80).all()
    assert out.lower_95.ge(0).all()

def test_interval_coverage_known():
    f=frame().iloc[:2].copy(); f['lower_80']=[9.,11.]; f['upper_80']=[11.,12.]; f['lower_95']=f.lower_80; f['upper_95']=f.upper_80
    out=coverage(f)
    assert out.empirical_coverage_pct.eq(50).all() and out.interval_rows.eq(2).all()

def test_calibration_cannot_use_holdout():
    f=frame(); f['split_type']='holdout'
    with pytest.raises(ValueError,match='Holdout'): calibrate(f,configuration())
