import pandas as pd
import pytest
from src.forecast_risk import classify_error

@pytest.mark.parametrize('n,p,expected',[(15,.1,'Lower observed error'),(15,.5,'Moderate observed error'),(15,.9,'Higher observed error'),(5,.1,'Insufficient evaluation evidence')])
def test_error_classes(n,p,expected,phase5_cfg): assert classify_error(.8,n,p,phase5_cfg)==expected

def test_horizon_support_and_missing_counts(phase5_tables):
    f=phase5_tables['forecast_horizon_risk']
    assert not f.duplicated(['series_id','split_type','horizon']).any()
    assert f.expected_forecasts.eq(f.horizon.map({1:6,2:5,3:4})).all()
    assert f.n.add(f.missing_forecasts).eq(f.expected_forecasts).all()

def test_intervals_unavailable_and_not_mae_bands(phase5_tables):
    f=phase5_tables['forecast_dashboard']
    for col in ['lower_80','upper_80','lower_95','upper_95']: assert f[col].isna().all()
    assert f.interval_status.str.startswith('unavailable').all()

def test_hierarchy_gap_arithmetic(phase5_tables):
    f=phase5_tables['forecast_hierarchy_gap_analysis']
    for r in f.itertuples():
        expected=r.regional_sum_forecast-r.direct_forecast
        assert r.signed_gap_items==pytest.approx(expected)
        assert r.absolute_gap_pct==pytest.approx(100*abs(expected)/r.direct_forecast)

def test_frozen_models_and_paired_baseline(phase5_tables,phase5_inputs):
    p=phase5_tables['forecast_reliability_profiles'].set_index('series_id'); s=phase5_inputs['p4/model_selection_decisions'].set_index('series_id')
    assert p.selected_variant.to_dict()==s.selected_variant.to_dict()
    assert p.paired_n.eq(15).all() and p.selected_failure_count.eq(0).all()
    assert p.all_family_failure_count.sum()==len(phase5_inputs['p4/model_failures'])
