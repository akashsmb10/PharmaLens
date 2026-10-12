"""Validated historical inputs, explicit calendar coverage, and unique decision grains."""
import json
import numpy as np
import pandas as pd
from .common import ROOT,sha256
from .forecast_data import protected_snapshot as prior_snapshot

LEVEL_KEYS={'regional':['region_code'], 'presentation':['presentation_key'],
            'region_presentation':['region_code','presentation_key'], 'national':[]}

def configuration(root=ROOT):
    cfg=json.loads((root/'config/decision_intelligence.yaml').read_text(encoding='utf-8'))
    validate_weights(cfg['weights'])
    if not 0<=cfg['moderate_priority']<cfg['high_priority']<=100: raise ValueError('Invalid tiers')
    if any(x<=-100 for x in cfg['scenario_changes_pct']): raise ValueError('Invalid scenario change')
    return cfg

def validate_weights(weights):
    if not weights or any(not np.isfinite(v) or v<0 for v in weights.values()) or not np.isclose(sum(weights.values()),1,atol=1e-12,rtol=0):
        raise ValueError('Weights must be nonnegative and sum to one')

def protected_snapshot(root=ROOT):
    result={k:v for k,v in prior_snapshot(root).items() if not k.startswith('docs/PHASE5_')}
    for directory,pattern in [('outputs/phase4/tables','*'),('outputs/phase4/charts','*.png'),
                              ('outputs/phase4/models','*.json'),('outputs/phase4/validation','*.json'),
                              ('outputs/phase4/validation','*.xml'),('docs','PHASE4*.md'),
                              ('notebooks','0[45]*.ipynb'),('config','forecasting.yaml')]:
        for p in (root/directory).glob(pattern):
            if p.is_file(): result[str(p.relative_to(root)).replace('\\','/')]=sha256(p)
    return dict(sorted(result.items()))

def load_inputs(root=ROOT):
    audit=json.loads((root/'outputs/phase4/validation/final_audit.json').read_text(encoding='utf-8'))
    if not audit['passed'] or audit['tests']['failures'] or audit['independent_failed_checks']:
        raise ValueError('Phase 4 audit is not passed')
    for name,item in audit['exports'].items():
        for extension in ['csv','parquet']:
            if sha256(root/f'outputs/phase4/tables/{name}.{extension}')!=item[f'{extension}_sha256']:
                raise AssertionError('Frozen Phase 4 output changed: '+name)
    frozen=root/'outputs/phase4/validation/frozen_development_decisions.json'
    if sha256(frozen)!=audit['frozen_decisions_sha256']: raise AssertionError('Frozen selection changed')
    from .forecast_data import load_forecasting_data
    from .forecast_config import configuration as fc
    load_forecasting_data(fc(root),root) # Reuse verified Phase 2/3 SQL and hash controls.
    inputs={}
    for phase,directory in [('p2','outputs/tables'),('p3','outputs/phase3/tables'),('p4','outputs/phase4/tables')]:
        for p in sorted((root/directory).glob('*.parquet')): inputs[f'{phase}/{p.stem}']=pd.read_parquet(p)
    return inputs

def join_unique(left,right,on):
    if right.duplicated(on).any(): raise ValueError('Right grain is not unique')
    result=left.merge(right,on=on,how='left',validate='many_to_one')
    if len(result)!=len(left): raise AssertionError('Join multiplication')
    return result

def coverage_grid(inputs):
    # The Phase 2 missing-series export contains absent cells only. Its union
    # with observed analytical rows reproduces the existing diagnostic spine.
    observed=inputs['p2/cost_analytics'].assign(is_observed=True)
    absent=inputs['p2/missing_series_months']
    if absent.is_observed.any(): raise AssertionError('Expected absence-only export')
    grid=pd.concat([observed,absent],ignore_index=True)
    if grid.duplicated(['month','region_code','presentation_key']).any(): raise AssertionError('Coverage grain duplicates')
    return grid

