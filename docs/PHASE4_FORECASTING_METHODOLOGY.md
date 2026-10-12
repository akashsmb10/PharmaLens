# Phase 4 forecasting methodology

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
