import numpy as np
import pandas as pd
import pytest
from src.trend_analysis import estimate_trend

def fixture():
    return pd.Series(10+2*np.arange(36),index=pd.date_range('2023-01-01',periods=36,freq='MS'))

def test_exact_linear_coefficients():
    r=estimate_trend(fixture())
    assert r['ols_slope_per_month']==pytest.approx(2)
    assert r['theil_sen_slope_per_month']==2
    assert r['annual_linear_effect']==pytest.approx(24)
    assert r['kendall_tau_descriptive']==pytest.approx(1)

def test_missing_month_elapsed_time_and_withheld_hac():
    s=fixture(); s.iloc[12]=np.nan
    r=estimate_trend(s)
    assert r['ols_slope_per_month']==pytest.approx(2)
    assert r['missing_months']==1 and pd.isna(r['hac_ci_low'])

def test_short_series_skip():
    assert estimate_trend(fixture().iloc[:12])['status'].startswith('skipped')

def test_robust_slope_outlier():
    s=fixture(); s.iloc[18]=10000
    r=estimate_trend(s)
    assert r['theil_sen_slope_per_month']==2
    assert r['ols_slope_per_month']!=pytest.approx(2)

def test_log_linear_effect():
    s=fixture().astype(float); s[:]=np.exp(.02*np.arange(36))
    assert estimate_trend(s)['log_linear_annual_change_pct']==pytest.approx(100*np.expm1(.24))

def test_month_controls_and_chronology():
    a=estimate_trend(fixture(),month_controls=True)
    b=estimate_trend(fixture().iloc[::-1],month_controls=True)
    assert a['ols_slope_per_month']==pytest.approx(2)
    assert a==b
