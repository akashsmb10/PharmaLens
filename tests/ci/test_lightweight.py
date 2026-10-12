"""Data-free CI: deterministic accounting, filters, contracts, imports and startup."""
import importlib
import math
import pandas as pd
import pytest
from dashboard.data_contracts import validate,DataError
from dashboard.filters import apply,csv_bytes
from dashboard.metrics import ratio
from dashboard.scenarios import simulate

def test_runtime_modules_import_without_external_data():
    for module in ['dashboard.data_loader','dashboard.metrics','dashboard.chart_factory','dashboard.navigation','dashboard.scenarios']:
        importlib.import_module(module)

def test_scenario_accounting_fixture():
    out=simulate(1000,2000,5,-5,'deterministic fixture').iloc[0]
    assert out.hypothetical_nic_gbp==pytest.approx(1995)
    assert out.break_even_cost_change_pct==pytest.approx(-4.7619047619)
    with pytest.raises(ValueError): simulate(0,0,0,0,'absent')

def test_filter_export_and_undefined_denominator():
    frame=pd.DataFrame({'month':pd.to_datetime(['2025-01-01','2025-02-01']),'region_code':['A','B'],'value':[10,20]})
    selected=apply(frame,regions=['A']); assert len(selected)==1 and b'A' in csv_bytes(selected)
    assert apply(frame,regions=[]).empty and math.isnan(ratio(1,0))

def test_contract_rejects_duplicate_business_keys():
    frame=pd.DataFrame({'id':['A','A'],'prescription_items':[1.,2.]})
    contract={'columns':list(frame),'keys':['id'],'rows':2,'dtypes':{c:str(frame[c].dtype) for c in frame},'dates':{}}
    with pytest.raises(DataError): validate(frame,contract,'fixture')

def test_app_missing_manifest_is_clear(tmp_path,monkeypatch):
    from dashboard.data_loader import manifest
    with pytest.raises(DataError,match='manifest is unavailable'): manifest(tmp_path)

def test_streamlit_http_startup_fixture(tmp_path):
    from src.phase6_startup import startup
    (tmp_path/'app.py').write_text('import streamlit as st\nst.title("CI fixture startup")\n',encoding='utf-8')
    result=startup(tmp_path)
    assert result['passed'] and result['listener_closed']
