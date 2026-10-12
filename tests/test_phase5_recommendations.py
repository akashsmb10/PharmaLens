import pandas as pd

def test_recommendation_sources_are_unique_and_match(phase5_tables):
    for r in phase5_tables['executive_recommendations'].itertuples():
        f=phase5_tables[r.source_output]; row=f[f[r.source_key].astype(str).eq(r.source_key_value)]
        assert len(row)==1 and str(row[r.triggering_metric].iloc[0])==r.observed_value
        assert r.decision_rule and r.recommended_investigation and r.limitation

def test_evidence_classes_and_no_confidence_probabilities(phase5_tables,phase5_cfg):
    for name,f in phase5_tables.items():
        if 'evidence_class' in f: assert f.evidence_class.isin(phase5_cfg['evidence_classes']).all(),name
    assert 'confidence_probability' not in phase5_tables['executive_recommendations']

def test_no_unsupported_financial_or_clinical_actions(phase5_tables):
    actions=phase5_tables['executive_recommendations'].recommended_investigation.str.lower()
    for forbidden in ['increase sales','sales-force investment','change patient treatment','reduce prescribing','cut marketing','change manufacturer prices','realized savings','revenue opportunity']:
        assert not actions.str.contains(forbidden,regex=False).any()

def test_actions_are_proposed_not_outcomes(phase5_tables):
    f=phase5_tables['decision_action_register']; assert f.action_status.eq('Proposed investigation; no action or outcome observed').all()
    assert f.recommendation_id.is_unique and set(f.recommendation_id)==set(phase5_tables['executive_recommendations'].recommendation_id)
