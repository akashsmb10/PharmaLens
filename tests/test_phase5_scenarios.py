import json
import numpy as np
import pandas as pd
import pytest
from src.scenario_engine import accounting,break_even,mix_simulation,scenarios

@pytest.mark.parametrize('v,c,expected',[(0,0,200),(10,0,220),(0,-10,180),(10,-10,198),(-10,10,198)])
def test_accounting_known_fixture(v,c,expected):
    items,unit,nic=accounting(100,2,v,c); assert nic==pytest.approx(expected) and nic==pytest.approx(items*unit)

@pytest.mark.parametrize('args',[(-1,2,0,0),(1,-2,0,0),(100,2,-100,0),(100,2,0,-101),(np.nan,2,0,0)])
def test_invalid_accounting(args):
    with pytest.raises(ValueError): accounting(*args)

@pytest.mark.parametrize('volume',[-10,-5,0,5,10,50])
def test_break_even_equality(volume):
    offset=break_even(volume); assert (1+volume/100)*(1+offset/100)==pytest.approx(1)
    if volume==5: assert offset==pytest.approx(-100/21)

def product_fixture():
    return pd.DataFrame({'presentation_key':['A|tablet','B|ml'],'presentation_name':['A','B'],
                         'recent_items':[80.,20.],'recent_nic_per_item_gbp':[2.,5.]})

def test_mix_conservation_and_independent_accounting():
    out=mix_simulation(product_fixture(),100,'A|tablet','B|ml',10)
    assert out.scenario_share.tolist()==pytest.approx([.7,.3])
    assert out.hypothetical_items.sum()==pytest.approx(100) and out.hypothetical_nic_gbp.sum()==pytest.approx(290)

@pytest.mark.parametrize('transfer',[81,-1,np.nan])
def test_infeasible_mix_rejected(transfer):
    with pytest.raises(ValueError): mix_simulation(product_fixture(),100,'A|tablet','B|ml',transfer)

def test_unknown_mix_key_rejected():
    with pytest.raises(ValueError): mix_simulation(product_fixture(),100,'UNKNOWN','B|ml',1)

def test_scenarios_have_matching_baselines_and_no_probabilities(phase5_tables,phase5_cfg):
    f=phase5_tables['scenario_results']; op=f[f.baseline_type.eq('Model forecast baseline')]
    assert op.baseline_end_date.le(op.forecast_as_of).all()
    assert op.forecast_as_of.eq(pd.Timestamp(phase5_cfg['forecast_as_of'])).all()
    assert f.hypothetical_items.ge(0).all()
    assert phase5_tables['scenario_assumptions'].probability.isna().all()
    assert f[f.scenario_name.str.startswith('D:')].hypothetical_items.nunique()==1

def test_forecast_scenario_reference_exactly_frozen(phase5_tables,phase5_inputs):
    original=phase5_inputs['p4/operational_forecasts']; original=original[original.series_id.eq('England')].set_index('forecast_month')
    for r in phase5_tables['scenario_results'].query("baseline_type == 'Model forecast baseline'").itertuples():
        assert r.reference_items==original.loc[pd.Timestamp(r.baseline_period),'point_forecast']

def test_future_actual_does_not_affect_planning_scenarios(phase5_tables,phase5_inputs,phase5_cfg):
    features={k:phase5_tables[name] for k,name in [('regional','regional_decision_features'),('presentation','presentation_decision_features'),('national','national_decision_summary')]}
    base=scenarios(features,phase5_inputs,phase5_cfg)
    altered={k:v.copy() for k,v in phase5_inputs.items()}
    extra=altered['p2/national_monthly_trends'].iloc[:1].copy(); extra['month']=pd.Timestamp('2026-01-01'); extra['net_ingredient_cost_gbp']=1e12
    altered['p2/national_monthly_trends']=pd.concat([altered['p2/national_monthly_trends'],extra],ignore_index=True)
    out=scenarios(features,altered,phase5_cfg)
    pd.testing.assert_frame_equal(base['scenario_results'],out['scenario_results'])
