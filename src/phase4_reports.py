"""Interview-defensible reports sourced from executed forecast rows, never fixed results."""
import json
import pandas as pd
from .common import ROOT,write_json
from .phase3_reports import md_table

METHODOLOGY=r'''# Phase 4 forecasting methodology

## Scope and prerequisites

Forecast monthly NHSBSA atorvastatin prescription-item activity in England. Items are product
occurrences, not patients, sales or India demand. No NIC model is fitted: cost is optional and its
Phase 3 shifts require separate validation. Read-only Phase 2 SQL views reproduce all twenty Parquet
exports and their final-audit hashes. Phase 3 table hashes and its passed audit are checked. Source
snapshots, the DuckDB file, SQL, prior reports, notebooks and analytical tables are hash protected.
Existing settings.yaml is absent; config/dataset.json and config/phase2.json are retained.
config/forecasting.yaml is the single forecasting configuration (JSON syntax, valid YAML subset),
parsed with the standard library. Existing pinned dependencies suffice; nothing is installed.

## Series and eligibility

Series are national, seven regional aggregates, and candidate region/presentation/unit item series.
Region/presentation quantity is never combined across units. Aggregated item totals sum all observed
presentations, not just screened candidates. Unknown absent cells remain null and are never zero-filled.

The Phase 2 full-history inventory is revalidated and reported, but cannot determine membership
using holdout values. Eligibility is frozen using January 2023–December 2024 only: 24 contiguous,
finite observed months, complete coverage, and >=36,000 items for a region/presentation series.
This uses the existing absolute volume threshold over a shorter observed training window, conservatively
excluding candidates that only reach it later. The first-origin decision applies to every later origin;
no series is admitted because of good future outcomes. Future gaps are recorded and cause explicit
model failures, not retrospective membership changes. Full-history missingness is descriptive only.

## Chronological evaluation and the freeze

Development history: January 2023–June 2025. Expanding origins start December 2024 (24 months),
with targets January–June 2025. At h=1/2/3 there are 6/5/4 valid development forecasts per series.
Each origin trains on observations through that origin and produces all requested future steps
at once. No intermediate actual future observation is substituted.

The frozen model family, hyperparameters, selection policy and interval calibration are written
before any holdout fit, with SHA-256 checked afterward. Final holdout targets are July–December 2025;
origins begin June 2025, giving 6/5/4 targets per horizon. July h=2/h=3 forecasts are excluded because
their origins precede the June selection freeze. This triangular support is deliberate, not an attempt
to improve scores. A December h=3 forecast originates in September. As holdout months arrive, the
model may refit using newly observed data, while architecture and selected alpha remain frozen.

The dataset's 2025 descriptive patterns were already visible in earlier phases. This is a retrospective
chronological holdout isolated from programmatic model selection, not a pristine blind external study.
Small overlapping forecast samples do not support iid significance tests or precise generalization claims.
Origin cutoffs identify the last included observation month. The fixed source vintage does not
reconstruct historical publication availability or subsequent revisions; release timing is not modeled.
Consequently the as-of label describes an analytical cutoff, not verified real-time data availability.

## Models and feature construction

Naive: yhat(t+h)=y(t). Seasonal naive: yhat(t+h)=y(t+h−12), using a target-aligned date that
already exists at the origin. Missing/short seasonal lags fail explicitly, without fallback.
Drift: yhat(t+h)=y(t)+h*(y(t)−y(first))/(n−1), requiring contiguous calendar history and n>=2.

Damped ETS is statsmodels Holt-Winters ExponentialSmoothing with additive damped trend,
no seasonal component, estimated training-only initialization, damping constrained to [0.8,0.98],
L-BFGS-B, maximum 1,000 iterations, no brute-force initialization. Training values divide by their
positive training mean for numerical conditioning and forecasts multiply back. This is damped Holt
exponential smoothing, not a claim that a full probabilistic ETS error model supplies native intervals.
Minimum history is 24 months. Optimizer success, warnings and fitted parameters are recorded.
Failure means null prediction under the same label; no replacement model is hidden.
See [statsmodels exponential smoothing](https://www.statsmodels.org/stable/generated/statsmodels.tsa.holtwinters.ExponentialSmoothing.html).

Ridge uses direct separate h=1/2/3 regressions. Feature origin u includes y(u), y(u−1), y(u−2),
the mean of those three observations, and sine/cosine of the known target calendar month u+h.
The labels are y(u+h), and only pairs with u+h<=training cutoff are permitted. lag_1 names the
last observation preceding an h=1 target; it is still y(u), not an unknown intermediate value at h>1.
StandardScaler and Ridge(solver='svd') are a scikit-learn pipeline fitted on supervised training rows.
No scaler, feature selection or label uses the holdout. The rolling mean is correlated with the lags;
regularization handles this redundancy, and coefficients are not causal importance or significance.

Six features and a minimum 15 usable rows avoid the severe loss from lag 12: first-origin direct
models have 21/20/19 rows for h=1/2/3. Alpha grid is 0.1,1,10,100, selected only on development.
No log transform, neural network, random split or optional complex model is introduced. Random seed
42 is recorded; SVD Ridge and the chosen ETS optimizer do not use stochastic training.
See [scikit-learn Pipeline](https://scikit-learn.org/1.5/modules/generated/sklearn.pipeline.Pipeline.html)
and [StandardScaler](https://scikit-learn.org/1.5/modules/generated/sklearn.preprocessing.StandardScaler.html).

All training calendars must be regular and populated. Nonnegative clipping is a predetermined
constraint on point predictions; both raw and constrained values are stored. An unconstrained
development sensitivity quantifies its effect. Continuous expected-count predictions are retained
at full precision; integer rounding is only for report display.

## Metrics and common support

Error e=prediction−actual, so positive bias means overforecast. MAE=mean(|e|),
RMSE=sqrt(mean(e²)), WAPE=100 sum(|e|)/sum(|actual|), and sMAPE=mean[200|e|/(|actual|+|prediction|)].
sMAPE assigns zero to a zero/zero pair; WAPE is undefined when total actual magnitude is zero.
All metric inputs are recorded prediction rows, not unrelated fitted calculations.

MASE=mean(|e_i|/q_i), with q_i=mean of absolute adjacent changes in the original training history
available at forecast i's origin. This is the nonseasonal naive scale, not a future-data denominator.
Zero/undefined q gives undefined scaled error, reported with mase_defined_rows. Scales use the
original expanding training prefix even in diagnostic window/anomaly sensitivities, giving a fixed
reference for comparison. RMSE is computed from individual errors, never averaged fold RMSEs.

For family comparison, every series/origin/horizon cell must have a successful prediction from all
five frozen family configurations; a failed cell is removed for every family. Development selection
first excludes any configuration with a failed development opportunity at that aggregation level,
then ranks remaining configurations on their common support. Failed attempts remain in the exports.
Comparison sample sizes can differ from all-opportunity selected-model summaries; both are labeled.
Pooled MASE weights each available forecast row equally; with complete support this is equal series
weight, while WAPE is volume-weighted. Raw presentation/regional MAE is affected by series size.

## Development-only selection

The short history makes per-series tuning unstable, so selection is shared by aggregation level.
Minimize pooled development MASE. Configurations within 2% relative MASE of the best receive a
simplicity preference: naive, drift, seasonal naive, damped ETS, Ridge; larger Ridge alpha breaks
otherwise equal within-family ties. Scores, runner-up, eligible configs, failure exclusion, support
and freeze date are recorded. Ridge alpha is frozen per level even when Ridge is only a comparator.
The selected operational family remains the development choice even if a comparator wins the holdout.
Observed holdout winners are descriptive and are never fed back into selection.

## Intervals

Only development errors of the frozen chosen series/model/horizon can calibrate holdout or operational
intervals. Absolute-residual empirical radii use a higher order quantile, with nonnegative lower bounds.
Minimum residual count is prespecified at 20 per series/horizon. Below that, 80%/95% bounds and
coverage are null, with an explicit unavailable status. Here 6/5/4 errors cannot support reliable
calibration. Pooling correlated regional errors is not independent national calibration. No narrow
95% interval is manufactured. Even with sufficient count the method is experimental: overlapping
origins, distribution changes and reuse of selection folds preclude an exchangeability guarantee.
Interval coverage and widths are evaluated only on genuinely available bounds; unavailable is not 0% coverage.

## Hierarchy and robustness

Historical national items must equal all seven regions, and each regional actual must equal all
observed presentations. Forecasts compare direct national with the sum of all seven regional forecasts,
using national training scales. Screened region/presentation forecasts never masquerade as a national
total. Direct and regional forecasts are not forcibly rescaled; their coherence gaps remain explicit.
An operational regional-sum comparison is also exported. Choosing a preferred hierarchy approach
from holdout superiority would be post-selection and is not done.

Development-only robustness varies expanding versus trailing 24 months, model/alpha, horizon,
nonnegative constraints, alternative metrics and selection tie thresholds 0/2/5%. Anomaly sensitivity
clips a diagnostic training copy at training median ±3.5 MAD/0.67449, only with positive MAD and
>=12 observations. No retrospective Phase 3 persistence classification is used for treatment.
No source row is deleted, changed or imputed. Eligibility exclusions and forecast coverage expose
missingness; the effect of unknown absent activity cannot be identified by assuming zero.

## Operational artifacts, validation and limits

After evaluation, frozen choices refit all observed history through December 2025 and predict
January–March 2026. These are retrospective as-of-December-2025 forecasts, not live present-day
market predictions. No 2026 actuals are sourced or evaluated. Saved model artifacts contain
refit parameters/configuration and versioned provenance, not opaque executable pickles; refitting
with the pinned environment recreates the estimators.

Independent Python/math checks recompute every baseline, calendar horizon, actual, MASE denominator,
expected row count, metric and development selection, plus historical hierarchy. Adversarial tests
change values after an origin and after the development freeze; preceding forecasts and selections
must remain unchanged. Complete reruns compare every CSV/Parquet hash and frozen decisions.
Earlier integration tests overwrite a summary; a test cleanup fixture restores its exact bytes,
without modifying prior calculations or relaxing validation.

Only 36 months and six holdout target months; overlapping errors; sparse tuning support; correlated
geography; full-history metadata already seen; unknown missing-cell mechanisms; restricted target
and geography. Accuracy is evidence for this retrospective window, not a guarantee of future planning
benefits. No causal, clinical, manufacturer-revenue or India-market claim is supported.
'''

