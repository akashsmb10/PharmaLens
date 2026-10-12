"""Traceable deterministic analyst actions, with no invented impact estimates."""
import pandas as pd

FEATURE_TABLES={'regional':'regional_decision_features','presentation':'presentation_decision_features',
                'region_presentation':'region_presentation_decision_features','national':'national_decision_summary'}

def recommendations(features,profiles,priorities,instability,hierarchy,cfg):
    records=[]
    def add(scope,metric,value,period,rule,source,key,key_value,action,benefit,limitation,evidence,priority):
        records.append({'recommendation_id':f'REC{len(records)+1:04d}','scope':scope,'triggering_metric':metric,
                        'observed_value':str(value),'observed_numeric_value':float(value) if isinstance(value,(int,float)) else float('nan'),'comparison_period':period,'decision_rule':rule,
                        'supporting_evidence':f'{source}: {key}={key_value}; {metric}={value}',
                        'recommended_investigation':action,'expected_analytical_benefit':benefit,
                        'limitation':limitation,'confidence_classification':evidence,'evidence_class':evidence,
                        'priority':priority,'source_output':source,'source_key':key,'source_key_value':str(key_value)})
    for level,f in features.items():
        for r in f.to_dict('records'):
            common=(r['entity_id'],FEATURE_TABLES[level],'entity_id',r['entity_id'])
            rules=[('nic_per_item_change_pct',cfg['cost_change_review_pct'],'Inspect dated basic-price, quantity-per-item and coding records','Clarify the accounting mechanism of the ratio change'),
                   ('item_growth_pct',cfg['item_growth_review_pct'],'Review comparable calendar totals and contributing presentations','Identify observed activity drivers')]
            for metric,threshold,action,benefit in rules:
                if pd.notna(r[metric]) and abs(r[metric])>=threshold:
                    add(common[0],metric,r[metric],'2025 versus 2024',f'absolute value >= {threshold}%',common[1],common[2],common[3],action,benefit,
                        'Descriptive change, no causal or clinical explanation established','Verified descriptive finding','High review priority')
            if r['missing_cells']>0:
                add(common[0],'missing_cells',r['missing_cells'],'January 2023–December 2025','missing_cells > 0',common[1],common[2],common[3],
                    'Inspect source coverage and applicability before interpreting absent activity','Resolve coverage ambiguity',
                    'An absent record is not an observed zero or confirmed data error','Verified descriptive finding','High review priority')
    for r in profiles.to_dict('records'):
        if r['manual_review']:
            add(r['series_id'],'holdout_MASE',r['holdout_MASE'],'July–December 2025','manual_review: high relative error, MASE >= 1, absolute bias >= policy, or missing forecasts',
                'forecast_reliability_profiles','series_id',r['series_id'],'Review horizon errors and persistent bias; compare naive on paired support; reassess on new observations',
                'Identify limitations before planning use','Overlapping short historical evaluation, unavailable intervals; do not reselect on this holdout',
                'Validated historical model result','High review priority')
    for level,f in priorities.items():
        for r in f[f.monitoring_tier.eq('High review priority')].to_dict('records'):
            add(r['entity_id'],'composite_score',r['composite_score'],'Historical cutoffs through December 2025',f'score >= {cfg["high_priority"]}',
                level+'_priority_scores','entity_id',r['entity_id'],'Review component scores and ranking sensitivity before assigning analyst time',
                'Make monitoring allocation transparent','Illustrative policy weights; not commercial opportunity or validated benefit','Exploratory signal','High review priority')
    for r in instability[instability.unstable_rank].to_dict('records'):
        add(r['entity_id'],'max_absolute_rank_change',r['max_absolute_rank_change'],'Documented weighting/normalization alternatives',
            'max rank change >= configured fraction of scored cohort','priority_rank_instability','entity_id',r['entity_id'],
            'Compare alternative priorities and component evidence before relying on the rank','Avoid policy-sensitive ranking decisions',
            'Sensitivity is not probabilistic uncertainty','Exploratory signal','Moderate review priority')
    # One explicit planning limitation is traceable to the selected national profile.
    n=profiles[profiles.series_id.eq('England')].iloc[0]
    add('England','interval_status',n.interval_status,'January–March 2026 retrospective forecasts','interval_status starts unavailable',
        'forecast_reliability_profiles','series_id','England','Show unsupported interval status; manually stress-test planning assumptions',
        'Prevent false precision in point-forecast planning','Stress tests are hypothetical and do not provide interval coverage','Validated historical model result','High review priority')
    r=pd.DataFrame(records)
    actions=r.copy(); actions['action_status']='Proposed investigation; no action or outcome observed'
    return r,actions

def evidence_register(tables,cfg):
    rows=[]
    for name,frame in tables.items():
        if 'evidence_class' not in frame: continue
        for evidence,n in frame.evidence_class.value_counts(dropna=False).items():
            if evidence not in cfg['evidence_classes']: raise ValueError('Unknown evidence class')
            rows.append({'output_table':name,'evidence_class':evidence,'rows':int(n),
                         'interpretation':'Traceable observations/model errors, explicit assumptions, or policy-dependent signals; no numerical confidence probability'})
    return pd.DataFrame(rows)
