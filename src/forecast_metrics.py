"""Origin-specific nonseasonal MASE and individual-error aggregation."""
import numpy as np
import pandas as pd

def mase_scale(training):
    s=np.asarray(training,dtype=float)
    if len(s)<2 or not np.isfinite(s).all(): return np.nan
    value=float(np.mean(np.abs(np.diff(s))))
    return value if value>0 else np.nan

def metrics(frame):
    f=frame.dropna(subset=['actual','prediction'])
    a=f.actual.to_numpy(dtype=float); p=f.prediction.to_numpy(dtype=float); e=p-a
    n=len(e)
    if not n: return {'n':0,**{m:np.nan for m in ['MAE','RMSE','WAPE','sMAPE','MASE','Bias']},'mase_defined_rows':0}
    d=np.abs(a)+np.abs(p); smape=np.divide(200*np.abs(e),d,out=np.zeros(n),where=d!=0)
    scales=f.mase_scale.to_numpy(dtype=float)
    scaled=np.divide(np.abs(e),scales,out=np.full(n,np.nan),where=np.isfinite(scales)&(scales>0))
    return {'n':n,'MAE':float(np.mean(np.abs(e))),'RMSE':float(np.sqrt(np.mean(e**2))),
            'WAPE':float(100*np.sum(np.abs(e))/np.sum(np.abs(a))) if np.sum(np.abs(a))>0 else np.nan,
            'sMAPE':float(smape.mean()),'MASE':float(np.nanmean(scaled)) if np.isfinite(scaled).any() else np.nan,
            'Bias':float(e.mean()),'mase_defined_rows':int(np.isfinite(scaled).sum())}

def grouped_metrics(frame,keys):
    rows=[]
    for key,f in frame.groupby(keys,sort=True,dropna=False):
        key=key if isinstance(key,tuple) else (key,)
        rows.append({**dict(zip(keys,key)),**metrics(f)})
    return pd.DataFrame(rows)
