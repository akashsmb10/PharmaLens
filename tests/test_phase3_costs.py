import numpy as np
import pandas as pd
import pytest
from src.cost_diagnostics import shapley_cost,annual_contributions

def test_pure_volume_change():
    r=shapley_cost(100,[.6,.4],[2,5],120,[.6,.4],[2,5])
    assert r['item_volume_effect_gbp']==pytest.approx(64)
    assert r['presentation_mix_effect_gbp']==0
    assert r['within_presentation_cost_per_item_effect_gbp']==0

def test_pure_mix_change():
    r=shapley_cost(100,[.6,.4],[2,5],100,[.5,.5],[2,5])
    assert r['presentation_mix_effect_gbp']==pytest.approx(30)
    assert r['item_volume_effect_gbp']==0

def test_pure_cost_per_item_change():
    r=shapley_cost(100,[.6,.4],[2,5],100,[.6,.4],[1,4])
    assert r['within_presentation_cost_per_item_effect_gbp']==pytest.approx(-100)
    assert abs(r['reconciliation_residual_gbp'])<1e-10

def test_mixed_change_reconciles_and_reverses():
    a=shapley_cost(100,[.6,.4],[2,5],120,[.5,.5],[1,4])
    b=shapley_cost(120,[.5,.5],[1,4],100,[.6,.4],[2,5])
    assert a['observed_cost_change_gbp']==pytest.approx(-20)
    for k in a: assert a[k]==pytest.approx(-b[k],abs=1e-10)

def test_invalid_share_or_unidentified_cost_rejected():
    with pytest.raises(ValueError): shapley_cost(100,[.3,.4],[2,5],120,[.5,.5],[1,4])
    with pytest.raises(ValueError): shapley_cost(100,[.6,.4],[2,np.nan],120,[.5,.5],[1,4])

def test_weighted_annual_ratio():
    f=pd.DataFrame({'month':pd.to_datetime(['2024-01-01','2024-02-01','2025-01-01','2025-02-01']),
                    'key':['X']*4,'prescription_items':[1,9,2,8],'net_ingredient_cost_gbp':[10,9,20,8]})
    c=annual_contributions(f,['key'])
    assert c.cost_per_item_baseline.iloc[0]==pytest.approx(1.9)
    assert c.cost_per_item_current.iloc[0]==pytest.approx(2.8)
    assert c.nic_change_gbp.iloc[0]==9
