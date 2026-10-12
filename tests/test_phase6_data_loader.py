import json
import pytest
from dashboard.data_loader import load,manifest,safe_path
from dashboard.data_contracts import DataError,validate
from src.common import ROOT

@pytest.mark.parametrize('name',list(manifest()['datasets']))
def test_every_runtime_contract(name):
    assert len(load(name))==manifest()['datasets'][name]['rows']

def test_cache_isolation():
    f=load('p2/cost_analytics'); original=f.prescription_items.iloc[0]
    f.loc[0,'prescription_items']=-999
    assert load('p2/cost_analytics').prescription_items.iloc[0]==original

def test_missing_manifest_and_optional(tmp_path):
    with pytest.raises(DataError): load('p2/cost_analytics',tmp_path)
    assert load('absent',optional=True) is None
    with pytest.raises(DataError): load('absent')

def test_path_escape():
    with pytest.raises(DataError): safe_path(ROOT,'../outside.parquet')

@pytest.mark.parametrize('mutation',['missing','duplicate','type','negative'])
def test_invalid_contract(mutation):
    name='p2/cost_analytics'; f=load(name); c=manifest()['datasets'][name]
    if mutation=='missing': f=f.drop(columns=['prescription_items'])
    elif mutation=='duplicate': f.iloc[1]=f.iloc[0]
    elif mutation=='type': f['prescription_items']=f.prescription_items.astype(str)
    else: f.loc[0,'prescription_items']=-1
    with pytest.raises(DataError): validate(f,c,name)

def test_corrupted_runtime_rejected(tmp_path):
    m=manifest(); c=m['datasets']['p2/cost_analytics']; path=tmp_path/c['path']; path.parent.mkdir(parents=True)
    path.write_bytes(b'corrupt parquet')
    (tmp_path/'config').mkdir(); (tmp_path/'config/dashboard_manifest.json').write_text(json.dumps(m))
    with pytest.raises(DataError,match='validated version'): load('p2/cost_analytics',tmp_path)

def test_percentage_roundoff_and_growth_not_bounded():
    name='p5/national_decision_summary'; f=load(name); c=manifest()['datasets'][name]
    f.loc[0,'historical_nic_share_pct']=100+1e-12
    validate(f,c,name)
    f.loc[0,'historical_nic_share_pct']=100.01
    with pytest.raises(DataError): validate(f,c,name)