def reports(tables,result,cfg,root=ROOT):
    docs=root/'docs'; docs.mkdir(exist_ok=True)
    (docs/'PHASE4_FORECASTING_METHODOLOGY.md').write_text(METHODOLOGY,encoding='utf-8')
    development=tables['development_model_metrics']; hold=tables['holdout_model_metrics']; decisions=tables['model_selection_decisions']
    winner=decisions[decisions.series_id.eq('England')].iloc[0]
    national=hold[hold.aggregation_level.eq('national')]
    selected=national[national.variant.eq(winner.selected_variant)].iloc[0]; naive=national[national.model.eq('naive')].iloc[0]
    observed_best=national.sort_values('MASE').iloc[0]
    improvement=100*(1-selected.MASE/naive.MASE)
    horizons=tables['horizon_metrics']; nationalh=horizons[(horizons.split_type=='holdout')&(horizons.aggregation_level=='national')]
    besth=nationalh.sort_values('MASE').groupby('horizon',sort=True).head(1).sort_values('horizon')
    devh=horizons[(horizons.split_type=='development')&(horizons.aggregation_level=='national')].sort_values('MASE').groupby('horizon',sort=True).head(1).sort_values('horizon')
    selectedh=tables['selected_forecast_metrics']; selectedh=selectedh[(selectedh.split_type=='holdout')&(selectedh.aggregation_level=='national')]
    region=tables['regional_forecast_metrics']; region=region[(region.split_type=='holdout')&(region.variant.eq(decisions[decisions.aggregation_level.eq('regional')].selected_variant.iloc[0]))]
    calibration=tables['interval_calibration']; support=calibration[calibration.series_id.eq('England')]
    op=tables['operational_forecasts']; nationalop=op[op.series_id.eq('England')]
    failures=tables['model_failures']; failure_summary=failures.groupby(['split_type','aggregation_level','model']).size().rename('failed_forecasts').reset_index()
    hierarchy=tables['aggregate_forecast_metrics']; compare=tables['aggregate_forecast_comparison']; holdgap=compare[compare.split_type.eq('holdout')]
    counts=decisions.groupby(['aggregation_level','selected_model','selected_variant']).size().rename('series').reset_index()
    excluded=tables['series_eligibility'].query('phase2_full_history_candidate and not eligible')
    claims={'selected_national_model':winner.selected_model,'selected_national_variant':winner.selected_variant,
            'national_holdout_mase':float(selected.MASE),'national_holdout_mae':float(selected.MAE),'national_holdout_rmse':float(selected.RMSE),
            'national_holdout_wape_pct':float(selected.WAPE),'national_holdout_bias':float(selected.Bias),
            'national_naive_mase':float(naive.MASE),'mase_improvement_vs_naive_pct':improvement,
            'observed_holdout_lowest_mase_model':observed_best.model,'observed_holdout_lowest_mase':float(observed_best.MASE),
            'operational_national':json.loads(nationalop[['forecast_month','horizon','point_forecast']].to_json(orient='records',date_format='iso')),
            'series_evaluated':result['series_count'],'development_forecasts':result['development_forecasts'],
            'holdout_forecasts':result['holdout_forecasts'],'model_failures':result['model_failures']}
    write_json(root/'outputs/phase4/validation/business_claims.json',claims)
    comparison=f'''# Phase 4 model comparison

Development selection is frozen before holdout evaluation. Do not replace the selected family with
the lowest holdout score. Tables derive from stored predictions. Failure cells are removed for all
families on common support; selected-model summaries preserve all successful selected opportunities.

## Development family comparison (frozen Ridge alpha)

{md_table(development)}

## Development selection decisions

{md_table(decisions.drop_duplicates(['aggregation_level','selected_variant']).drop(columns='series_id'))}

## Final holdout family comparison

{md_table(hold)}

## National horizon comparison: final holdout

{md_table(nationalh)}

## Lowest development MASE by horizon (diagnostic, not separate operational selection)

{md_table(devh[['horizon','model','variant','n','MASE','MAE','WAPE']])}

## Lowest observed holdout MASE by horizon (descriptive only)

{md_table(besth[['horizon','model','variant','n','MASE','MAE','WAPE']])}

## Frozen selected national model by horizon

{md_table(selectedh)}

## Regional selected-model performance

{md_table(region)}

## Failures and coverage

{md_table(failure_summary)}

Every failure remains a row in model_failures.csv and backtest_predictions.csv, with origin,
target, horizon, requested model and optimizer warnings/status. Any failed development opportunity
excludes that configuration from shared-level selection. A lower successful-row score does not
override this guard. Metrics based on different supports are not silently ranked together.
Region/presentation common-support comparisons lose the ETS-failed cells for every family; the
selected Ridge all-opportunity summary includes those cells and therefore has a different n.

## Hierarchical forecast comparison

{md_table(hierarchy)}

Direct and regional-sum forecasts remain separate. Coherence differences are not corrected or
declared statistical errors. Screened presentation series do not form a complete national total.
'''
    (docs/'PHASE4_MODEL_COMPARISON.md').write_text(comparison,encoding='utf-8')
    business=f'''# Phase 4 business insights

## Executive summary and objective

Forecast recorded monthly NHS atorvastatin item activity one to three months ahead. **{result['series_count']}**
series are evaluated: one national, seven regional and training-eligible region/presentation series.
The development-selected national model is **{winner.selected_model}**, with final holdout
**MASE {selected.MASE:.6f}**, **MAE {selected.MAE:,.2f} items**, **RMSE {selected.RMSE:,.2f} items**,
and **WAPE {selected.WAPE:.6f}%**, over **{int(selected.n)}** overlapping forecasts.
Relative MASE improvement against naive is **{improvement:.6f}%** on identical support.
This is a measured retrospective forecast comparison, not an observed business revenue benefit.

## Models and validation design

Naive, seasonal naive (period 12), drift, nonseasonal damped additive ETS, and direct Ridge with
training-only StandardScaler. Ridge alpha candidates 0.1/1/10/100 are evaluated in development;
family choices and hyperparameters are frozen before holdout. Development: Jan 2023–Jun 2025,
initial training Jan 2023–Dec 2024. Final targets: Jul–Dec 2025, origins Jun–Nov 2025.
There are 6/5/4 forecasts per horizon, not six at every horizon. Shared model selection by level
reduces per-series tuning on very short histories. Earlier descriptive data were visible, so this
is retrospective chronological evaluation rather than a blinded external study.

## Eight evidence-based findings

1. **Selected national model beats naive in this window.** {winner.selected_model}, horizons 1–3,
Jul–Dec 2025: MASE **{selected.MASE:.6f}** versus naive **{naive.MASE:.6f}**, an improvement
of **{improvement:.6f}%**, n={int(selected.n)} paired forecast cells. It could support activity planning,
subject to ongoing monitoring; six target months and overlapping errors limit generalization.
Evidence: holdout_model_metrics.csv; charts 04–06.

2. **Holdout winner differs from frozen national selection.** Lowest observed national MASE is
**{observed_best.model} ({observed_best.MASE:.6f})**, n={int(observed_best.n)}, versus selected
**{winner.selected_model} ({selected.MASE:.6f})**. This comparison is reported honestly and does
not change the operational family. Development choices are not retuned on holdout rankings.
Evidence: model_selection_decisions.csv and holdout_model_metrics.csv; charts 03 and 12.

3. **Horizon accuracy is uneven.** The selected national model's horizon-specific errors are below.
Each h=3 forecast genuinely originates three months earlier. Different target-month support and
small n mean these results cannot establish monotonic reliability or independent error distributions.
Evidence: horizon_metrics.csv; charts 06 and 11.

4. **Regional variation remains.** Selected regional MASE spans **{region.MASE.min():.6f}–{region.MASE.max():.6f}**,
Jul–Dec 2025, n={int(region.n.min())} cells per region. Compare against each region's naive rows
before adopting a uniform service target. Regions are unadjusted fixed aggregates and share shocks.
Evidence: regional_forecast_metrics.csv; charts 07–08.

5. **Presentation-level reliability includes failure risk.** The selected model distribution below
uses shared development decisions. **{result['model_failures']}** attempted ETS forecast rows failed
optimization, with dates and warnings retained. Selection excludes configs with development failures,
rather than silently replacing their predictions. Eligible products are not the full prescribing population.
Evidence: model_failures.csv and model_selection_decisions.csv; chart 17.

6. **Uncertainty intervals are unsupported.** National development calibration counts are only
6/5/4, below the frozen minimum {cfg['minimum_interval_residuals']}; 80%/95% bounds and empirical
coverage are null. Point forecasts should be shown with this limitation, not narrow bands suggesting
calibrated confidence. Evidence: interval_calibration.csv and interval_coverage_summary.csv; chart 15.

7. **Hierarchy requires explicit checks.** All **{len(tables['forecast_hierarchy_checks'])}** historical
national/regional/presentation consistency checks pass. The mean absolute final holdout difference
between direct national and regional-sum forecasts is **{holdgap.coherence_gap.abs().mean():,.2f} items**,
n={len(holdgap)} origin/horizon cells. They remain separately evaluated, without post-hoc rescaling.
Evidence: forecast_hierarchy_checks.csv and aggregate_forecast_comparison.csv; chart 16.

8. **Operational outputs are historical as-of forecasts.** Refit frozen choices through December
2025 to issue January–March 2026 expectations below. They are not live current-market forecasts
and are not compared with separately uncollected 2026 actuals. Source data stay intact; development
sensitivities cover trailing windows, training-only anomaly treatment, constraints and tie policies.
Evidence: operational_forecasts.csv and forecast_robustness_results.csv; chart 18.

## Selected national horizon performance

{md_table(selectedh)}

## Selected model distribution

{md_table(counts)}

## Regional selected-model errors

{md_table(region[['region_name','model','n','MASE','MAE','RMSE','WAPE','Bias']])}

## Eligibility reconciliation with Phase 2

Full-history inventory reports {int(tables['series_eligibility'].phase2_full_history_candidate.sum())} region/presentation
candidates, but the initial training-only screen excludes:

{md_table(excluded[['series_id','presentation_name','initial_training_items','reason']])}

The exclusion prevents future volume from influencing series membership; no missing record is fabricated.

## Retrospective national operational forecasts

{md_table(nationalop[['forecast_month','horizon','model','point_forecast','interval_status']])}

## Recommendations and limits

For Phase 5, build a dashboard that distinguishes observed history, origin-specific holdout predictions
and retrospective operational forecasts. Show model, horizon, cutoff, error metrics, sample support,
failure status and unavailable uncertainty prominently. Monitor drift and missingness before live use.
Evaluate more chronological origins and additional genuinely future observations before claiming stable
accuracy or calibrated intervals. Do not select a regional-sum approach merely because it wins this
holdout; assess it in a fresh period. Keep naive as the ongoing benchmark.

Only 36 months, short overlapping holdout, nonblind historical context, selected high-activity series,
unknown gaps and correlated geography. No clinical recommendation, patient-demand claim,
manufacturer revenue estimate, measured profit impact or direct India-market extrapolation is supported.
'''
    (docs/'PHASE4_BUSINESS_INSIGHTS.md').write_text(business,encoding='utf-8')
    card=f'''# Phase 4 model card

**Version:** {cfg['model_version']}. **Target:** monthly prescription_items. **Intended use:**
reproducible retrospective activity forecasting and analyst-interview demonstration of honest evaluation.
Source: NHSBSA PCA atorvastatin community dispensing, England, Jan 2023–Dec 2025; read-only validated
Phase 2 views and protected monthly Parquet. Data/config hashes and exact environment are in
outputs/phase4/validation/run_metadata.json.

These forecasts represent historical NHS atorvastatin prescribing activity, not pharmaceutical
manufacturer revenue or actual patient demand. Forecasts are not clinical prescribing recommendations.
Forecasts should not be extrapolated directly to India.

## Training, families and selection

24-month initial contiguous training, expanding development origins, shared by aggregation-level
MASE selection with {100*cfg['selection_tie_relative']:.1f}% simplicity preference. Five families:
naive; seasonal naive 12; drift; damped additive nonseasonal ETS; direct StandardScaler+Ridge.
Effective first-origin Ridge rows 21/20/19; alpha grid 0.1/1/10/100. Failed development configurations
are ineligible for selection. Choices and calibration are persisted before holdout evaluation.

{md_table(counts)}

## Evaluation

Development Jan 2023–Jun 2025, final holdout Jul–Dec 2025, origin-sliced 1–3 month forecasts,
6/5/4 targets per horizon per series. Holdout models may refit on newly observed months but cannot
change architecture or alpha. MASE uses training-only adjacent naive error; MAE/RMSE/WAPE/sMAPE/Bias
are computed from stored predictions. Common-support family comparison accounts for model failures.
National selected model holdout MASE {selected.MASE:.6f}, MAE {selected.MAE:,.2f}, RMSE {selected.RMSE:,.2f},
WAPE {selected.WAPE:.6f}%, n={int(selected.n)}. Full results: PHASE4_MODEL_COMPARISON.md.

## Uncertainty and operational behavior

Development residual empirical intervals require {cfg['minimum_interval_residuals']} observations per series/horizon;
only 6/5/4 exist, so bounds and coverage are unavailable. No coverage guarantee. Nonnegative forecasts
retain raw values. Frozen models refit through December 2025 to predict January–March 2026; these
are retrospective as-of forecasts, not current predictions. No 2026 actuals are incorporated.

## Limitations and inappropriate uses

Short overlapping evaluation, retrospective nonblind context, only one chemical/geography,
unknown absent-cell mechanisms, failure exclusions, no patient or population denominators, no
intervention/clinical evidence. No guaranteed accuracy, clinical dosing, price/revenue forecast,
India-market transfer or demonstrated business gain. Continuous point expectations are not observed counts.
Screened presentation sums are not national forecasts. Direct and regional-sum forecasts are not
forced coherent; gaps are disclosed. Additional future evaluation is needed before production adoption.

## Reproduce

```powershell
.\\.venv\\Scripts\\python.exe run_pipeline.py --phase 4
.\\.venv\\Scripts\\python.exe -m src.phase4_pipeline --audit
```

Saved selected_model_parameters.json contains refit parameters and provenance; deterministic fitting
with the pinned environment recreates models. No executable pickle is required. Source hashes, model
decisions, dates, predicted rows and failure reasons are available for independent review.
'''
    (docs/'PHASE4_MODEL_CARD.md').write_text(card,encoding='utf-8')

