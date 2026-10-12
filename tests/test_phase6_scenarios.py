import pytest
from dashboard.scenarios import simulate,two_way,mix_simulation
from dashboard.data_loader import load
from dashboard.metrics import totals,summarize

@pytest.mark.parametrize('v,c',[(0,0),(5,0),(5,-5),(-20,20),(20,-20)])
def test_hypothetical_accounting_and_offset(v,c):
    r=simulate(100,200,v,c,'test').iloc[0]
    assert r.hypothetical_nic_gbp==pytest.approx(200*(1+v/100)*(1+c/100))
    assert (1+v/100)*(1+r.break_even_cost_change_pct/100)==pytest.approx(1)
    assert r.evidence_class=='Hypothetical scenario'

def test_zero_baseline_rejected():
    with pytest.raises(ValueError): simulate(0,0,0,0,'missing')

def test_mix_and_sensitivity():
    f=load('p2/cost_analytics'); f=f[f.month.dt.year.eq(2025)]; k=totals(f)
    p=summarize(f,['presentation_key','presentation_name']).rename(columns={'prescription_items':'recent_items','nic_per_item_gbp':'recent_nic_per_item_gbp'}).sort_values('recent_items',ascending=False)
    out=mix_simulation(p,k['items'],p.presentation_key.iloc[0],p.presentation_key.iloc[1],5)
    assert out.scenario_share.ge(0).all() and out.scenario_share.sum()==pytest.approx(1)
    assert out.hypothetical_items.sum()==pytest.approx(k['items'])
    assert len(two_way(k['items'],k['nic_gbp']))==25
