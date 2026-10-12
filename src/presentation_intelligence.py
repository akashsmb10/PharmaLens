"""Exact presentation identifiers and within-extract activity/cost contributions."""
def profiles(features):
    f=features.copy(); f['limitation']='Prescription items only; concentration is not clinical substitution or appropriateness'
    return f,f[['entity_id','presentation_key','presentation_name','items_change','nic_change_gbp','items_change_contribution_pct','nic_change_contribution_pct','nic_per_item_change_pct','evidence_class']].copy(),f[['entity_id','presentation_key','presentation_name','historical_item_share_pct','concentration_hhi','item_growth_pct','missing_cell_pct','forecast_eligible_series','evidence_class']].copy()
