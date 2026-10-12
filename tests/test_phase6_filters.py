import pandas as pd
from io import BytesIO
from dashboard.filters import apply,search,csv_bytes
from dashboard.data_loader import load

def test_explicit_empty_and_combined_filters():
    f=load('p2/cost_analytics')
    assert apply(f,regions=[]).empty
    code=f.region_code.iloc[0]; key=f.presentation_key.iloc[0]
    out=apply(f,start='2025-01-01',end='2025-12-01',regions=[code],presentations=[key])
    assert out.region_code.eq(code).all() and out.presentation_key.eq(key).all()
    assert out.month.dt.year.eq(2025).all()

def test_csv_matches_filtered_rows():
    f=apply(load('p2/cost_analytics'),regions=[])
    exported=pd.read_csv(BytesIO(csv_bytes(f)))
    assert list(exported)==list(f) and exported.empty

def test_nonempty_csv_matches_filtered_values():
    f=load('p2/cost_analytics'); code=f.region_code.iloc[0]
    selected=apply(f,start='2025-01-01',end='2025-12-01',regions=[code])
    exported=pd.read_csv(BytesIO(csv_bytes(selected)))
    assert len(exported)==len(selected) and exported.region_code.eq(code).all()
    assert exported.prescription_items.sum()==selected.prescription_items.sum()
    assert pd.to_datetime(exported.month).dt.year.eq(2025).all()

def test_literal_search():
    f=pd.DataFrame({'text':['a.b','axb',None]})
    assert search(f,'a.b',['text']).text.tolist()==['a.b']
