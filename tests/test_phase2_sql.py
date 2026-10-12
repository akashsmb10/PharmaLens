import pandas as pd
import pytest
from src.sql_analytics import build_model,EXPORTS

def test_fact_grain_and_dimension_keys(fixture_db):
    assert fixture_db.execute('SELECT COUNT(*) FROM phase2.fact_monthly_prescribing').fetchone()[0]==107
    for table,key in [('dim_month','month'),('dim_region','region_code'),('dim_presentation','presentation_key')]:
        count,distinct=fixture_db.execute(f'SELECT COUNT(*),COUNT(DISTINCT {key}) FROM phase2.{table}').fetchone()
        assert count==distinct
    assert fixture_db.execute('SELECT SUM(failure_count) FROM phase2.vw_model_quality').fetchone()[0]==0

def test_joins_do_not_multiply(fixture_db):
    a=fixture_db.execute('SELECT COUNT(*),SUM(prescription_items) FROM phase2.fact_monthly_prescribing').fetchone()
    b=fixture_db.execute('SELECT COUNT(*),SUM(prescription_items) FROM phase2.vw_fact_enriched').fetchone()
    assert a==b

def test_reporting_view_grains(actual_db):
    cases=[('vw_national_monthly_kpis','month'),('vw_regional_performance','region_code'),
           ('vw_regional_monthly_trends','month,region_code'),('vw_presentation_performance','presentation_key'),
           ('vw_presentation_monthly_trends','month,presentation_key'),('vw_cost_analytics','month,region_code,presentation_key'),
           ('vw_series_coverage','region_code,presentation_key'),('vw_forecast_candidates','region_code,presentation_key')]
    for view,key in cases:
        count=actual_db.execute(f'SELECT COUNT(*) FROM phase2.{view}').fetchone()[0]
        distinct=actual_db.execute(f'SELECT COUNT(*) FROM (SELECT DISTINCT {key} FROM phase2.{view})').fetchone()[0]
        assert count==distinct

def test_no_registered_input_dependencies(fixture_db):
    for view in EXPORTS.values():
        fixture_db.execute(f'SELECT * FROM phase2.{view} LIMIT 1').fetchall()

def test_sql_rerun_is_idempotent(fixture_source):
    import duckdb
    with duckdb.connect(':memory:') as con:
        build_model(con,fixture_source)
        first={v:con.execute(f'SELECT * FROM phase2.{v} ORDER BY ALL').df() for v in EXPORTS.values()}
        build_model(con,fixture_source)
        for v,frame in first.items():
            pd.testing.assert_frame_equal(frame,con.execute(f'SELECT * FROM phase2.{v} ORDER BY ALL').df())

def test_duplicate_input_is_rejected(fixture_source):
    import duckdb
    with duckdb.connect(':memory:') as con:
        duplicate=pd.concat([fixture_source,fixture_source.iloc[[0]]],ignore_index=True)
        with pytest.raises(ValueError,match='Duplicate'):
            build_model(con,duplicate)
