import pandas as pd
from src.forecast_reconciliation import hierarchy

def test_hierarchy_all_presentations_not_candidate_subset():
    months=pd.date_range('2024-01-01',periods=2,freq='MS')
    national=pd.DataFrame({'month':months,'prescription_items':[28,28]})
    regional=pd.DataFrame([{'month':m,'region_code':str(r),'prescription_items':r} for m in months for r in range(1,8)])
    detail=pd.DataFrame([{'month':m,'region_code':str(r),'prescription_items':r/2} for m in months for r in range(1,8) for _ in range(2)])
    selected=pd.DataFrame([{'split_type':'holdout','origin_date':pd.Timestamp('2023-12-01'),'target_date':months[0],'horizon':1,
                           'aggregation_level':'national','series_id':'England','actual':28.,'prediction':29.,'mase_scale':1.}]+
                         [{'split_type':'holdout','origin_date':pd.Timestamp('2023-12-01'),'target_date':months[0],'horizon':1,
                           'aggregation_level':'regional','series_id':str(r),'actual':float(r),'prediction':float(r),'mase_scale':1.} for r in range(1,8)])
    checks,comparison,metrics=hierarchy({'national':(national,[]),'regional':(regional,[]),'region_presentation':(detail,[])},selected)
    assert checks.status.eq('passed').all() and len(checks)==16
    assert comparison.regional_sum.iloc[0]==28 and comparison.coherence_gap.iloc[0]==-1
    assert set(metrics.approach)=={'direct_national','sum_all_seven_regions'}