def historical_features(inputs,cfg):
    fact=inputs['p2/cost_analytics'].copy()
    fact=fact[fact.month.between(pd.Timestamp(cfg['historical_start']),pd.Timestamp(cfg['historical_end']))]
    # Canonical nullable-compatible arithmetic dtype after the cutoff: a future
    # source row must not alter even the schema of historical feature outputs.
    fact['prescription_items']=fact.prescription_items.astype('float64')
    grid=coverage_grid(inputs)
    grid=grid[grid.month.between(pd.Timestamp(cfg['historical_start']),pd.Timestamp(cfg['historical_end']))]
    flags=inputs['p2/extreme_value_review']; eligibility=inputs['p4/series_eligibility']
    flags=flags[flags.month.between(pd.Timestamp(cfg['historical_start']),pd.Timestamp(cfg['historical_end']))]
    anomalies=inputs['p3/anomaly_diagnostics']
    anomalies=anomalies[anomalies.month.between(pd.Timestamp(cfg['historical_start']),pd.Timestamp(cfg['historical_end']))]
    total_items=fact.prescription_items.sum(); total_cost=fact.net_ingredient_cost_gbp.sum()
    rows={}
    for level,keys in LEVEL_KEYS.items():
        identity=grid[keys].drop_duplicates().sort_values(keys) if keys else pd.DataFrame([{}])
        output=[]
        for identity_row in (identity.to_dict('records') if keys else [{}]):
            f=fact; g=grid; a=flags; diagnostic=anomalies
            for k,v in identity_row.items(): f=f[f[k].eq(v)]; g=g[g[k].eq(v)]; a=a[a[k].eq(v)]; diagnostic=diagnostic[diagnostic[k].eq(v)]
            monthly=f.groupby('month')[['prescription_items','net_ingredient_cost_gbp']].sum(min_count=1)
            monthly=monthly.reindex(pd.date_range(cfg['historical_start'],cfg['historical_end'],freq='MS'))
            annual={}
            for year in [cfg['baseline_year'],cfg['recent_year']]:
                part=monthly[monthly.index.year==year]
                annual[year]={'items':part.prescription_items.sum(min_count=1),'cost':part.net_ingredient_cost_gbp.sum(min_count=1),'n':int(part.prescription_items.notna().sum())}
            old,new=annual[cfg['baseline_year']],annual[cfg['recent_year']]
            items=monthly.prescription_items.sum(min_count=1); cost=monthly.net_ingredient_cost_gbp.sum(min_count=1)
            ratio=lambda c,i:c/i if pd.notna(i) and i>0 else np.nan
            growth=lambda n,o:100*(n/o-1) if pd.notna(o) and o>0 and old['n']==new['n']==12 else np.nan
            current_ratio=ratio(new['cost'],new['items']); prior_ratio=ratio(old['cost'],old['items'])
            detail=f.groupby('presentation_key' if level in ['national','regional'] else 'region_code').prescription_items.sum()
            concentration=float(((detail/detail.sum())**2).sum()) if len(detail) and detail.sum()>0 else np.nan
            sid='England' if level=='national' else str(identity_row['region_code']) if level=='regional' else str(identity_row['presentation_key']) if level=='presentation' else identity_row['region_code']+'::'+identity_row['presentation_key']
            row={'entity_id':sid,'aggregation_level':level,**identity_row,
                 'historical_start':pd.Timestamp(cfg['historical_start']),'historical_end':pd.Timestamp(cfg['historical_end']),
                 'baseline_year':cfg['baseline_year'],'recent_year':cfg['recent_year'],
                 'historical_items':items,'historical_nic_gbp':cost,'historical_nic_per_item_gbp':ratio(cost,items),
                 'recent_items':new['items'],'recent_nic_gbp':new['cost'],'baseline_items':old['items'],'baseline_nic_gbp':old['cost'],
                 'recent_nic_per_item_gbp':current_ratio,'baseline_nic_per_item_gbp':prior_ratio,
                 'item_growth_pct':growth(new['items'],old['items']),'nic_growth_pct':growth(new['cost'],old['cost']),
                 'nic_per_item_change_pct':growth(current_ratio,prior_ratio),
                 'items_change':new['items']-old['items'] if old['n']==new['n']==12 else np.nan,
                 'nic_change_gbp':new['cost']-old['cost'] if old['n']==new['n']==12 else np.nan,
                 'historical_item_share_pct':100*items/total_items,'historical_nic_share_pct':100*cost/total_cost,
                 'monthly_items_cv':monthly.prescription_items.std(ddof=1)/monthly.prescription_items.mean() if monthly.prescription_items.mean()>0 else np.nan,
                 'concentration_hhi':concentration,'monthly_observations':int(monthly.prescription_items.notna().sum()),
                 'observed_cells':int(g.is_observed.sum()),'expected_cells':len(g),
                 'missing_cells':int((~g.is_observed).sum()),'missing_cell_pct':100*(~g.is_observed).mean(),
                 'extreme_flags':len(a),'flagged_cells':len(a[['month','region_code','presentation_key']].drop_duplicates()),
                 'phase3_union_flags':len(diagnostic),
                 'potential_structural_shift_flags':int(diagnostic.classification.eq('Potential structural shift').sum()),
                 'unusual_plausible_flags':int(diagnostic.classification.eq('Unusual but plausible activity').sum()),
                 'insufficient_anomaly_evidence_flags':int(diagnostic.classification.eq('Insufficient evidence').sum()),
                 'extreme_flags_per_1000_observed_cells':1000*len(a)/g.is_observed.sum() if g.is_observed.sum()>0 else np.nan,
                 'evidence_class':'Verified descriptive finding',
                 'coverage_interpretation':'Absent cells have unknown activity/applicability; observed sums are not imputed population totals'}
            for name in ['region_name','presentation_name','presentation_code','unit_of_measure']:
                if name in g and (name.startswith('region') and 'region_code' in keys or not name.startswith('region') and 'presentation_key' in keys): row[name]=g[name].iloc[0]
            if level=='presentation':
                e=eligibility[eligibility.presentation_key.eq(identity_row['presentation_key']) & eligibility.aggregation_level.eq('region_presentation')]
                row['forecast_eligible_series']=int(e.eligible.sum()); row['forecast_eligible']=bool(e.eligible.any())
            else:
                e=eligibility[eligibility.series_id.eq(sid)]
                row['forecast_eligible']=bool(len(e) and e.eligible.iloc[0]); row['forecast_eligible_series']=int(row['forecast_eligible'])
            output.append(row)
        rows[level]=pd.DataFrame(output)
    national_delta=rows['national'].iloc[0]
    for f in rows.values():
        f['items_change_contribution_pct']=100*f.items_change/national_delta.items_change if national_delta.items_change!=0 else np.nan
        f['nic_change_contribution_pct']=100*f.nic_change_gbp/national_delta.nic_change_gbp if national_delta.nic_change_gbp!=0 else np.nan
    return rows

