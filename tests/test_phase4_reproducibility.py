import json
import numpy as np
import pandas as pd
from src.common import ROOT,sha256
from src.forecast_config import configuration
from src.forecast_data import load_forecasting_data,prepare_series,protected_snapshot
from src.forecast_models import fit_forecast

def test_training_eligibility_ignores_future_inventory():
    cfg=configuration(); _,_,pops,loaded,_=load_forecasting_data(cfg)
    a,e,_=prepare_series(pops,loaded['forecast_candidate_series'],cfg)
    mutated={k:(f.copy(deep=True),keys) for k,(f,keys) in pops.items()}
    for f,_ in mutated.values(): f.loc[f.month>pd.Timestamp('2024-12-01'),'prescription_items']=0
    b,other,_=prepare_series(mutated,loaded['forecast_candidate_series'].iloc[:0],cfg)
    assert sorted(a)==sorted(b)
    assert e.eligible.tolist()==other.eligible.tolist()

def test_models_reproducible():
    cfg=configuration(); s=pd.Series(100+np.arange(24)*2.,index=pd.date_range('2023-01-01',periods=24,freq='MS'))
    for model in cfg['models']:
        v={'model':model,'variant':model,'alpha':1}
        a=fit_forecast(s,[1,2,3],v,cfg); b=fit_forecast(s,[1,2,3],v,cfg)
        np.testing.assert_array_equal(a[1],b[1])

def test_operational_dates_metadata_and_uniqueness():
    f=pd.read_parquet(ROOT/'outputs/phase4/tables/operational_forecasts.parquet')
    assert set(f.forecast_month)==set(pd.date_range('2026-01-01',periods=3,freq='MS'))
    assert f.training_end_date.eq(pd.Timestamp('2025-12-01')).all()
    assert not f.duplicated(['series_id','horizon']).any()
    assert f.point_forecast.ge(0).all() and f.model_version.notna().all() and f.data_version.str.len().eq(64).all()
    assert f.lower_80.isna().all() # Current development supplies only six/five/four residuals.

def test_prior_artifact_hashes():
    expected=json.loads((ROOT/'outputs/phase4/validation/source_guard.json').read_text())
    assert protected_snapshot()==expected

def test_recorded_predictions_valid_horizon_and_stage():
    f=pd.read_parquet(ROOT/'outputs/phase4/tables/backtest_predictions.parquet')
    assert not f.duplicated(['series_id','variant','origin_date','horizon','split_type']).any()
    for r in f.itertuples(): assert r.target_date==r.origin_date+pd.DateOffset(months=int(r.horizon))
    hold=f[f.split_type.eq('holdout')]
    assert hold.origin_date.ge(pd.Timestamp('2025-06-01')).all()
    assert f[f.split_type.eq('development')].target_date.le(pd.Timestamp('2025-06-01')).all()

def test_full_pipeline_idempotence_evidence():
    # Audit executes both full pipelines before pytest; verify the recorded runs against actual files.
    evidence=json.loads((ROOT/'outputs/phase4/validation/reproducibility.json').read_text())
    assert evidence['byte_identical'] and evidence['first_exports']==evidence['second_exports']
    for stem,item in evidence['second_exports'].items():
        for suffix in ['csv','parquet']:
            assert sha256(ROOT/f'outputs/phase4/tables/{stem}.{suffix}')==item[f'{suffix}_sha256']
