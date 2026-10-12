"""Pure filters preserve nulls, input order and explicit empty selections."""
import pandas as pd

def apply(frame,start=None,end=None,regions=None,presentations=None,models=None,horizon=None,stage=None,date_column='month'):
    out=frame.copy(deep=True)
    if start is not None: out=out[out[date_column].ge(pd.Timestamp(start))]
    if end is not None: out=out[out[date_column].le(pd.Timestamp(end))]
    for values,col in [(regions,'region_code'),(presentations,'presentation_key'),(models,'variant')]:
        if values is not None: out=out[out[col].isin(values)]
    if horizon is not None: out=out[out.horizon.eq(horizon)]
    if stage is not None: out=out[out.split_type.eq(stage)]
    return out.copy(deep=True)

def search(frame,text,columns):
    if not text.strip(): return frame.copy()
    combined=frame[columns].fillna('').astype(str).agg(' '.join,axis=1)
    return frame[combined.str.contains(text,case=False,regex=False)].copy()

def csv_bytes(frame): return frame.to_csv(index=False,date_format='%Y-%m-%d').encode('utf-8-sig')
