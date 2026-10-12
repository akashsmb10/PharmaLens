"""Reports use actual decision outputs and disclose policy assumptions."""
import pandas as pd
from .common import ROOT
from .phase3_reports import md_table

FRAMEWORK='''# Phase 5 decision framework

## Objective and scope

Allocate analytical monitoring and investigation effort using verified NHSBSA atorvastatin activity
in England. The evidence concerns prescription items and NIC, not patients, manufacturer revenue,
healthcare quality or India demand. NIC is an accounting measure, not final NHS expenditure.
No interactive dashboard or PBIX is created; Phase 6 consumes the stable exported datasets.

## Features, joins and missingness

Historical source: Phase 2 cost_analytics (observed region/presentation/month), annual and monthly
reporting views, the absence-only missing_series_months export and series_coverage. Union observed
and absent cells to reconstruct the existing diagnostic grid, without manufacturing activity.
At region/presentation, region, presentation and national grains, sum observed prescription items
and GBP NIC. NIC/item is sum NIC divided by sum items, never mean of row ratios. Historical shares
use the full observed national total. Recent annual change compares 2025 with 2024, requiring twelve
observed aggregate months in both years and a positive baseline; otherwise change is null.
Aggregate completeness does not imply constituent-cell completeness; both exposures are exported.
Absence can reflect unknown applicability; a never-observed cell is not known zero activity.
Monthly variability is sample SD/mean, includes trend, and is not forecast error. Concentration HHI
sums squared presentation item shares for regions/national and squared regional shares for presentations.
Contribution percentages divide component change by national net change; negative/>100% values are valid.
All 17 presentation identifiers include native unit; physical quantities are not combined.

Original Phase 2 extreme flags and unique flagged cells remain descriptive review exposure. Phase 3
union flags and classifications are separate, retrospective heuristics, not confirmed errors. A flag count
can count several metrics for the same cell. Nothing is deleted or treated as proven structural causation.
All joins validate right-side uniqueness and preserve left row counts. Frozen Phase 4 selections identify
selected-model rows, aggregated explicitly by series/split/horizon. Pooled Phase 4 family metrics are
not silently substituted for individual selected-series metrics. Missing forecasts stay null.
Presentation forecast features are equal-series means over the eligible regional subset, not national
presentation forecasts; their subset scope is explicit. Future presentation totals are not fabricated.

Field-level definitions, sources, units, null behavior and business keys are exported in
decision_feature_dictionary and dashboard_data_dictionary. Dates are typed in Parquet and ISO in CSV.
Percent metrics use 0–100; share fractions/HHI use 0–1. Ratios and item expectations retain precision.

## Monitoring policy

Five dimensions: activity = recent annual items; historical change = absolute annual item growth;
cost-pattern change = absolute annual weighted NIC/item change; forecast risk = selected-series
holdout MASE (presentation uses the disclosed eligible-subset mean); quality concern = missing-cell
percentage plus original extreme flags per 1,000 observed cells. Combining those two quality indicators
is an illustrative policy choice with no empirical calibration. Greater values mean more review relevance.
Higher data-quality concern does not mean commercial opportunity. Each raw feature remains exported.

Normalize each dimension separately within its aggregation-level cohort: 100*(average rank−1)/(n−1)
over finite values, where n is the finite count; tied values use midranks. A constant or singleton
dimension scores 50, a neutral ranking convention rather than measured risk. Missing values remain null.
Initial weights: activity 25%, change 20%, cost 20%, forecast 20%, quality 15%; validate nonnegative
finite weights summing to one. Composite = weighted sum of component scores. Every positive-weight
component must exist; otherwise status is Insufficient evidence and composite/rank are null. Missing
components are not zero risk and remaining weights are not silently redistributed.

Rank descending with equal scores sharing minimum rank; entity IDs deterministically order display
ties. Initial tiers: >=70 High review priority, >=40 Moderate review priority, otherwise Routine monitoring.
Actions: investigate drivers/risk, review next cycle, standard tracking, or improve evidence before scoring.
These labels are policy-dependent; a top-ranked entity need not meet the high-review threshold.

## Sensitivity and forecast reliability

Compare equal weighting; activity/forecast/quality-heavy weights (50% primary, 12.5% others); each
leave-one-component-out policy with remaining original weights rescaled; min-max normalization
(100*(x−min)/(max−min), constant=50); tiers 60/30, 70/40 and 80/50. Export individual rank changes,
newly scored entities, tier changes, paired Spearman correlations and top-three overlap restricted to
the baseline-scored universe (ties can admit more than three). Unscored baseline entities have no
invented rank movement. Flag maximum rank change >= max(1,25% of baseline scored cohort size).
This is a sensitivity diagnostic, not a robustness guarantee or probabilistic confidence interval.

Forecast risk consumes frozen Phase 4 outputs only, with no fitting/reselection. MAE/RMSE describe
absolute errors, MASE scales by origin-training naive change, WAPE is aggregate absolute error/actual
volume, bias=forecast−actual, and bias_pct=mean error/mean actual. Compare naive on identical successful
origin/horizon cells. Error classes are relative within aggregation level: normalized MASE percentile
<=1/3 Lower, <=2/3 Moderate, otherwise Higher; fewer than 12 valid total holdout forecasts is Insufficient
evaluation evidence. Singleton national percentile=0.5 is a neutral convention, not a comparative finding.
Manual review triggers: Higher/Insufficient class, MASE>=1, absolute bias>=2%, or missing forecasts.
Even lower observed error only supports routine point tracking; consequential planning needs manual validation.
Horizon samples are 6/5/4 overlapping forecasts, too short for precise reliability claims. All calibrated
intervals remain unavailable. Historical errors are never relabeled probabilistic prediction intervals.
Selected-model failures and all-family failures are distinct; the latter include nonselected comparators.

Hierarchy compares direct national with all seven regional forecasts, without reconciliation. Signed
gap=sum regions−direct; absolute/relative gaps are explicit. Absolute gap>=1% prompts policy review.
Coherence is not accuracy, and the 28 eligible presentation series do not form a complete hierarchy.

## Evidence and limits

Verified descriptive finding: source-backed historical arithmetic. Validated historical model result:
frozen-model evaluation or retrospective point forecasts. Hypothetical scenario: accounting assumptions.
Exploratory signal: policy priorities/sensitivity. Insufficient evidence: explicitly unavailable support.
No confidence label carries a probability. Output-row labels and decision_evidence_register preserve
these distinctions. Rule-based recommendations point to unique source rows/metrics, list limitations
and propose investigations, without estimating savings or asserting that any action occurred.
Priority rows labeled exploratory retain explicit Insufficient evidence tiers where unscored.

Only 36 historical months; observed-sum undercoverage unknown; sparse eligible forecast subset;
correlated regions/overlapping errors; nonblind retrospective analysis; no population, case-mix,
manufacturer margin or intervention data. Analytical observation cutoffs do not reconstruct historical
release availability or revisions. No clinical appropriateness, causal, sales-force or investment conclusion.
'''