def enrich_forecasts(features,profiles,op,hierarchy):
    result={}
    metrics=['selected_model','selected_variant','holdout_n','holdout_MAE','holdout_RMSE','holdout_MASE','holdout_WAPE','holdout_Bias','bias_pct','development_MASE','selected_failure_count','selected_failure_rate_pct','all_family_failure_count','interval_status','reliability_class']
    for level,f in features.items():
        if level!='presentation':
            right=profiles[['series_id']+metrics].rename(columns={'series_id':'entity_id'})
        else:
            e=profiles[profiles.aggregation_level.eq('region_presentation')].copy()
            numeric=[k for k in metrics if k in e and pd.api.types.is_numeric_dtype(e[k])]
            right=e.groupby('presentation_key')[numeric].mean().reset_index().rename(columns={'presentation_key':'entity_id'})
            names=e.groupby('presentation_key')[['selected_model','selected_variant']].agg(lambda s:';'.join(sorted(set(s)))).reset_index().rename(columns={'presentation_key':'entity_id'})
            right=join_unique(right,names,['entity_id'])
            right['interval_status']='unavailable: insufficient development residuals'
            right['reliability_class']='Eligible regional subset only; not a national presentation forecast'
        f=join_unique(f,right,['entity_id'])
        f['forecast_metric_scope']='Own selected series' if level!='presentation' else 'Equal-series mean over eligible region/presentation subset; not all regions'
        sums=op.groupby('series_id').point_forecast.sum(min_count=3).rename('retrospective_jan_mar_2026_items').reset_index().rename(columns={'series_id':'entity_id'})
        if level!='presentation': f=join_unique(f,sums,['entity_id'])
        else: f['retrospective_jan_mar_2026_items']=np.nan
        f['hierarchy_mean_abs_gap_pct']=hierarchy[hierarchy.context.eq('operational')].absolute_gap_pct.mean() if level in ['national','regional'] else np.nan
        result[level]=f
    return result

