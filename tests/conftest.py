import pandas as pd
import duckdb
import pytest
from src.common import ROOT
from src.sql_analytics import build_model

@pytest.fixture(autouse=True)
def preserve_previous_phase_summary():
    """The Phase 3 integration test runs its pipeline; restore its summary after each test."""
    path=ROOT/'outputs/phase3/validation/pipeline_summary.json'
    saved=path.read_bytes() if path.exists() else None
    yield
    if saved is not None and path.read_bytes()!=saved:
        path.write_bytes(saved)

def fixture_rows():
    rows=[]
    for i,month in enumerate(pd.date_range('2023-01-01','2025-12-01',freq='MS')):
        for region in ['A','B']:
            for product,unit in [('P','tablet'),('Q','ml')]:
                # P/A has an internal missing month; Q/B is never observed; P/B has an observed zero.
                if (region=='A' and product=='P' and i==5) or (region=='B' and product=='Q'):
                    continue
                items = 0 if (region=='B' and product=='P' and i==0) else (100+i*10 if product=='P' else 10+i)
                cost = items*(2 if product=='P' else 5)
                rows.append({'month':month,'product_code':product,'product_name':'Presentation '+product,
                             'region_code':region,'region_name':'Region '+region,'unit_of_measure':unit,
                             'chemical_code':'C','chemical_name':'Test chemical','items':float(items),
                             'nic_gbp':float(cost),'total_quantity':float(items*28),'source_row_count':1,'data_origin':'test_fixture'})
    return pd.DataFrame(rows)

@pytest.fixture(scope='session')
def fixture_source():
    return fixture_rows()

@pytest.fixture(scope='session')
def fixture_db(fixture_source):
    con=duckdb.connect(':memory:')
    build_model(con,fixture_source)
    yield con
    con.close()

@pytest.fixture(scope='session')
def actual_db():
    con=duckdb.connect(':memory:')
    build_model(con,pd.read_parquet(ROOT / 'data/processed/monthly_prescribing.parquet'))
    yield con
    con.close()

@pytest.fixture(scope='session')
def phase5_tables():
    return {p.stem:pd.read_parquet(p) for p in (ROOT/'outputs/phase5/tables').glob('*.parquet')}

@pytest.fixture(scope='session')
def phase5_inputs():
    from src.decision_features import load_inputs
    return load_inputs()

@pytest.fixture(scope='session')
def phase5_cfg():
    from src.decision_features import configuration
    return configuration()