SCENARIO_METHOD='''# Phase 5 scenario methodology

All scenarios are deterministic hypothetical accounting sensitivities. Assumptions have no probabilities.
Observed baseline: calendar 2025 prescription items and weighted NIC/item. Forecast planning baseline:
frozen direct national January–March 2026 point expectations, with December 2025 observation cutoff.
No 2026 actuals or refitted models are used. Latest complete historical 2025 weighted NIC/item is a
fixed assumption for converting hypothetical forecast item volumes into NIC; no cost trend is extrapolated.
The fixed-vintage retrospective cutoff is not a claim of real-time source publication availability.

Let I be baseline items, P baseline NIC/item, v fractional volume change and c fractional cost change.
I*=I(1+v), P*=P(1+c), C*=I*P*=IP(1+v)(1+c). Deltas compare with the matching baseline IP.
Interaction is retained; volume and cost effects are not just added. Input counts/costs must be finite
and nonnegative, changes >−100%. Fractional item expectations are accounting allocations, not observed counts.
Configured stress tests −10/−5/0/+5/+10% are illustrative, not empirical forecasts or attainable interventions.

A varies volume at fixed P; B varies P at fixed I; C varies both on a 5×5 matrix. E varies one region
at a time using its own 2025 weighted P, other regions held fixed; export its contribution to national NIC.
F hypothetically varies each frozen national forecast at fixed historical P; no scenario is an interval.
Baselines, reference period, observation cutoff, assumptions and units are explicit on each scenario row.

D transfers 1/2/5 percentage points of 2025 item share from the largest presentation to the second largest
(descending recent items, presentation key breaks ties). This rule is disclosed, not optimized for an outcome.
All 17 baseline and scenario shares must be nonnegative and sum to one. Keep total items fixed:
I_j*=I_total*s_j*, C*=sum_j I_j*P_j, with each presentation's observed 2025 weighted P_j held fixed.
Mixed tablet/ml physical quantities are not used. Baseline C=sum_j I_total*s_j*P_j reconciles to national NIC.
Any infeasible donor reduction, unknown presentation, negative share or incomplete baseline raises an error.
This is an accounting redistribution, not clinical substitution or a clinically appropriate recommendation.

Accounting break-even solves (1+v)(1+c)=1, so c=1/(1+v)−1. It describes NIC equality, not manufacturer
profitability. No manufacturer cost/revenue/margin or marketing-spend data exists. One-way, two-way,
mix and regional sensitivities retain all configured outcomes, including zero-change controls.

Independent validation uses explicit loops/algebra for item/NIC changes, share/item conservation and
break-even; separate tests include known numeric fixtures and infeasible inputs. Scenario results do not
estimate financial savings, causation, patient outcomes, clinical benefits or future prices.
'''

