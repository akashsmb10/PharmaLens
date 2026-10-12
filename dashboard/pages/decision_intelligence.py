import streamlit as st
from dashboard.data_loader import load
from dashboard.filters import search
from dashboard.components import plot,table,empty,context
from dashboard.chart_factory import bars,heatmap
from dashboard.evidence import explain,methodology

def render():
    st.header('Decision Intelligence')
    baseline=load('p5/priority_dashboard')
    level=st.selectbox('Monitoring level',sorted(baseline.aggregation_level.unique()),index=list(sorted(baseline.aggregation_level.unique())).index('regional'),key='decision_level')
    f=baseline[baseline.aggregation_level.eq(level)].copy()
    display='region_name' if level=='regional' else 'presentation_name' if level=='presentation' else 'entity_id'
    entities=st.multiselect('Entities in this view',f.entity_id.tolist(),default=f.entity_id.tolist(),format_func=lambda x:f.set_index('entity_id').loc[x,display],key='decision_entities')
    tiers=st.multiselect('Monitoring tiers',sorted(f.monitoring_tier.unique()),default=sorted(f.monitoring_tier.unique()),key='decision_tiers')
    f['risk_filter_label']=f.reliability_class.fillna('Insufficient forecast evidence')
    risks=st.multiselect('Observed forecast risk category',sorted(f.risk_filter_label.unique()),default=sorted(f.risk_filter_label.unique()),key='decision_risk')
    f=f[f.entity_id.isin(entities)&f.monitoring_tier.isin(tiers)&f.risk_filter_label.isin(risks)]
    context(level+'; fixed 2023–2025 Phase 5 baseline; displayed subset does not recompute ranks')
    st.caption('Baseline weights: '+(f.weight_configuration.iloc[0] if len(f) else 'See decision framework')+'. Scores prioritize analytical monitoring, not sales opportunity.')
    unstable=load('p5/priority_rank_instability'); u=unstable[unstable.aggregation_level.eq(level)&unstable.entity_id.isin(f.entity_id)]
    if u.unstable_rank.any(): st.warning(f'{u.unstable_rank.sum()} displayed ranks are policy-sensitive under documented alternatives.')
    if empty(f): return
    scored=f[f.rank_eligible].sort_values(['rank','entity_id']); missing=f[~f.rank_eligible]
    if len(scored):
        plot(bars(scored,display,'composite_score','Validated baseline monitoring scores · original cohort ranks','Score (0–100)'),'decision_scores')
        table(scored,'filtered scored priorities','decision_scored')
        components=scored.set_index(display)[[x+'_score' for x in ['activity','change','cost','forecast','quality']]]
        plot(heatmap(components,'Retained review dimensions','Score'),'decision_components')
    if len(missing):
        st.info('Not scored — insufficient required forecast evidence or another required component. Unscored does not mean zero performance.')
        table(missing,'unscored selected entities','decision_unscored')
    st.subheader('Validated precomputed policy alternatives')
    sensitivity=load('p5/priority_sensitivity_results')
    # Keep required forecast evidence: do not promote unavailable series by dropping that dimension.
    sensitivity=sensitivity[sensitivity.aggregation_level.eq(level)&sensitivity.scheme.isin(['default','equal','activity_heavy','forecast_heavy','quality_heavy'])]
    options=sensitivity[['scheme','normalization']].drop_duplicates().apply(lambda r:r.scheme+' / '+r.normalization,axis=1).tolist()
    option=st.selectbox('Alternative policy',options,key='decision_policy'); scheme,norm=option.split(' / ')
    alt=sensitivity[sensitivity.scheme.eq(scheme)&sensitivity.normalization.eq(norm)&sensitivity.entity_id.isin(f.entity_id)]
    st.caption('Precomputed Phase 5 scenario; every dimension remains required. No baseline file is overwritten. Missing-forecast presentations remain unscored.')
    table(alt,'filtered policy sensitivity','decision_alternative')
    st.subheader('Searchable proposed-investigation register')
    rec=load('p5/recommendations_dashboard'); rec=rec[rec.scope.isin(f.entity_id)]
    priorities=sorted(rec.priority.unique()); classes=sorted(rec.evidence_class.unique())
    investigation_priority=st.multiselect('Investigation priorities',priorities,default=priorities,key='decision_rec_priority')
    evidence=st.multiselect('Investigation evidence categories',classes,default=classes,key='decision_evidence')
    rec=rec[rec.priority.isin(investigation_priority)&rec.evidence_class.isin(evidence)]
    query=st.text_input('Search proposed investigations',key='decision_search')
    rec=search(rec,query,['scope','triggering_metric','recommended_investigation','supporting_evidence'])
    table(rec,'filtered proposed investigations','decision_recommendations')
    if len(rec):
        selected=st.selectbox('Inspect recommendation evidence',rec.recommendation_id.tolist(),key='decision_rec')
        r=rec[rec.recommendation_id.eq(selected)].iloc[0]
        with st.expander('Recommendation source and decision rule',expanded=False):
            st.write(r.supporting_evidence); st.write(r.decision_rule); st.write(r.limitation)
            source=load('p5/'+r.source_output); row=source[source[r.source_key].astype(str).eq(r.source_key_value)]
            st.dataframe(row,hide_index=True,use_container_width=True)
    explain('Validated Phase 5 priority_dashboard, priority_sensitivity_results and recommendations_dashboard','Fixed Phase 5 2023–2025 history and Jul–Dec 2025 model evidence',
        'Stored percentile components, configured weighted composite and original cohort ranks. Precomputed alternatives use exact Phase 5 rules; missing required dimensions stay unscored.',
        'Exploratory signal','Weights/thresholds are illustrative policy assumptions. Recommendations are proposed analyst investigations, not observed actions or benefits.')
    methodology(['PHASE5_DECISION_FRAMEWORK.md'])
