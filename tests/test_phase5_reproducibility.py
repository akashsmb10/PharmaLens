import json
import nbformat
import pytest
from src.common import ROOT,sha256
from src.decision_features import protected_snapshot,load_inputs

def test_full_pipeline_two_run_evidence():
    evidence=json.loads((ROOT/'outputs/phase5/validation/reproducibility.json').read_text())
    assert evidence['byte_identical'] and evidence['first_exports']==evidence['second_exports']
    for name,item in evidence['second_exports'].items():
        for extension in ['csv','parquet']: assert sha256(ROOT/f'outputs/phase5/tables/{name}.{extension}')==item[extension+'_sha256']

def test_protected_artifacts():
    expected=json.loads((ROOT/'outputs/phase5/validation/source_guard.json').read_text())
    assert protected_snapshot()==expected

def test_changed_frozen_input_rejected(monkeypatch):
    monkeypatch.setattr('src.decision_features.sha256',lambda path:'invalid_hash')
    with pytest.raises(AssertionError,match='Frozen Phase 4 output changed'): load_inputs()

def test_eighteen_real_chart_artifacts():
    paths=list((ROOT/'outputs/phase5/charts').glob('*.png')); assert len(paths)==18
    for p in paths: assert p.read_bytes().startswith(b'\x89PNG') and p.stat().st_size>10000

@pytest.mark.parametrize('name',['06_decision_intelligence','07_scenario_analysis'])
def test_notebooks_fully_executed(name):
    nb=nbformat.read(ROOT/f'notebooks/{name}.ipynb',as_version=4)
    codes=[c for c in nb.cells if c.cell_type=='code']; assert len(codes)>=6
    assert all(c.execution_count is not None for c in codes)
    assert all(o.output_type!='error' for c in codes for o in c.outputs)
