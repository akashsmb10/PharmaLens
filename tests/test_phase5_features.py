import numpy as np
import pandas as pd
import pytest
from src.decision_features import join_unique,historical_features,coverage_grid

@pytest.mark.parametrize('name,n',[('regional_decision_features',7),('presentation_decision_features',17),('region_presentation_decision_features',119),('national_decision_summary',1)])
def test_feature_grains(phase5_tables,name,n):
    f=phase5_tables[name]; assert len(f)==n and f.entity_id.is_unique

def test_join_rejects_multiplication():
    with pytest.raises(ValueError): join_unique(pd.DataFrame({'id':[1,2]}),pd.DataFrame({'id':[1,1],'x':[2,3]}),['id'])

def test_left_join_preserves_missing():
    f=join_unique(pd.DataFrame({'id':[1,2]}),pd.DataFrame({'id':[1],'forecast':[100.]}),['id'])
    assert len(f)==2 and pd.isna(f.forecast.iloc[1])

def test_region_and_presentation_totals(phase5_tables,phase5_inputs):
    fact=phase5_inputs['p2/cost_analytics']
    for name in ['regional_decision_features','presentation_decision_features']:
        f=phase5_tables[name]; assert f.historical_items.sum()==fact.prescription_items.sum()
        assert f.historical_nic_gbp.sum()==pytest.approx(fact.net_ingredient_cost_gbp.sum(),abs=.01)
        assert f.historical_item_share_pct.sum()==pytest.approx(100)

def test_weighted_cost_ratio(phase5_tables):
    f=phase5_tables['regional_decision_features']
    np.testing.assert_allclose(f.recent_nic_per_item_gbp,f.recent_nic_gbp/f.recent_items)

def test_grid_union_is_complete(phase5_inputs):
    grid=coverage_grid(phase5_inputs)
    assert len(grid)==36*7*17 and grid.is_observed.sum()==len(phase5_inputs['p2/cost_analytics'])
    assert (~grid.is_observed).sum()==len(phase5_inputs['p2/missing_series_months'])

def test_forecast_joins_match_selected_series(phase5_tables):
    p=phase5_tables['forecast_reliability_profiles'].set_index('series_id')
    for name in ['regional_decision_features','region_presentation_decision_features','national_decision_summary']:
        for r in phase5_tables[name].itertuples():
            if r.forecast_eligible: assert r.holdout_MASE==p.loc[r.entity_id,'holdout_MASE']
            else: assert pd.isna(r.holdout_MASE)

def test_future_history_not_used(phase5_inputs,phase5_cfg):
    original=historical_features(phase5_inputs,phase5_cfg)
    altered={k:v.copy() for k,v in phase5_inputs.items()}
    extra=altered['p2/cost_analytics'].iloc[:1].copy(); extra['month']=pd.Timestamp('2026-01-01'); extra['prescription_items']=1e12
    altered['p2/cost_analytics']=pd.concat([altered['p2/cost_analytics'],extra],ignore_index=True)
    other=historical_features(altered,phase5_cfg)
    for key in original: pd.testing.assert_frame_equal(original[key],other[key])

def test_partial_annual_comparison_is_not_zero(phase5_tables):
    f=phase5_tables['region_presentation_decision_features']
    assert f.item_growth_pct.isna().any()
    assert f.loc[~f.forecast_eligible,'retrospective_jan_mar_2026_items'].isna().all()
