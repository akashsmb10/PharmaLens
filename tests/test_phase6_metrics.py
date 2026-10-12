import numpy as np
import pandas as pd
import pytest
from dashboard.metrics import totals,annual_growth,shares,summarize,ratio
from dashboard.data_loader import load
from dashboard.filters import apply

def test_weighted_ratio_and_nulls():
    f=load('p2/cost_analytics')
    assert totals(f)['nic_per_item_gbp']==pytest.approx(f.net_ingredient_cost_gbp.sum()/f.prescription_items.sum())
    assert np.isnan(totals(f.iloc[:0])['items'])
    assert np.isnan(ratio(12,0))

def test_partial_window_growth_unavailable():
    f=load('p2/cost_analytics'); f=apply(f,start='2025-01-01',end='2025-06-01')
    g=annual_growth(f,2025).iloc[0]
    assert pd.isna(g.item_growth_pct) and 'incomplete' in g.status

def test_scope_share_denominator():
    f=load('p2/cost_analytics'); f=f[f.month.dt.year.eq(2025)]
    summary=shares(summarize(f,['region_code']),f)
    assert summary.item_share_pct.sum()==pytest.approx(100)
    subset=shares(summary.iloc[:1],f)
    assert subset.item_share_pct.iloc[0]==pytest.approx(summary.item_share_pct.iloc[0])
