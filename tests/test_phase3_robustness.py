import json
import numpy as np
import pandas as pd
import pytest
from src.anomaly_diagnostics import robust_z
from src.common import ROOT,sha256
from src.phase3_pipeline import load_inputs,protected_snapshot,run_phase3
from src.robustness_analysis import robustness

def test_robust_z_known_fixture():
    s=pd.Series(np.tile([1.,2.,3.],4))
    z,mad=robust_z(s)
    assert mad==1
    np.testing.assert_allclose(z.iloc[:3],[-.6744897501960817,0,.6744897501960817])

def test_zero_mad():
    z,mad=robust_z(pd.Series([5.]*15))
    assert mad==0 and z.isna().all()

def test_short_robust_z():
    assert robust_z(pd.Series([1.,2.,3.]))[0].isna().all()

def test_phase3_inputs_and_missingness():
    loaded,pops,calendar,evidence=load_inputs()
    detail=pops['region_presentation'][0]
    assert len(calendar)==36 and len(detail)==4284
    assert detail.prescription_items.isna().sum()==364
    assert detail.loc[detail.prescription_items.isna(),'net_ingredient_cost_gbp'].isna().all()
    assert evidence['total_items']==212022236
    assert len(loaded['forecast_candidate_series'])==29

def test_robustness_deterministic_and_immutable():
    loaded,pops,calendar,_=load_inputs()
    before=pops['region_presentation'][0].copy(deep=True)
    a=robustness(pops,loaded['extreme_value_review'],loaded['series_coverage'],calendar)
    b=robustness(pops,loaded['extreme_value_review'],loaded['series_coverage'],calendar)
    for x,y in zip(a,b): pd.testing.assert_frame_equal(x,y)
    pd.testing.assert_frame_equal(pops['region_presentation'][0],before)
    assert len(a[2])==5

def test_pipeline_rerun_schema_and_source_preservation():
    before=protected_snapshot()
    first=run_phase3(make_charts=False,make_reports=False)
    second=run_phase3(make_charts=False,make_reports=False)
    assert first['tables']==second['tables']
    assert protected_snapshot()==before
    assert len(first['tables'])==20
    assert first['decomposition_max_residual_gbp']<.01
    assert first['original_extreme_flags_retained']==161
    d=pd.read_parquet(ROOT/'outputs/phase3/tables/extreme_value_review_phase3.parquet')
    assert d.phase2_flag.all() and d.observed_value.notna().all()
    assert set(d.classification).issubset({'Potential data issue','Potential structural shift','Unusual but plausible activity','Insufficient evidence'})

def test_chart_inventory_valid_png():
    # Verify already executed production plots, including nonempty image dimensions.
    import matplotlib.image as mpimg
    paths=list((ROOT/'outputs/phase3/charts').glob('*.png'))
    assert len(paths)==18
    for p in paths:
        a=mpimg.imread(p)
        assert a.shape[0]>=700 and a.shape[1]>=1500