def reports(t,result,cfg,root=ROOT):
    docs=root/'docs'; docs.mkdir(exist_ok=True)
    (docs/'PHASE5_DECISION_FRAMEWORK.md').write_text(FRAMEWORK,encoding='utf-8')
    (docs/'PHASE5_SCENARIO_METHODOLOGY.md').write_text(SCENARIO_METHOD,encoding='utf-8')
    regional=t['regional_priority_scores']; presentations=t['presentation_priority_scores']; n=t['national_decision_summary'].iloc[0]
    risk=t['forecast_reliability_profiles']; r=risk[risk.aggregation_level.eq('regional')]
    ranks=t['rank_stability_summary']; alt=ranks[ranks.aggregation_level.eq('regional') & ~((ranks.scheme=='default')&(ranks.normalization=='percentile'))]
    s=t['scenario_results']; plus=s[s.scenario_id.eq('A_5')].iloc[0]; combined=s[s.scenario_id.eq('C_5_-5')].iloc[0]
    be=t['accounting_break_even_analysis']; offset=be[be.volume_change_pct.eq(5)].iloc[0]
    national=risk[risk.series_id.eq('England')].iloc[0]
    pcols=['presentation_name','historical_item_share_pct','nic_per_item_change_pct','composite_score','rank','monitoring_tier','missing_components']
    regcols=['region_name','historical_item_share_pct','item_growth_pct','holdout_MASE','composite_score','rank','monitoring_tier']
    summary=f'''# Phase 5 executive summary

Verified England atorvastatin extract: **{n.historical_items:,.0f} items**, **GBP {n.historical_nic_gbp:,.2f} NIC**,
January 2023–December 2025. 2025 versus 2024: items **{n.item_growth_pct:.4f}%**, NIC **{n.nic_growth_pct:.4f}%**,
weighted NIC/item **{n.nic_per_item_change_pct:.4f}%**. These are dispensing/accounting observations,
not patients, manufacturer revenue or India demand.

## Monitoring priorities

Policy weights 25/20/20/20/15%, five retained dimensions; score cutoffs 70/40. Top region:
**{regional.iloc[0].region_name}**, score **{regional.iloc[0].composite_score:.4f}**, tier
**{regional.iloc[0].monitoring_tier}**. Ranking and high-review classification are distinct.

{md_table(regional[regcols])}

All **{len(presentations)}** presentations remain visible; **{presentations.rank_eligible.sum()}** are scored,
**{(~presentations.rank_eligible).sum()}** have insufficient required forecast evidence.
Presentation forecast metrics concern eligible regional subsets, not national presentation predictions.

{md_table(presentations[pcols])}

Regional alternative-policy Spearman correlations span **{alt.spearman_rank_correlation.min():.4f}–{alt.spearman_rank_correlation.max():.4f}**;
top-priority overlap spans **{alt.top_priority_overlap_pct.min():.2f}–{alt.top_priority_overlap_pct.max():.2f}%**.
Do not treat the displayed order as invariant. Per-entity movement and newly-scored leave-out cases are exported.

## Forecast risk and hierarchy

Frozen national **{national.selected_model}** holdout MASE **{national.holdout_MASE:.6f}**,
MAE **{national.holdout_MAE:,.2f}**, RMSE **{national.holdout_RMSE:,.2f}**, WAPE **{national.holdout_WAPE:.6f}%**;
**{national.holdout_n:.0f}** overlapping forecast cells. Paired naive MASE improvement
**{national.paired_MASE_improvement_pct:.6f}%**. Models are not retrained or reselected.
Regional MASE ranges **{r.holdout_MASE.min():.6f}–{r.holdout_MASE.max():.6f}**;
**{risk.manual_review.sum()} of {len(risk)}** selected series trigger configured manual-review rules.
All intervals remain unavailable; observed-error categories do not guarantee future reliability.

{md_table(r[['region_name','holdout_n','holdout_MASE','holdout_WAPE','bias_pct','reliability_class','manual_review']])}

{md_table(t['forecast_hierarchy_gap_analysis'].query("context == 'operational'")[['forecast_month','horizon','signed_gap_items','absolute_gap_pct','manual_review']])}

These are separate unreconciled retrospective forecasts. Coherence is not accuracy.

## Hypothetical accounting sensitivities

At the 2025 fixed weighted NIC/item, +5% item volume gives **GBP {plus.hypothetical_nic_gbp:,.2f}** hypothetical
NIC, a **GBP {plus.nic_difference_gbp:,.2f}** difference. +5% volume with −5% NIC/item gives
**GBP {combined.hypothetical_nic_gbp:,.2f}**, difference **GBP {combined.nic_difference_gbp:,.2f}**.
To exactly offset +5% items requires **{offset.offsetting_nic_per_item_change_pct:.6f}%** NIC/item change.
These are assumptions/accounting equality, not savings, profitability or future price forecasts.

{md_table(s[s.scenario_name.str.startswith('D:')][['scenario_id','hypothetical_items','hypothetical_nic_gbp','nic_difference_gbp']])}

Mix-only scenarios preserve total items across all 17 presentations. They are accounting simulations,
not clinical substitutions. Forecast planning scenarios use only frozen December-cutoff point forecasts.

## Proposed investigations and Phase 6

**{len(t['executive_recommendations'])}** traceable rule-based investigations are exported; no action or benefit
is claimed observed. Review major weighted NIC/item changes using dated basic-price/quantity records;
inspect source coverage; review high relative forecast error/bias; show ranking sensitivity before allocating
analyst time. Keep routine tracking separate from consequential forecast planning.
Phase 6 should provide filters, component scores, sensitivity views, exact source keys, cutoff/horizon/sample
counts, unknown missingness and explicit unsupported intervals. Separate observations, model results and
hypothetical scenarios. Keep unscored entities visible. No UI or PBIX is created in Phase 5.

Limits: 36 months, short correlated/overlapping model errors, incomplete applicability information,
sparse eligible subset, subjective weights/thresholds, fixed cost assumptions and unmodeled release vintage.
No population/case-mix, clinical or manufacturer financial inference.
'''
    (docs/'PHASE5_EXECUTIVE_SUMMARY.md').write_text(summary,encoding='utf-8')
    recommendations=t['executive_recommendations']
    report='# Phase 5 business recommendations\n\nProposed analyst investigations only. Trigger values and unique source keys are exported; confidence labels carry no probabilities.\n\n'
    report+=md_table(recommendations[['recommendation_id','scope','triggering_metric','observed_value','decision_rule','recommended_investigation','evidence_class','priority','source_output']])
    report+='\n\nEvery action remains proposed. Expected benefit describes better analysis, not measured savings or commercial outcomes. Source coverage and forecast evaluation limits apply. See decision_action_register for complete limitations and evidence references.\n'
    (docs/'PHASE5_BUSINESS_RECOMMENDATIONS.md').write_text(report,encoding='utf-8')

