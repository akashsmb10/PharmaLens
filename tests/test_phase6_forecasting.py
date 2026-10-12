import pytest
from dashboard.data_loader import load
from dashboard.metrics import comparisons

@pytest.mark.parametrize('h',[1,2,3])
def test_holdout_common_support_and_frozen_selection(h):
    back=load('p4/backtest_predictions'); back=back[back.series_id.eq('England')&back.split_type.eq('holdout')&back.horizon.eq(h)]
    families=load('p4/frozen_family_configurations'); variants=families[families.aggregation_level.eq('national')].variant.tolist()
    out,good=comparisons(back,variants)
    assert len(out)==5 and out.n.nunique()==1 and out.n.iloc[0]==7-h
    assert good.groupby(['origin_date','horizon']).variant.nunique().eq(5).all()
    before=load('p4/model_selection_decisions'); comparisons(back,[variants[0]])
    assert before.equals(load('p4/model_selection_decisions'))

def test_failed_predictions_are_not_zero():
    f=load('p4/backtest_predictions'); f=f[f.series_id.eq('England')&f.horizon.eq(1)&f.split_type.eq('holdout')].copy()
    variants=f.variant.unique().tolist(); index=f.index[0]
    f.loc[index,'prediction']=float('nan'); f.loc[index,'model_status']='failed'
    metrics,good=comparisons(f,variants)
    assert metrics.n.eq(5).all() and good.model_status.eq('ok').all()
