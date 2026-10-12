"""Independent Pandas calculations from protected Parquet; compare unrounded SQL values."""
import json
import duckdb
import numpy as np
import pandas as pd
from .common import ROOT, write_json
from .sql_analytics import SETTINGS, atomic_csv

def reconcile(con, source, settings=SETTINGS):
    rows = []
    cost_tol = settings['cost_absolute_tolerance_gbp']
    ratio_tol = settings['ratio_absolute_tolerance']
    def compare(name, sql, python, tolerance):
        sql_missing, py_missing = pd.isna(sql), pd.isna(python)
        if sql_missing or py_missing:
            difference = np.nan
            passed = bool(sql_missing and py_missing)
        else:
            difference = float(sql)-float(python)
            passed = bool(abs(difference)<=tolerance)
        rows.append({'metric': name, 'sql_result': sql, 'python_result': python,
                     'difference': difference, 'tolerance': tolerance, 'passed': passed})
    def ratio(a,b,scale=1):
        return scale*a/b if pd.notna(a) and pd.notna(b) and b!=0 else np.nan
    total_items = int(source['items'].sum())
    total_cost = source['nic_gbp'].sum()
    sql_total = con.execute('SELECT SUM(prescription_items),SUM(net_ingredient_cost_gbp) FROM phase2.fact_monthly_prescribing').fetchone()
    compare('total_prescription_items',sql_total[0],total_items,0)
    compare('total_net_ingredient_cost_gbp',float(sql_total[1]),total_cost,cost_tol)
    for view, columns, name, has_shares in [
        ('vw_national_monthly_kpis',['month'],'monthly',False),
        ('vw_regional_performance',['region_code'],'regional',True),
        ('vw_presentation_performance',['presentation_key'],'presentation',True)]:
        frame = source.copy()
        frame['presentation_key'] = frame.product_code.astype(str)+'|'+frame.unit_of_measure.astype(str)
        expected = frame.groupby(columns)[['items','nic_gbp']].sum()
        sql_frame = con.execute(f'SELECT * FROM phase2.{view}').df().set_index(columns)
        if set(expected.index)!=set(sql_frame.index):
            compare(f'{name}_key_set_equal',0,1,0)
        for key, record in expected.iterrows():
            if key not in sql_frame.index:
                compare(f'{name}[{key}].missing_sql_key',0,1,0)
                continue
            s = sql_frame.loc[key]
            prefix = f'{name}[{key}]'
            compare(prefix+'.items',s.prescription_items,int(record['items']),0)
            compare(prefix+'.cost_gbp',s.net_ingredient_cost_gbp,record.nic_gbp,cost_tol)
            compare(prefix+'.cost_per_item',s.ingredient_cost_per_item_gbp,ratio(record.nic_gbp,record['items']),ratio_tol)
            if has_shares:
                compare(prefix+'.items_share_pct',s.items_share_pct,ratio(record['items'],total_items,100),ratio_tol)
                compare(prefix+'.cost_share_pct',s.cost_share_pct,ratio(record.nic_gbp,total_cost,100),ratio_tol)
    # Growth reference looks up actual calendar offsets, not a row-count shift.
    for view, groups, name in [('vw_national_monthly_kpis',[],'national'),
                               ('vw_regional_monthly_trends',['region_code'],'region'),
                               ('vw_presentation_monthly_trends',['presentation_key'],'presentation')]:
        frame = source.copy()
        frame['presentation_key'] = frame.product_code.astype(str)+'|'+frame.unit_of_measure.astype(str)
        totals = frame.groupby(groups+['month'])[['items','nic_gbp']].sum()
        sql_frame = con.execute(f'SELECT * FROM phase2.{view}').df()
        for _, s in sql_frame.iterrows():
            group = [s[c] for c in groups]
            def lookup(month, metric):
                key = tuple(group+[month]) if groups else month
                return totals.loc[key,metric] if key in totals.index else np.nan
            month = pd.Timestamp(s.month)
            item = lookup(month,'items')
            for lag,label in [(1,'mom'),(12,'yoy')]:
                previous = lookup(month-pd.DateOffset(months=lag),'items')
                compare(f'{name}[{group},{month.date()}].items_{label}_growth_pct',s[f'items_{label}_growth_pct'],ratio(item-previous,previous,100),ratio_tol)
                current_cost=lookup(month,'nic_gbp')
                previous_cost=lookup(month-pd.DateOffset(months=lag),'nic_gbp')
                compare(f'{name}[{group},{month.date()}].cost_{label}_growth_pct',s[f'cost_{label}_growth_pct'],ratio(current_cost-previous_cost,previous_cost,100),ratio_tol)
    for view, groups, name in [('vw_national_annual_kpis',[],'national_annual'),
                              ('vw_regional_annual_trends',['region_code'],'regional_annual'),
                              ('vw_presentation_annual_trends',['presentation_key'],'presentation_annual')]:
        frame = source.copy()
        frame['presentation_key'] = frame.product_code.astype(str)+'|'+frame.unit_of_measure.astype(str)
        frame['year'] = frame.month.dt.year
        reference = frame.groupby(groups+['year']).agg(items=('items','sum'),nic_gbp=('nic_gbp','sum'),months=('month','nunique'))
        for _, s in con.execute(f'SELECT * FROM phase2.{view}').df().iterrows():
            group = [s[c] for c in groups]
            key = tuple(group+[int(s.calendar_year)]) if groups else int(s.calendar_year)
            prior = tuple(group+[int(s.calendar_year)-1]) if groups else int(s.calendar_year)-1
            current = reference.loc[key] if key in reference.index else None
            previous = reference.loc[prior] if prior in reference.index else None
            growth = np.nan
            cost_growth = np.nan
            if current is not None and previous is not None and current.months==12 and previous.months==12:
                growth = ratio(current['items']-previous['items'],previous['items'],100)
                cost_growth=ratio(current.nic_gbp-previous.nic_gbp,previous.nic_gbp,100)
            compare(f'{name}[{key}].items_growth',s.items_annual_growth_pct,growth,ratio_tol)
            compare(f'{name}[{key}].cost_growth',s.cost_annual_growth_pct,cost_growth,ratio_tol)
    result = pd.DataFrame(rows)
    return result

def run_reconciliation(root=ROOT):
    source = pd.read_parquet(root / 'data/processed/monthly_prescribing.parquet')
    with duckdb.connect(str(root / 'data/processed/pharma.duckdb'),read_only=True) as con:
        con.execute('SET threads=1')
        result = reconcile(con,source)
        decomposition = con.execute('SELECT * FROM phase2.vw_cost_change_decomposition').df()
    atomic_csv(result,root / 'outputs/validation/sql_python_reconciliation.csv')
    summary = {'checks': len(result), 'passed_checks': int(result.passed.sum()), 'failed_checks': int((~result.passed).sum()),
               'maximum_decomposition_residual_gbp': float(decomposition.reconciliation_residual_gbp.abs().max()),
               'decomposition_checks':len(decomposition), 'decomposition_passed':bool(decomposition.reconciliation_residual_gbp.abs().le(SETTINGS['cost_absolute_tolerance_gbp']).all())}
    write_json(root / 'outputs/validation/phase2_reconciliation.json',summary)
    if not result.passed.all() or not summary['decomposition_passed']:
        raise AssertionError('Critical SQL/Python or decomposition reconciliation failure')
    return summary

if __name__=='__main__':
    print(json.dumps(run_reconciliation(),indent=2))
