import pandas as pd
import numpy as np
import pytest
from src.ingest import synthetic_source, normalize, aggregate, check_columns, load_csv, KEY
from src.validate import audit
from src.ingest import ingest, fetch_json
from src.common import write_json, sha256

@pytest.fixture
def source():
    return synthetic_source()

def findings(report, name):
    return next(c['count'] for c in report['checks'] if c['check'] == name)

def test_required_columns(source):
    check_columns(source)
    with pytest.raises(ValueError, match='ITEMS'):
        check_columns(source.drop(columns='ITEMS'))

def test_dates_and_types(source):
    df = normalize(source, False)
    assert pd.api.types.is_datetime64_any_dtype(df.month)
    assert df.month.notna().all() and df.month.dt.day.eq(1).all()
    assert pd.api.types.is_float_dtype(df['items'])
    assert df.product_code.iloc[0] == 'SYN_P0'

def test_invalid_date_and_numeric(source):
    source.loc[0, 'YEAR_MONTH'] = '202313'
    source.loc[1, 'ITEMS'] = 'invalid'
    df = normalize(source, False)
    report = audit(df, aggregate(df))
    assert findings(report, 'invalid_dates') == 1
    assert findings(report, 'invalid_numeric_items') == 1
    assert not report['passed']

def test_business_key_and_reconciliation(source):
    df = normalize(source, False)
    monthly = aggregate(df)
    assert not monthly.duplicated(KEY).any()
    assert monthly['items'].sum() == df['items'].sum()
    report = audit(df, monthly)
    assert report['passed']
    report = audit(df, pd.concat([monthly, monthly.iloc[[0]]], ignore_index=True))
    assert findings(report, 'duplicate_monthly_business_keys') == 2
    assert not report['passed']

def test_missing_reporting(source):
    source.loc[0, 'REGION_CODE'] = pd.NA
    df = normalize(source, False)
    report = audit(df, aggregate(df))
    assert findings(report, 'required_missing_values') == 1
    assert not report['passed']

def test_reproducible_ingestion(source, tmp_path):
    pd.testing.assert_frame_equal(source, synthetic_source())
    path = tmp_path / 'source.csv'
    source.to_csv(path, index=False)
    pd.testing.assert_frame_equal(normalize(load_csv(path), False), normalize(load_csv(path), False))

def test_negative_and_zero_behavior(source):
    source.loc[0, 'TOTAL_QUANTITY'] = '-1'
    source.loc[1, 'ITEMS'] = '0'
    df = normalize(source, False)
    report = audit(df, aggregate(df))
    assert findings(report, 'negative_total_quantity') == 1
    assert findings(report, 'zero_items') == 1
    assert len(df) == len(source)

def test_duplicate_raw_rows(source):
    df = normalize(pd.concat([source, source.iloc[[0]]], ignore_index=True), False)
    report = audit(df, aggregate(df))
    assert findings(report, 'duplicate_source_rows') == 2
    assert findings(report, 'duplicate_source_business_keys') == 2

def test_missing_months(source):
    source = source[source.YEAR_MONTH != '202301']
    df = normalize(source, False)
    report = audit(df, aggregate(df))
    assert findings(report, 'missing_global_months') == 1
    assert not report['passed']

def test_units_remain_separate(source):
    extra = source.iloc[[0]].copy()
    extra['UNIT_OF_MEASURE'] = 'ml'
    df = normalize(pd.concat([source, extra], ignore_index=True), False)
    monthly = aggregate(df)
    assert len(monthly) == len(source) + 1

def test_missing_metric_not_silently_dropped(source):
    extra = source.iloc[[0]].copy()
    combined = pd.concat([source, extra], ignore_index=True)
    combined.loc[len(combined)-1, 'ITEMS'] = pd.NA
    df = normalize(combined, False)
    monthly = aggregate(df)
    assert monthly['items'].isna().sum() == 1
    assert not audit(df, monthly)['passed']

def test_nonfinite_numeric(source):
    source.loc[0, 'NIC'] = 'inf'
    df = normalize(source, False)
    assert findings(audit(df, aggregate(df)), 'invalid_numeric_nic_gbp') == 1

def test_missing_required_monthly_column(source):
    df = normalize(source, False)
    report = audit(df, aggregate(df).drop(columns='items'))
    assert not report['passed']

def test_identifier_encoding_and_leading_zeros(tmp_path):
    path = tmp_path / 'latin.csv'
    path.write_bytes('code,name\n0101010J0AAAAAA,caf\xe9\n'.encode('cp1252'))
    df = load_csv(path)
    assert df.code.iloc[0] == '0101010J0AAAAAA'
    assert df.name.iloc[0] == 'caf\xe9'

def test_cached_ingestion_uses_no_network(tmp_path, monkeypatch):
    cached = tmp_path / 'cached.json'
    write_json(cached, {'success': True, 'result': {'records': [{'ITEMS': 10}]}})
    def prohibited(*args, **kwargs):
        raise AssertionError('Cached ingestion attempted a network request')
    monkeypatch.setattr('urllib.request.urlopen', prohibited)
    a, downloaded_a = fetch_json('https://example.invalid', cached)
    b, downloaded_b = fetch_json('https://example.invalid', cached)
    assert a == b and not downloaded_a and not downloaded_b

def test_full_synthetic_ingestion_reproducibility(tmp_path):
    _, first, manifest = ingest(root=tmp_path, synthetic=True)
    assert manifest['mode'] == 'synthetic'
    assert first.data_origin.eq('synthetic_demo').all()
    assert manifest['files'][0]['sha256'] == sha256(tmp_path / manifest['files'][0]['file'])
    _, second, repeat = ingest(root=tmp_path, synthetic=True)
    pd.testing.assert_frame_equal(first, second)
    assert manifest['processed_sha256'] == repeat['processed_sha256']

def test_type_errors_are_reported(source):
    detailed = normalize(source, False)
    monthly = aggregate(detailed)
    monthly['items'] = monthly['items'].astype('string')
    report = audit(detailed, monthly)
    assert not report['passed']
    assert findings(report, 'data_type_correctness') == 1

def test_optional_blank_is_missing_warning(source):
    source['SUPPLIER_NAME'] = ''
    df = normalize(source, False)
    assert df.SUPPLIER_NAME.isna().all()
    report = audit(df, aggregate(df))
    assert findings(report, 'optional_missing_values') == len(source)
    assert report['passed']

def test_schema_absence_is_a_valid_exception(source):
    source['PHARMACY_ADVANCED_SERVICE'] = 'Not applicable'
    source.loc[source.YEAR_MONTH.lt('202402'), 'PHARMACY_ADVANCED_SERVICE'] = ''
    df = normalize(source, False)
    report = audit(df, aggregate(df))
    assert findings(report, 'structural_schema_absence') == 117
    assert findings(report, 'optional_missing_values') == 0
    assert report['passed']
