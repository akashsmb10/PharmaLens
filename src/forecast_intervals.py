"""Development-only empirical intervals, explicitly unavailable with insufficient residuals."""
import numpy as np
import pandas as pd

def calibrate(development_selected,cfg):
    if not development_selected.split_type.eq('development').all(): raise ValueError('Holdout cannot calibrate intervals')
    rows=[]
    for (sid,h),f in development_selected.groupby(['series_id','horizon'],sort=True):
        residual=(f.actual-f.prediction).dropna(); n=len(residual)
        status='experimental empirical residual; overlapping origins, no coverage guarantee' if n>=cfg['minimum_interval_residuals'] else 'unavailable: insufficient development residuals'
        row={'series_id':sid,'horizon':h,'calibration_n':n,'calibration_source':'development only','interval_status':status}
        for level in cfg['interval_levels']:
            tag=int(level*100)
            row[f'radius_{tag}']=float(np.quantile(np.abs(residual),level,method='higher')) if n>=cfg['minimum_interval_residuals'] else np.nan
        rows.append(row)
    return pd.DataFrame(rows)

def add_intervals(predictions,calibration):
    out=predictions.merge(calibration,on=['series_id','horizon'],how='left',validate='many_to_one')
    for tag in [80,95]:
        out[f'lower_{tag}']=(out.prediction-out[f'radius_{tag}']).clip(lower=0)
        out[f'upper_{tag}']=out.prediction+out[f'radius_{tag}']
    return out

def coverage(frame,keys=['aggregation_level','horizon']):
    rows=[]
    for key,f in frame.groupby(keys,sort=True):
        key=key if isinstance(key,tuple) else (key,)
        for tag in [80,95]:
            valid=f.dropna(subset=[f'lower_{tag}',f'upper_{tag}','actual'])
            rows.append({**dict(zip(keys,key)),'nominal_level':tag,'forecast_rows':len(f),'interval_rows':len(valid),
                         'empirical_coverage_pct':100*((valid.actual>=valid[f'lower_{tag}'])&(valid.actual<=valid[f'upper_{tag}'])).mean() if len(valid) else np.nan,
                         'mean_width':(valid[f'upper_{tag}']-valid[f'lower_{tag}']).mean() if len(valid) else np.nan,
                         'status':'empirical coverage, overlapping errors' if len(valid) else 'unavailable: insufficient development calibration'})
    return pd.DataFrame(rows)