def dictionary(features):
    formulas={
      'entity_id':'England, region_code, presentation_key, or region_code::presentation_key by grain',
      'aggregation_level':'Explicit national/regional/presentation/region_presentation grain label',
      'historical_items':'Sum observed prescription_items over configured historical window; null if no observations',
      'historical_nic_gbp':'Sum observed net_ingredient_cost_gbp over configured historical window; null if no observations',
      'historical_nic_per_item_gbp':'Historical NIC / historical items if items > 0',
      'recent_items':'Sum observed items in configured recent calendar year',
      'recent_nic_gbp':'Sum observed NIC in configured recent calendar year',
      'baseline_items':'Sum observed items in configured baseline calendar year',
      'baseline_nic_gbp':'Sum observed NIC in configured baseline calendar year',
      'recent_nic_per_item_gbp':'Recent-year sum NIC / sum items, positive denominator required',
      'baseline_nic_per_item_gbp':'Baseline-year sum NIC / sum items, positive denominator required',
      'item_growth_pct':'100*(recent items / baseline items - 1); both years require 12 observed aggregate months and positive baseline',
      'nic_growth_pct':'100*(recent NIC / baseline NIC - 1); both years require 12 observed aggregate months and positive baseline',
      'nic_per_item_change_pct':'100*(recent weighted NIC/item / baseline weighted NIC/item - 1); same complete-year/positive-baseline rule',
      'items_change':'Recent items - baseline items; both years require 12 aggregate observed months',
      'nic_change_gbp':'Recent NIC - baseline NIC; both years require 12 aggregate observed months',
      'historical_item_share_pct':'100*entity observed historical items / national observed historical items',
      'historical_nic_share_pct':'100*entity observed historical NIC / national observed historical NIC',
      'monthly_items_cv':'Sample SD of observed monthly items / observed monthly mean; includes trend',
      'concentration_hhi':'Sum squared observed historical presentation shares for region/national; regional shares for presentation/region_presentation',
      'monthly_observations':'Count non-null aggregate monthly item observations in historical calendar',
      'observed_cells':'Count is_observed True in union of observed and absence-only region/presentation/month cells',
      'expected_cells':'Number of cells in the entity diagnostic calendar, including never-observed applicability-unknown cells',
      'missing_cells':'Count is_observed False in entity diagnostic calendar',
      'missing_cell_pct':'100*missing cells / expected diagnostic cells',
      'extreme_flags':'Count original Phase 2 region/presentation/month/metric flags within entity',
      'flagged_cells':'Count distinct month/region/presentation tuples among original extreme flags',
      'extreme_flags_per_1000_observed_cells':'1000*original extreme metric flags / observed cells; null if zero observed cells',
      'phase3_union_flags':'Count Phase 3 anomaly_diagnostics union rows within entity',
      'potential_structural_shift_flags':'Count Phase 3 diagnostic rows classified Potential structural shift',
      'unusual_plausible_flags':'Count Phase 3 diagnostic rows classified Unusual but plausible activity',
      'insufficient_anomaly_evidence_flags':'Count Phase 3 diagnostic rows classified Insufficient evidence',
      'forecast_eligible':'Frozen Phase 4 series_eligibility.eligible; presentation=True when any eligible regional subset exists',
      'forecast_eligible_series':'Count eligible frozen series in entity; presentation sums across its regions',
      'items_change_contribution_pct':'100*entity items change / national net items change; null if national change zero',
      'nic_change_contribution_pct':'100*entity NIC change / national net NIC change; null if national change zero',
      'holdout_n':'Count successful selected-model holdout origin/horizon cells; presentation uses equal-series mean count',
      'holdout_MAE':'Mean absolute selected-model error over successful holdout forecast cells; presentation equal-series mean',
      'holdout_RMSE':'Square root mean squared selected-model holdout error; presentation equal-series mean, not pooled RMSE',
      'holdout_MASE':'Mean absolute error / each forecast origin training-prefix naive scale; presentation equal-series mean',
      'holdout_WAPE':'100*sum absolute selected-model holdout errors / sum absolute actuals; presentation equal-series mean, not pooled WAPE',
      'holdout_Bias':'Mean selected-model prediction minus actual in holdout; presentation equal-series mean',
      'bias_pct':'100*mean selected-model error / mean actual over successful holdout cells; presentation equal-series mean',
      'development_MASE':'Mean selected-model development scaled absolute errors; presentation equal-series mean',
      'selected_failure_count':'Count failed selected-model holdout forecast rows; presentation mean over eligible regional subset',
      'selected_failure_rate_pct':'100*selected failure count / attempted selected-model holdout cells; presentation equal-series mean',
      'all_family_failure_count':'Count all failed family/configuration forecast rows in both development and holdout; presentation equal-series mean',
      'selected_model':'Frozen Phase 4 selected model family; presentation joins unique eligible-subset model names',
      'selected_variant':'Frozen Phase 4 selected model/hyperparameter variant; presentation joins eligible-subset variant names',
      'retrospective_jan_mar_2026_items':'Sum three frozen operational monthly point forecasts for own series, requiring three nonnull values; presentation null',
      'hierarchy_mean_abs_gap_pct':'Mean operational absolute (sum seven regions - direct national) / direct national *100; common national-system indicator attached only to national/regions',
      'interval_status':'Frozen development interval-calibration availability label; missing or unsupported stays explicit',
      'reliability_class':'Within-level relative MASE classification with minimum evaluation support; presentation label discloses subset scope',
      'forecast_metric_scope':'Own selected series, or disclosed equal-series eligible regional presentation subset',
      'coverage_interpretation':'Explicit unknown applicability/undercoverage label; not an imputation or error classification',
      'evidence_class':'Verified descriptive finding for mixed-source feature products; forecast field classes recorded separately here',
    }
    rows=[]
    for level,f in features.items():
        for col in f:
            forecast=any(x in col for x in ['forecast','holdout','development','selected','bias','interval','reliability','retrospective','hierarchy'])
            source='Phase 4 selected prediction rows, frozen decisions and operational forecasts' if forecast else 'Phase 2 cost_analytics and missing_series_months; extreme_value_review'
            calculation=formulas.get(col,'Configured period label' if col in ['historical_start','historical_end','baseline_year','recent_year'] else 'Exact source dimensional identifier/name/native unit; no transformation')
            if col in ['phase3_union_flags','potential_structural_shift_flags','unusual_plausible_flags','insufficient_anomaly_evidence_flags']: source='Phase 3 anomaly_diagnostics, aggregated explicitly by entity'
            rows.append({'feature':col,'grain':level,'source_table':source,'business_definition':col.replace('_',' '),
                         'calculation':calculation,'period':'2023–2025 history; 2025 vs 2024 change; Jul–Dec 2025 holdout; Jan–Mar 2026 retrospective',
                         'missingness_behavior':'Null if undefined, missing forecast, or incomplete annual comparison; no zero filling',
                         'limitations':'Observed extract only; coverage includes unknown applicability; forecast subset and overlapping short evaluation',
                         'evidence_class':'Verified descriptive finding' if not forecast else 'Validated historical model result'})
    return pd.DataFrame(rows)
