"""Regional activity/change/risk profiles, without population or efficiency inference."""
def profiles(features):
    f=features.copy()
    f['activity_dimension']='Observed within-extract prescribing volume/share'
    f['change_dimension']='2025 versus 2024 complete monthly aggregate comparison'
    f['forecast_dimension']='Frozen selected-model historical errors; intervals unavailable'
    f['quality_dimension']='Grid absences of unknown applicability and original extreme flags'
    f['limitation']='No population or case-mix adjustment; size and NIC/item do not measure healthcare performance'
    return f,f[['entity_id','region_code','region_name','item_growth_pct','holdout_MASE','holdout_WAPE','bias_pct','missing_cell_pct','evidence_class']].copy()
