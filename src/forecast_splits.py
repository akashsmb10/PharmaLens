"""Expanding calendar origins; holdout origins cannot predate the frozen development cutoff."""
import pandas as pd

def folds(calendar,cfg,stage):
    calendar=pd.DatetimeIndex(calendar).sort_values()
    if calendar.has_duplicates or not calendar.as_unit('ns').equals(pd.date_range(calendar.min(),calendar.max(),freq='MS')):
        raise ValueError('A unique contiguous monthly calendar is required')
    dev_end=pd.Timestamp(cfg['development_end']); start=pd.Timestamp(cfg['final_holdout_start']); end=pd.Timestamp(cfg['final_holdout_end'])
    rows=[]
    for n in range(cfg['initial_training_months'],len(calendar)):
        origin=calendar[n-1]
        for h in cfg['forecast_horizons']:
            if n-1+h>=len(calendar): continue
            target=calendar[n-1+h]
            valid=target<=dev_end if stage=='development' else origin>=dev_end and start<=target<=end if stage=='holdout' else False
            if valid: rows.append({'split_id':f'{stage}:{origin:%Y-%m}:{h}','split_type':stage,'origin_date':origin,'target_date':target,'horizon':h,'train_observations':n})
    return pd.DataFrame(rows)
