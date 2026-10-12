import numpy as np
import pandas as pd
import pytest
from src.statistical_analysis import safe_ratio,calendar_series,growth,describe_series,summaries,regional_comparisons

def test_zero_denominator():
    assert np.isnan(safe_ratio(5,0))
    np.testing.assert_allclose(safe_ratio([6,0],[3,2]),[2,0])

def test_growth_calendar_gap():
    f=pd.DataFrame({'month':pd.to_datetime(['2024-03-01','2024-01-01']),'v':[121,100]})
    s=calendar_series(f,'v')
    assert len(s)==3 and pd.isna(s.iloc[1])
    assert growth(s).isna().all()

def test_known_growth():
    s=pd.Series([100.,110.,0.,20.])
    assert growth(s).iloc[1]==pytest.approx(10)
    assert growth(s).iloc[2]==-100
    assert pd.isna(growth(s).iloc[3])

def test_summary_coverage_and_sample_sd():
    d=describe_series(pd.Series([1.,2.,3.,np.nan]))
    assert d['mean']==2 and d['standard_deviation']==1
    assert d['coverage_pct']==75 and d['missing_months']==1

def test_duplicate_month_rejected():
    f=pd.DataFrame({'month':pd.to_datetime(['2024-01-01']*2),'v':[1,2]})
    with pytest.raises(ValueError): calendar_series(f,'v')

def test_population_grouping_no_quantity_aggregation():
    cal=pd.date_range('2024-01-01',periods=2,freq='MS')
    f=pd.DataFrame({'month':list(cal)*2,'region':['A']*2+['B']*2,'presentation':['X']*2+['Y']*2,
                    'prescription_items':[1,3,10,20],'net_ingredient_cost_gbp':[2,6,30,60],
                    'ingredient_cost_per_item_gbp':[2,2,3,3],'total_quantity':[1,3,100,200],
                    'unit':['tablet']*2+['ml']*2})
    d,g=summaries({'test':(f,['region','presentation','unit'])},cal)
    assert len(d)==6 and len(g)==12
    assert d[d.region=='A'].query("metric == 'prescription_items'")['mean'].iloc[0]==2
    assert 'total_quantity' not in d.metric.values
    assert f.total_quantity.tolist()==[1,3,100,200]

def test_matched_regional_comparisons():
    cal=pd.date_range('2024-01-01',periods=3,freq='MS')
    f=pd.DataFrame({'month':list(cal)*2,'region_name':['A']*3+['B']*3,
                    'prescription_items':[10,20,30,20,40,60], 'net_ingredient_cost_gbp':[10,20,30,40,80,120],
                    'ingredient_cost_per_item_gbp':[1]*3+[2]*3})
    result=regional_comparisons(f)
    assert len(result)==3
    assert result.query("metric == 'prescription_items'").mean_paired_difference.iloc[0]==0
    assert result.query("metric == 'ingredient_cost_per_item_gbp'").mean_paired_difference.iloc[0]==-1
