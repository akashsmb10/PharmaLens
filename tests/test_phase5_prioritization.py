import numpy as np
import pandas as pd
import pytest
from src.prioritization import normalize,priority_scores,tier,sensitivity,COMPONENTS
from src.decision_features import validate_weights

@pytest.mark.parametrize('weights',[{'x':.9},{'x':1.1,'y':-.1},{'x':float('nan')},{}])
def test_bad_weights_rejected(weights):
    with pytest.raises(ValueError): validate_weights(weights)

def test_midrank_normalization_and_null():
    result=normalize([10,20,20,40,np.nan])
    np.testing.assert_allclose(result[:4],[0,50,50,100]); assert pd.isna(result.iloc[4])

def test_constant_neutral_normalization():
    assert normalize([0,0,0]).tolist()==[50,50,50] and normalize([8]).tolist()==[50]

def test_minmax_normalization():
    np.testing.assert_allclose(normalize([0,1,10],'minmax'),[0,10,100])

@pytest.mark.parametrize('score,expected',[(70,'High review priority'),(40,'Moderate review priority'),(39.99,'Routine monitoring'),(np.nan,'Insufficient evidence')])
def test_thresholds(score,expected,phase5_cfg): assert tier(score,phase5_cfg)==expected

def test_missing_required_dimension_unscored(phase5_tables,phase5_cfg):
    f=phase5_tables['regional_decision_features'].copy(); f.loc[0,'holdout_MASE']=np.nan
    out=priority_scores(f,phase5_cfg); row=out[out.entity_id.eq(f.entity_id.iloc[0])].iloc[0]
    assert not row.rank_eligible and pd.isna(row['rank']) and pd.isna(row.composite_score) and row.missing_components=='forecast'

def test_zero_weight_does_not_require_missing_dimension(phase5_tables,phase5_cfg):
    f=phase5_tables['regional_decision_features'].copy(); f['holdout_MASE']=np.nan
    weights={k:(0 if k=='forecast' else .25) for k in COMPONENTS}
    out=priority_scores(f,phase5_cfg,weights); assert out.rank_eligible.all() and out.composite_score.notna().all()

def test_equal_scores_share_minimum_rank(phase5_tables,phase5_cfg):
    f=phase5_tables['regional_decision_features'].iloc[:2].copy()
    for c in ['recent_items','item_growth_pct','nic_per_item_change_pct','holdout_MASE','missing_cell_pct','extreme_flags_per_1000_observed_cells']: f[c]=10.
    out=priority_scores(f,phase5_cfg); assert out['rank'].tolist()==[1,1] and out.composite_score.tolist()==[50,50]

def test_score_order_and_component_bounds(phase5_tables):
    for name in ['regional_priority_scores','presentation_priority_scores','region_presentation_priority_scores']:
        f=phase5_tables[name]; assert f.composite_score.dropna().is_monotonic_decreasing
        for c in COMPONENTS: assert f[c+'_score'].dropna().between(0,100).all()

def test_sensitivity_reproducible_and_baseline_identical(phase5_tables,phase5_cfg):
    features={k:phase5_tables[name] for k,name in [('regional','regional_decision_features'),('presentation','presentation_decision_features'),('region_presentation','region_presentation_decision_features')]}
    base={k:phase5_tables[k+'_priority_scores'] for k in features}
    first=sensitivity(features,base,phase5_cfg); second=sensitivity(features,base,phase5_cfg)
    for a,b in zip(first,second): pd.testing.assert_frame_equal(a,b)
    default=first[0].query("scheme == 'default' and normalization == 'percentile'")
    assert default.rank_change.dropna().eq(0).all() and not default.tier_changed.any()
    summary=first[1]; assert summary.spearman_rank_correlation.dropna().between(-1,1).all()
