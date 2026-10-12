from dashboard.data_loader import manifest
from src.phase6_audit import numerical_checks,protected_snapshot
import json
from src.common import ROOT

def test_deterministic_numerical_reconciliation():
    assert numerical_checks()==numerical_checks()

def test_protected_artifacts():
    guard=json.loads((ROOT/'outputs/phase6/validation/source_guard.json').read_text())
    assert protected_snapshot()==guard
