import pandas as pd
from src.common import ROOT
from src.reconcile_metrics import reconcile

def test_fixture_sql_python_agreement(fixture_db,fixture_source):
    result=reconcile(fixture_db,fixture_source)
    assert result.passed.all(), result.loc[~result.passed].to_string()

def test_actual_sql_python_agreement(actual_db):
    result=reconcile(actual_db,pd.read_parquet(ROOT / 'data/processed/monthly_prescribing.parquet'))
    assert len(result)==3980
    assert result.passed.all(), result.loc[~result.passed].to_string()

def test_reconciliation_detects_independent_source_discrepancy(fixture_db,fixture_source):
    wrong=fixture_source.copy()
    wrong.loc[0,'items']+=1
    result=reconcile(fixture_db,wrong)
    assert not result.passed.all()
    assert not result.loc[result.metric=='total_prescription_items','passed'].iloc[0]
