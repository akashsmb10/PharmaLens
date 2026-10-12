import numpy as np
import pandas as pd
import pytest
from src.seasonality_analysis import seasonal_indices,seasonality

def fixture():
    return pd.Series(np.tile(np.arange(1,13,dtype=float),3),index=pd.date_range('2023-01-01',periods=36,freq='MS'))

def test_index_normalization():
    f=seasonal_indices(fixture())
    assert f.annual_mean_index.iloc[0]==pytest.approx(100/6.5)
    np.testing.assert_allclose(f.groupby('calendar_year').annual_mean_index.mean(),100)
    np.testing.assert_allclose(f.groupby('calendar_year').day_adjusted_index.mean(),100)

def test_acf_ordering():
    a=seasonality(fixture()); b=seasonality(fixture().iloc[::-1])
    pd.testing.assert_frame_equal(a[2],b[2]); pd.testing.assert_frame_equal(a[3],b[3])
    assert a[2].acf.iloc[0]==pytest.approx(1)
    assert a[2].acf.iloc[12]==pytest.approx(2/3)

def test_stl_identity():
    components=seasonality(fixture())[3]
    np.testing.assert_allclose(components.observed,components.trend+components.seasonal+components.residual)

def test_gap_no_acf_compression():
    s=fixture(); s.iloc[10]=np.nan
    result=seasonality(s)
    assert result[2].empty and result[3].empty and 'skipped' in result[0]['status']

def test_short_series_no_stl():
    assert seasonality(fixture().iloc[:12])[3].empty