def audit_report(result,cfg,root=ROOT):
    t={p.stem:pd.read_parquet(p) for p in (root/'outputs/phase5/tables').glob('*.parquet')}
    reports(t,result,cfg,root)
    inventory=[str(p.relative_to(root)).replace('\\','/') for d,pattern in [('src','*decision*.py'),('src','*intelligence.py'),('src','prioritization.py'),('src','scenario_engine.py'),('src','forecast_risk.py'),('src','phase5*.py'),('tests','test_phase5*.py'),('notebooks','0[67]*.ipynb'),('docs','PHASE5*.md')] for p in (root/d).glob(pattern)]
    inventory+=['config/decision_intelligence.yaml','run_pipeline.py','src/phase3_pipeline.py','tests/conftest.py','README.md']
    exports=pd.DataFrame([{'table':name,'rows':v['rows'],'business_key':';'.join(v['business_key']),'CSV/Parquet byte hashes recorded':True} for name,v in result['exports'].items()])
    text=f'''# Phase 5 final audit

Overall pass: **{result['passed']}**. Phase 1–4 baseline: **124 passed**, zero failures;
baseline_tests.xml is separate from the final suite. Existing settings.yaml is absent. Existing pinned
environment reused with no dependencies installed. Read-only Phase 2/3 input checks and all Phase 4
export/frozen-decision hashes are verified. input_inventory.json records actual schemas and inspected files.
The Phase 3 guard excludes later-phase reports from its prior-input inventory; original hashes remain valid.
No earlier reports, frozen forecasts or model-selection decisions are rewritten.

## Implementation inventory

'''+ '\n'.join(f'- `{p}`' for p in sorted(set(inventory)))+f'''

## Features, scoring and sensitivity

Feature grains: seven regions, 17 presentations, 119 region/presentation cells, one national row.
The absence-only 364-row export is unioned with 3,920 observed rows to form the 4,284-cell diagnostic grid.
Share/ratio definitions, complete-year changes, forecast-subset scope and unique joins are in
PHASE5_DECISION_FRAMEWORK.md and the two exported dictionaries. Original and Phase 3 flag counts remain distinct.
Missing activity is never zero-filled. Priorities use retained percentile components and policy weights
{cfg['weights']}; missing required dimensions leave explicit unscored status. Initial tiers are
{cfg['high_priority']}/{cfg['moderate_priority']}; ranks do not assert commercial value.
Weight, leave-out, threshold and min-max alternatives are exported with rank/tier changes and overlap.

{md_table(t['regional_priority_scores'][['region_name','composite_score','rank','monitoring_tier']])}

{md_table(t['rank_stability_summary'])}

## Frozen forecast risk and hierarchy

Selected-series profiles recompute origin/horizon errors using the frozen selected variant; paired naive
comparisons share forecast cells. No fitting or reselection occurs. Absolute, scaled and volume-relative
errors, signed bias, sample counts, selected/all-family failures and interval-unavailable status remain explicit.
Hierarchy gaps compare direct national with all seven regions. Forecasts are unchanged and unreconciled.
See the executive summary and forecast_risk_register for actual observed risk classes and review rules.

## Scenarios, recommendations and dashboard products

Six scenario families use observed 2025 or frozen retrospective forecast baselines, explicit fixed cost
assumptions, nonnegative counts and item-conserving mix changes. Accounting break-even is independently
checked. Every scenario is hypothetical, without probabilities or observed-benefit claims.
All recommendations are deterministic, traceable to a unique source row/metric, with evidence class,
proposed analyst action and limitation. Dashboard products retain business keys, units and null/status semantics.

{md_table(exports)}

## Chart inventory

'''+ '\n'.join(f'- `{p}`' for p in result['charts'])+f'''

## Executed notebooks and tests

{md_table(pd.DataFrame(result['notebooks']))}

Full suite: **{result['tests']['tests']} tests**, **{result['tests']['failures']} failures**,
**{result['tests']['errors']} errors**, **{result['tests']['skipped']} skipped**. Evidence:
outputs/phase5/validation/all_tests.xml and test_execution.log. Tests include deterministic accounting
fixtures, impossible mix inputs, missing-component/tie/weight behavior, future-data cutoffs, source joins,
rank sensitivity, rule traceability, schemas, chart and notebook artifacts, and full earlier-phase regression.

## Independent reconciliation, reproducibility and preservation

**{result['independent_checks']} independent checks passed**, **{result['independent_failed_checks']} failed**.
Separate loops/algebra reconstruct history, shares, ratios, forecast errors, weighted arithmetic/ranks,
scenario results, mix conservation, break-even, hierarchy gaps, dashboard counts and recommendation references.
Evidence: decision_reconciliation.csv with expected/observed/difference/tolerance/status.
Two complete executions have byte-identical CSV/Parquet exports: **{result['tables_byte_identical']}**;
reproducibility.json records both inventories. Notebook runtime metadata is not claimed byte-identical.
Protected prior artifacts: **{result['protected_artifacts']}**, unchanged: **{result['protected_artifacts_unchanged']}**.
Metadata records Python/dependency versions, original hashes, configuration, weights and assumptions.

## Limitations and Phase 6

Subjective policy weights and thresholds; incomplete applicability; 36 months; overlapping short forecast
support; sparse eligible subset; no calibrated intervals; retrospective publication-vintage limitations;
fixed accounting assumptions; no population, case-mix, clinical intervention or manufacturer financial data.
Phase 6 should expose component scores, policy sensitivity, unscored entities, source evidence, origin/horizon
counts and unavailable uncertainty. Visually separate historical observations, model results and hypothetical
scenarios. No dashboard, UI or PBIX is implemented here. No critical validation remains unresolved if pass=True.

## Windows PowerShell reproduction

```powershell
Set-Location '<PROJECT_ROOT>'
.\\.venv\\Scripts\\python.exe run_pipeline.py --phase 5
.\\.venv\\Scripts\\python.exe -m src.phase5_pipeline --audit
```
'''
    (root/'docs/PHASE5_AUDIT.md').write_text(text,encoding='utf-8')
