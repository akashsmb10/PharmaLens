import pytest

def test_internal_gap_longest_runs(fixture_db):
    r=fixture_db.execute("SELECT observed_month_count,internal_missing_month_count,longest_consecutive_observed_run,longest_missing_interval FROM phase2.vw_series_coverage WHERE region_code='A' AND presentation_code='P'").fetchone()
    assert r==(35,1,30,1)
    missing=fixture_db.execute("SELECT coverage_status,prescription_items FROM phase2.vw_series_calendar WHERE region_code='A' AND presentation_code='P' AND month='2023-06-01'").fetchone()
    assert missing==('internal_gap_reporting_or_no_activity_unknown',None)

def test_zero_is_observed_and_never_seen_not_imputed(fixture_db):
    r=fixture_db.execute("SELECT observed_month_count,observed_zero_item_months,full_window_missing_count FROM phase2.vw_series_coverage WHERE region_code='B' AND presentation_code='P'").fetchone()
    assert r==(36,1,0)
    r=fixture_db.execute("SELECT observed_month_count,never_observed_month_count,longest_missing_interval FROM phase2.vw_series_coverage WHERE region_code='B' AND presentation_code='Q'").fetchone()
    assert r==(0,36,36)

def test_actual_phase1_gap_and_extreme_counts(actual_db):
    counts=actual_db.execute('SELECT coverage_status,COUNT(*) FROM phase2.vw_missing_series_months GROUP BY coverage_status').fetchall()
    mapping=dict(counts)
    assert sum(mapping.values())==364
    assert mapping['never_observed_applicability_unknown']==72
    assert sum(v for k,v in mapping.items() if k!='never_observed_applicability_unknown')==292
    assert mapping['internal_gap_reporting_or_no_activity_unknown']==159
    assert actual_db.execute('SELECT COUNT(*) FROM phase2.vw_extreme_value_review').fetchone()[0]==161

def test_forecast_eligibility_thresholds(actual_db):
    candidates=actual_db.execute('SELECT * FROM phase2.vw_forecast_candidates').df()
    assert len(candidates)==29
    assert candidates.observed_month_count.ge(24).all()
    assert candidates.full_window_coverage_pct.eq(100).all()
    assert candidates.internal_missing_month_count.eq(0).all()
    assert candidates.prescription_items.ge(36000).all()

def test_coverage_matrix_does_not_cross_incompatible_units(actual_db):
    assert actual_db.execute('SELECT COUNT(*) FROM phase2.vw_series_calendar').fetchone()[0]==36*7*17
    assert actual_db.execute('SELECT COUNT(*) FROM phase2.vw_series_coverage').fetchone()[0]==119

def test_before_and_after_activity_are_not_imputed(fixture_source):
    import duckdb
    import pandas as pd
    from src.sql_analytics import build_model
    remove=(fixture_source.product_code=='Q') & ~fixture_source.month.between(pd.Timestamp('2023-04-01'),pd.Timestamp('2025-06-01'))
    with duckdb.connect(':memory:') as con:
        build_model(con,fixture_source[~remove])
        row=con.execute("SELECT observed_month_count,before_first_observed_count,after_last_observed_count,internal_missing_month_count,longest_missing_interval FROM phase2.vw_series_coverage WHERE presentation_code='Q' AND region_code='A'").fetchone()
        assert row==(27,3,6,0,6)