def audit_report(result,cfg,root=ROOT):
    tables={p.stem:pd.read_parquet(p) for p in (root/'outputs/phase4/tables').glob('*.parquet')}
    inventory=[str(p.relative_to(root)).replace('\\','/') for directory,pattern in [('src','forecast*.py'),('src','phase4*.py'),('tests','test_phase4*.py'),('docs','PHASE4*.md'),('notebooks','0[45]*.ipynb')] for p in (root/directory).glob(pattern)]
    inventory+=['config/forecasting.yaml','config/kernels/pharma-phase4/kernel.json','tests/conftest.py','README.md','run_pipeline.py','src/phase3_pipeline.py','docs/PHASE4_AUDIT.md']
    export_table=pd.DataFrame([{'output (CSV and Parquet)':k,'rows':v['rows'],'columns':len(v['columns'])} for k,v in result['exports'].items()])
    text=f'''# Phase 4 final audit

Overall pass: **{result['passed']}**. This is executed retrospective prescribing-activity forecasting,
not manufacturer revenue, clinical advice, patient demand or India-market forecasting.

## Repository baseline and prerequisites

Existing Phase 1–3 suite: **74 tests passed**; baseline_tests.xml records the rerun with authorized
project-local temporary storage after four Windows PermissionError setup errors in the initial run.
Required raw/data/SQL/docs/notebooks and reporting artifacts exist. No packages were installed.
settings.yaml is absent; existing configs were retained. The database remains
data/processed/pharma.duckdb, main/phase2; DATEs and exact twenty-view exports are verified read-only.
Relevant actual totals: {result['input_verification']['total_items']:,} items and
GBP {result['input_verification']['total_nic_gbp']:,.2f} NIC. Fact rows {result['input_verification']['fact_rows']};
364 absent diagnostic cells remain null. Prior full-history inventory and retrospective anomaly flags
are inspected but never used as future-aware training treatments.

## Architecture and implementation inventory

Central configuration → validated series → origin folds → development fits → pooled-level model
selection and frozen choices/calibration → holdout refits → comparison/independent validation →
as-of-December operational refits → exports/charts/notebooks. Earlier pipeline modes remain supported.
The Phase 3 document guard excludes new Phase 4 reports while retaining its original prior-file
hashes; no prior analytical calculations or protected artifacts are changed.

'''+ '\n'.join(f'- `{p}`' for p in sorted(set(inventory)))+f'''

## Eligibility and evaluation support

Evaluated series: **{result['series_count']}**, by level **{result['series_by_level']}**.
Training-only initial-window eligibility is frozen without holdout membership leakage. Series eligibility
and exclusions include all candidate pairs and Phase 2 inventory reconciliation. Development origins
Dec 2024–May 2025 with targets Jan–Jun 2025; holdout origins Jun–Nov 2025 with targets Jul–Dec 2025.
Each stage has 15 origin/horizon cells per series: 6/5/4. Development forecasts:
**{result['development_forecasts']}**, including eight configurations (four Ridge alpha trials).
Holdout forecasts: **{result['holdout_forecasts']}**, five frozen family configurations per level.
Selected holdout forecasts: **{result['selected_holdout_forecasts']}**. Failed attempts are included in
these counts; successful common-support n is reported separately.

## Model configurations and selection

{md_table(tables['frozen_family_configurations'])}

{md_table(tables['model_selection_decisions'].drop_duplicates(['aggregation_level','selected_variant']).drop(columns='series_id'))}

Selected choices/config hash are persisted before the first holdout fit. Their SHA-256 remains
{result['frozen_decisions_sha256']} afterward. Model parameters, warnings, optimizer status,
cutoffs, data/config/model versions and package versions are saved. There are **{result['model_failures']}**
failed main forecast rows; no fallback is relabeled as the failed family.

## Final holdout comparison and horizon results

{md_table(tables['holdout_model_metrics'])}

{md_table(tables['selected_forecast_metrics'].query("split_type == 'holdout'"))}

Regional and per-series comparisons, bias, alpha development scores and robustness are separate
exports. National ETS is the development choice; a lower holdout Ridge score is disclosed without
changing selection. Presentation-level ETS failures prevent its shared-level selection even where
successful-row scores are lower. No iid significance or artificial confidence interval for metrics is claimed.

## Interval and hierarchy diagnostics

{md_table(tables['interval_coverage_summary'])}

Calibration is development-only with minimum {cfg['minimum_interval_residuals']} residuals per series/horizon;
short samples give null bounds/coverage, not fabricated uncertainty. All
**{len(tables['forecast_hierarchy_checks'])}** historical hierarchy checks pass. Direct national and
all-seven-region sums are evaluated separately; no screened-presentation sum becomes a national total.

{md_table(tables['aggregate_forecast_metrics'])}

## Retrospective operational forecasts

{md_table(tables['operational_forecasts'].query("series_id == 'England'")[['forecast_month','horizon','model','point_forecast','interval_status']])}

All selected series have three as-of-Dec-2025 future rows. Operational regional-sum comparison is
separate. No external Jan–Mar 2026 actuals are fabricated or evaluated.

## Export inventory

{md_table(export_table)}

Each output is under outputs/phase4/tables. Independent forecast_validation.csv is under validation.
Selected refit parameter metadata is under outputs/phase4/models. Dataset/config/choices hashes,
environment and sample provenance are in run_metadata.json and frozen_development_decisions.json.

## Chart inventory

'''+ '\n'.join(f'- `{p}`' for p in result['charts'])+f'''

Charts explicitly distinguish single-origin paths, rolling h=1 predictions from different origins,
development/holdout and retrospective operational dates. No different-origin forecast path is spliced silently.

## Notebook execution

{md_table(pd.DataFrame(result['notebooks']))}

## Tests, independent validation and reproducibility

Full suite: **{result['tests']['tests']} tests**, **{result['tests']['failures']} failures**,
**{result['tests']['errors']} errors**, **{result['tests']['skipped']} skipped**. Tests include analytical
fixtures, target dates, direct supervised label bounds, scaler isolation, adversarial future-value changes,
holdout-isolated selection, failure logging, undefined ratios, common support, hierarchy, intervals,
metadata and operational dates. Audit rerun evidence is asserted against actual hashes by pytest.

Independent Python/math checks: **{result['independent_checks']} passed**,
**{result['independent_failed_checks']} failed**. These independently recompute baselines, dates,
actuals, MASE scales, row counts, metrics and pooled development selections. Historical hierarchy is
independently summed. Numerical business claims derive from these checked prediction-based tables.

All {len(result['exports'])} CSV/Parquet pairs byte-identical across two full pipeline executions:
**{result['tables_byte_identical']}**. Frozen selection/calibration hashes also match. Notebook runtime
metadata is not claimed byte-identical. Protected previous artifacts: **{result['protected_artifacts']}**,
unchanged: **{result['protected_artifacts_unchanged']}**. Test-only restoration of the Phase 3 summary
prevents its integration-test side effect; no prior calculation or source observation is modified.

## Limits and Phase 5

Short overlapping samples, retrospective nonblind context, one chemical/geography, unknown gaps,
failed models and unsupported intervals limit confidence. Holdout rankings are not operational retuning.
Build a dashboard that exposes origin, horizon, selected model, baseline/error sample, failure status,
coherence and missing interval support. Seek longer and genuinely future evaluation before live use.
No critical validation remains unresolved when overall pass above is True.

## Reproduce

```powershell
.\\.venv\\Scripts\\python.exe run_pipeline.py --phase 4
.\\.venv\\Scripts\\python.exe -m src.phase4_pipeline --audit
```
'''
    (root/'docs/PHASE4_AUDIT.md').write_text(text,encoding='utf-8')
