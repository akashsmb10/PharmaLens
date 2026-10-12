"""Explicit contracts are pinned to the audited deployed data manifest."""
import numpy as np
import pandas as pd

class DataError(ValueError): pass

STATUSES={
 'model_status':{'ok','failed'},
 'monitoring_tier':{'High review priority','Moderate review priority','Routine monitoring','Insufficient evidence'},
 'evidence_class':{'Verified descriptive finding','Validated historical model result','Hypothetical scenario','Exploratory signal','Insufficient evidence'},
 'split_type':{'development','holdout'},
}

def validate(frame,contract,name):
    missing=set(contract['columns'])-set(frame.columns)
    if missing: raise DataError(f'{name}: missing required fields: {", ".join(sorted(missing))}')
    keys=contract['keys']
    if frame[keys].isna().any().any() or frame.duplicated(keys).any(): raise DataError(f'{name}: business key must be populated and unique')
    if len(frame)!=contract['rows']: raise DataError(f'{name}: row count differs from validated version')
    for col,dtype in contract['dtypes'].items():
        observed=str(frame[col].dtype)
        if observed!=dtype: raise DataError(f'{name}.{col}: expected {dtype}, found {observed}; no implicit conversion')
        if pd.api.types.is_numeric_dtype(frame[col]) and not pd.api.types.is_bool_dtype(frame[col]):
            values=frame[col].dropna().to_numpy(dtype=float)
            if not np.isfinite(values).all(): raise DataError(f'{name}.{col}: nonfinite numeric values')
    for col,limits in contract.get('dates',{}).items():
        if not pd.api.types.is_datetime64_any_dtype(frame[col]): raise DataError(f'{name}.{col}: date type required')
        valid=frame[col].dropna()
        if not valid.between(pd.Timestamp(limits[0]),pd.Timestamp(limits[1])).all(): raise DataError(f'{name}.{col}: outside validated date range')
    for col in ['prescription_items','historical_items','recent_items','baseline_items','point_forecast','hypothetical_items','actual','prediction','raw_prediction']:
        if col in frame and frame[col].dropna().lt(0).any(): raise DataError(f'{name}.{col}: negative prescription-item count')
    for col in frame:
        if col.endswith('_share_pct') or col.endswith('_score') or col in ['missing_cell_pct','selected_failure_rate_pct','full_window_coverage_pct']:
            if pd.api.types.is_numeric_dtype(frame[col]) and not frame[col].dropna().between(-1e-9,100+1e-9).all(): raise DataError(f'{name}.{col}: expected percentage/score in 0–100 (floating tolerance 1e-9)')
    for col,allowed in STATUSES.items():
        if col in frame and not set(frame[col].dropna())<=allowed: raise DataError(f'{name}.{col}: unsupported status category')
    if 'horizon' in frame and not frame.horizon.isin([1,2,3]).all(): raise DataError(f'{name}: horizon must be 1, 2 or 3 months')
    if 'scenario_id' in frame and not frame.scenario_id.str.match(r'^[A-F]_').all(): raise DataError(f'{name}: invalid audited scenario identifier')
    return frame
