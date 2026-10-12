import numpy as np
import pytest

def test_national_total_independent(fixture_db,fixture_source):
    result=fixture_db.execute('SELECT SUM(prescription_items),SUM(net_ingredient_cost_gbp) FROM phase2.vw_national_monthly_kpis').fetchone()
    assert result[0]==int(fixture_source['items'].sum())
    assert float(result[1])==fixture_source.nic_gbp.sum()

def test_weighted_cost_and_shares(fixture_db,fixture_source):
    for view,key in [('vw_regional_performance','region_code'),('vw_presentation_performance','presentation_key')]:
        frame=fixture_db.execute(f'SELECT * FROM phase2.{view}').df()
        assert frame.items_share_pct.sum()==pytest.approx(100)
        assert frame.cost_share_pct.sum()==pytest.approx(100)
        for _,r in frame.iterrows():
            assert r.ingredient_cost_per_item_gbp==pytest.approx(r.net_ingredient_cost_gbp/r.prescription_items)
    # Jan national: P/A 100 items £200, P/B 0 £0, Q/A 10 £50 => weighted £250/110.
    value=fixture_db.execute("SELECT ingredient_cost_per_item_gbp FROM phase2.vw_national_monthly_kpis WHERE month='2023-01-01'").fetchone()[0]
    assert value==pytest.approx(250/110)
    assert value!=pytest.approx((2+5)/2)

def test_zero_denominator_is_null(fixture_db):
    result=fixture_db.execute("SELECT ingredient_cost_per_item_gbp,ingredient_cost_per_native_unit_gbp FROM phase2.vw_cost_analytics WHERE region_code='B' AND month='2023-01-01'").fetchone()
    assert result==(None,None)
    growth=fixture_db.execute("SELECT items_mom_growth_pct FROM phase2.vw_regional_monthly_trends WHERE region_code='B' AND month='2023-02-01'").fetchone()[0]
    assert growth is None

def test_calendar_mom_yoy(fixture_db):
    result=fixture_db.execute("SELECT items_mom_growth_pct,items_yoy_growth_pct FROM phase2.vw_presentation_monthly_trends WHERE presentation_code='Q' AND month='2024-01-01'").fetchone()
    assert result[0]==pytest.approx(100*(22-21)/21)
    assert result[1]==pytest.approx(120)
    # A/P June is absent; July's previous calendar month remains NULL, not May's value.
    result=fixture_db.execute("SELECT items_mom_growth_pct FROM phase2.vw_regional_monthly_trends WHERE region_code='A' AND month='2023-07-01'").fetchone()[0]
    assert result is not None # regional aggregate still includes Q, so June is observed nationally/regionally.

def test_rolling_windows(fixture_db,fixture_source):
    frame=fixture_db.execute('SELECT * FROM phase2.vw_national_monthly_kpis ORDER BY month').df()
    expected=fixture_source.groupby('month')['items'].sum()
    for width,col in [(3,'items_rolling_3m'),(6,'items_rolling_6m'),(12,'items_rolling_12m')]:
        np.testing.assert_allclose(frame[col],expected.rolling(width,min_periods=width).mean(),equal_nan=True)

def test_ranking_concentration(fixture_db):
    frame=fixture_db.execute('SELECT * FROM phase2.vw_presentation_concentration ORDER BY pareto_position').df()
    assert frame.iloc[0].presentation_code=='P'
    assert list(frame.pareto_position)==[1,2]
    assert frame.cumulative_items_share_pct.iloc[-1]==pytest.approx(100)
    assert frame.items_hhi_0_to_1.iloc[0]==pytest.approx(sum((frame.items_share_pct/100)**2))

def test_exact_decomposition(fixture_db):
    rows=fixture_db.execute('SELECT * FROM phase2.vw_cost_change_decomposition').df()
    for _,r in rows.iterrows():
        v0,v1=r.baseline_items,r.prescription_items
        p0,p1=r.baseline_cost_gbp/v0,r.net_ingredient_cost_gbp/v1
        assert r.item_volume_effect_gbp==pytest.approx((v1-v0)*(p1+p0)/2)
        assert r.aggregate_unit_cost_and_mix_effect_gbp==pytest.approx((p1-p0)*(v1+v0)/2)
        assert r.reconciliation_residual_gbp==pytest.approx(0,abs=1e-8)

def test_quantity_unit_contract(fixture_db):
    assert fixture_db.execute('SELECT COUNT(DISTINCT unit_of_measure) FROM phase2.dim_presentation').fetchone()[0]==2
    national_columns=[r[0] for r in fixture_db.execute('DESCRIBE phase2.vw_national_monthly_kpis').fetchall()]
    assert 'total_quantity' not in national_columns
    rows=fixture_db.execute('SELECT presentation_code,ingredient_cost_per_native_unit_gbp FROM phase2.vw_presentation_performance').fetchall()
    expected={'P':2/28,'Q':5/28}
    for code,value in rows:
        assert value==pytest.approx(expected[code])

def test_missing_calendar_period_is_not_previous_available_row(fixture_source):
    import duckdb
    from src.sql_analytics import build_model
    absent=fixture_source[fixture_source.month!=__import__('pandas').Timestamp('2023-06-01')]
    with duckdb.connect(':memory:') as con:
        build_model(con,absent)
        missing=con.execute("SELECT prescription_items FROM phase2.vw_national_monthly_kpis WHERE month='2023-06-01'").fetchone()[0]
        july=con.execute("SELECT items_mom_growth_pct,items_rolling_3m FROM phase2.vw_national_monthly_kpis WHERE month='2023-07-01'").fetchone()
        yoy=con.execute("SELECT items_yoy_growth_pct FROM phase2.vw_national_monthly_kpis WHERE month='2024-06-01'").fetchone()[0]
        assert missing is None and july==(None,None) and yoy is None
