# Phase 3 statistical findings

Observation units and assumptions: PHASE3_METHODOLOGY.md. All histories are monthly and calendar ordered.
Model intervals are conditional uncertainty; fixed totals have no sampling intervals. No iid p-value
claims, region ANOVA, causal explanation or forecasting model is supplied.

## National trend effects

| level | metric | observed_months | missing_months | hac_lags | specification | interpretation | status | ols_slope_per_month | hac_ci_low | hac_ci_high | annual_linear_effect | annual_linear_effect_pct_of_mean | theil_sen_slope_per_month | kendall_tau_descriptive | r_squared | residual_sd | residual_cv | residual_lag1_correlation | log_linear_annual_change_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| national | prescription_items | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | 46,650.037066 | 41,844.583162 | 51,455.490969 | 559,800.444788 | 9.505048 | 47,729.625000 | 0.784127 | 0.856898 | 200,850.226159 | 0.034103 | -0.458962 | 10.082916 |
| national | net_ingredient_cost_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -167,339.592138 | -375,720.865475 | 41,041.681200 | -2,008,075.105653 | -21.455029 | -238,635.842500 | -0.425397 | 0.236419 | 3,168,450.911533 | 0.338529 | 0.801529 | -18.112097 |
| national | ingredient_cost_per_item_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -0.039432 | -0.076390 | -0.002474 | -0.473184 | -29.202888 | -0.048418 | -0.590476 | 0.350242 | 0.565850 | 0.349219 | 0.787084 | -25.612524 |

## Regional trend effects

| level | region_code | region_name | metric | observed_months | missing_months | hac_lags | specification | interpretation | status | ols_slope_per_month | hac_ci_low | hac_ci_high | annual_linear_effect | annual_linear_effect_pct_of_mean | theil_sen_slope_per_month | kendall_tau_descriptive | r_squared | residual_sd | residual_cv | residual_lag1_correlation | log_linear_annual_change_pct |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| regional | Y56 | LONDON | prescription_items | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | 3,908.897040 | 2,916.874059 | 4,900.920020 | 46,906.764479 | 5.884995 | 3,926.932143 | 0.669841 | 0.683846 | 28,001.770627 | 0.035131 | -0.251023 | 6.159912 |
| regional | Y56 | LONDON | net_ingredient_cost_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -27,297.070099 | -56,500.181208 | 1,906.041010 | -327,564.841189 | -25.950587 | -38,104.050575 | -0.558730 | 0.295545 | 444,009.964669 | 0.351757 | 0.799757 | -22.556631 |
| regional | Y56 | LONDON | ingredient_cost_per_item_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -0.040745 | -0.077061 | -0.004429 | -0.488940 | -30.586963 | -0.049088 | -0.606349 | 0.373374 | 0.556119 | 0.347895 | 0.788229 | -27.050270 |
| regional | Y58 | SOUTH WEST | prescription_items | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | 3,690.117632 | 3,177.464816 | 4,202.770448 | 44,281.411583 | 8.104432 | 3,817.452381 | 0.761905 | 0.815684 | 18,480.852044 | 0.033824 | -0.348073 | 8.546252 |
| regional | Y58 | SOUTH WEST | net_ingredient_cost_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -17,475.030709 | -38,383.781798 | 3,433.720380 | -209,700.368510 | -23.320170 | -24,015.658538 | -0.476190 | 0.252248 | 316,989.292451 | 0.352515 | 0.803971 | -19.755893 |
| regional | Y58 | SOUTH WEST | ingredient_cost_per_item_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -0.041674 | -0.081178 | -0.002169 | -0.500082 | -29.896860 | -0.051147 | -0.577778 | 0.346067 | 0.603544 | 0.360822 | 0.787406 | -26.073811 |
| regional | Y59 | SOUTH EAST | prescription_items | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | 5,738.831274 | 5,149.738193 | 6,327.924355 | 68,865.975290 | 9.908812 | 5,896.339744 | 0.822222 | 0.874047 | 22,952.069059 | 0.033025 | -0.411214 | 10.535187 |
| regional | Y59 | SOUTH EAST | net_ingredient_cost_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -21,912.578990 | -50,027.293559 | 6,202.135580 | -262,950.947876 | -20.789296 | -31,637.470556 | -0.396825 | 0.225150 | 428,279.603442 | 0.338604 | 0.802298 | -17.406119 |
| regional | Y59 | SOUTH EAST | ingredient_cost_per_item_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -0.044713 | -0.087091 | -0.002335 | -0.536555 | -28.902010 | -0.053191 | -0.577778 | 0.344489 | 0.649824 | 0.350034 | 0.786899 | -25.278201 |
| regional | Y60 | MIDLANDS | prescription_items | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | 9,311.112870 | 8,388.830002 | 10,233.395738 | 111,733.354440 | 9.813721 | 9,630.420635 | 0.787302 | 0.855166 | 40,371.324781 | 0.035459 | -0.483629 | 10.419532 |
| regional | Y60 | MIDLANDS | net_ingredient_cost_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -31,439.458905 | -72,480.489599 | 9,601.571789 | -377,273.506857 | -20.262217 | -45,878.154420 | -0.396825 | 0.219598 | 624,426.694125 | 0.335361 | 0.797533 | -16.812991 |
| regional | Y60 | MIDLANDS | ingredient_cost_per_item_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -0.039345 | -0.077197 | -0.001493 | -0.472137 | -28.307366 | -0.048487 | -0.587302 | 0.337779 | 0.580408 | 0.347988 | 0.781356 | -24.662777 |
| regional | Y61 | EAST OF ENGLAND | prescription_items | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | 5,438.879279 | 4,980.502507 | 5,897.256051 | 65,266.551351 | 9.711496 | 5,588.583333 | 0.834921 | 0.875425 | 21,616.105656 | 0.032164 | -0.502647 | 10.290220 |
| regional | Y61 | EAST OF ENGLAND | net_ingredient_cost_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -17,465.199279 | -39,653.190952 | 4,722.792393 | -209,582.391351 | -20.172388 | -25,034.411206 | -0.412698 | 0.228982 | 337,649.445272 | 0.324989 | 0.797185 | -16.950581 |
| regional | Y61 | EAST OF ENGLAND | ingredient_cost_per_item_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -0.036995 | -0.071718 | -0.002271 | -0.443934 | -28.155516 | -0.044893 | -0.590476 | 0.349540 | 0.531693 | 0.337214 | 0.785746 | -24.699199 |
| regional | Y62 | NORTH WEST | prescription_items | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | 5,227.134363 | 4,519.710226 | 5,934.558500 | 62,725.612355 | 8.092127 | 5,407.017857 | 0.742857 | 0.791239 | 28,287.603556 | 0.036493 | -0.435903 | 8.524327 |
| regional | Y62 | NORTH WEST | net_ingredient_cost_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -23,236.781319 | -50,271.353350 | 3,797.790712 | -278,841.375830 | -23.264692 | -33,357.410714 | -0.501587 | 0.261053 | 411,888.718341 | 0.343653 | 0.799213 | -19.984487 |
| regional | Y62 | NORTH WEST | ingredient_cost_per_item_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -0.039092 | -0.075117 | -0.003066 | -0.469101 | -29.842293 | -0.048548 | -0.590476 | 0.357298 | 0.552377 | 0.351400 | 0.784138 | -26.269514 |
| regional | Y63 | NORTH EAST AND YORKSHIRE | prescription_items | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | 13,335.064607 | 12,414.825145 | 14,255.304070 | 160,020.775290 | 12.646599 | 13,560.888889 | 0.834921 | 0.903495 | 45,916.372239 | 0.036288 | -0.461867 | 13.631919 |
| regional | Y63 | NORTH EAST AND YORKSHIRE | net_ingredient_cost_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -28,513.472837 | -68,446.285516 | 11,419.339843 | -342,161.674039 | -18.660006 | -42,932.597393 | -0.374603 | 0.196502 | 607,464.527670 | 0.331285 | 0.805883 | -15.405254 |
| regional | Y63 | NORTH EAST AND YORKSHIRE | ingredient_cost_per_item_gbp | 36 | 0 | 3 | linear | Descriptive trend; HAC intervals conditional on short-series model, not causal | estimated | -0.036091 | -0.070276 | -0.001906 | -0.433090 | -29.064738 | -0.044458 | -0.603175 | 0.346223 | 0.522511 | 0.350658 | 0.794117 | -25.553712 |

## Seasonal diagnostics (three annual cycles)

| metric | observed_months | annual_cycles | interpretation | status | acf_lag12 | detrended_acf_lag12 | stl_seasonal_strength | mean_year_profile_correlation | raw_seasonal_index_range | day_adjusted_index_range |
|---|---|---|---|---|---|---|---|---|---|---|
| prescription_items | 36 | 3.000000 | Exploratory: only three annual cycles; indices retain within-year trend | exploratory complete series | 0.114859 | 0.220321 | 0.802226 | 0.668679 | 15.812292 | 8.569063 |
| net_ingredient_cost_gbp | 36 | 3.000000 | Exploratory: only three annual cycles; indices retain within-year trend | exploratory complete series | -0.122078 | -0.141627 | 0.627319 | -0.128290 | 37.436408 | 32.562207 |
| ingredient_cost_per_item_gbp | 36 | 3.000000 | Exploratory: only three annual cycles; indices retain within-year trend | exploratory complete series | -0.100248 | -0.140320 | 0.740303 | -0.128000 | 35.011681 | 34.445485 |

## Exact cost identities

| comparison | status | categories | method | item_volume_effect_gbp | presentation_mix_effect_gbp | within_presentation_cost_per_item_effect_gbp | observed_cost_change_gbp | reconciliation_residual_gbp | phase2_two_factor_volume_gbp | phase2_two_factor_cost_and_mix_gbp |
|---|---|---|---|---|---|---|---|---|---|---|
| 2024 vs 2023 | reconciled | 17 | Symmetric Shapley average over all six factor orders | 15,010,492.25 | 1,051,090.58 | -24,060,147.625673 | -7,998,564.79 | -0.00 | 14,999,211.25 | -22,997,776.04 |
| 2025 vs 2024 | reconciled | 17 | Symmetric Shapley average over all six factor orders | 7,478,389.50 | 1,254,765.30 | -59,243,626.551694 | -50,510,471.75 | 0.00 | 7,470,132.05 | -57,980,603.80 |
| 2025 vs 2023 | reconciled | 17 | Symmetric Shapley average over all six factor orders | 20,435,039.73 | 2,268,373.31 | -81,212,449.579711 | -58,509,036.54 | 0.00 | 20,368,919.39 | -78,877,955.93 |

Maximum decomposition residual: **GBP 2.23517417908e-08**.

## Business-question evidence map

| Question | Executed evidence and interpretation |
|---|---|
| Q1 Increasing activity | trend_summary; annual item growth and positive robust/OLS slopes |
| Q2 Across regions | regional_trend_summary; all seven latest annual item changes positive |
| Q3 Seasonality | seasonality_summary; profile correlation, day adjustment, detrended ACF; weak three-cycle evidence |
| Q4 Presentations driving growth | presentation_cost_change_contributions includes absolute item changes and contribution shares |
| Q5 Variability | descriptive_statistics raw CV; trend/forecast diagnostics detrended residual CV |
| Q6 Regional differences | matched calendar descriptive contrasts; no independent-region sampling inference |
| Q7 NIC divergence | weighted ratios, exact two/three-factor identity; association not causation |
| Q8 Breadth vs concentration | presentation/regional contributions; within-presentation ratios; mix effect |
| Q9 Large changes | calendar MoM diagnostics, rolling median, MAD and national path review |
| Q10 Meaning of extremes | all original flags classified retrospectively; no confirmed error without external verification |
| Q11 Future forecasting | coverage, zeros, volatility, ACF and shifts; no accuracy validation |
| Q12 Missingness/aggregation | cohort thresholds, complete/incomplete history, annual/monthly ratios; absent activity remains unknown |
| Q13 Robust recommendations | positive item direction across models/cohorts/regions and largest-presentation exclusion; cost mechanism unproven |
| Q14 Unsupported conclusions | clinical/causal/patient/India/manufacturer revenue claims and stable annual seasonality |

## Anomaly evidence and robustness

| classification | flags |
|---|---|
| Insufficient evidence | 16 |
| Potential structural shift | 61 |
| Unusual but plausible activity | 84 |

| analysis | metric | scenarios | minimum_estimate | maximum_estimate | all_positive | all_negative | unit | interpretation |
|---|---|---|---|---|---|---|---|---|
| annual aggregation | ingredient_cost_per_item_gbp | 1 | -44.166334 | -44.166334 | False | True | percent; annual ratio weighted, monthly reference unweighted | Sensitivity range, not sampling confidence interval |
| annual aggregation | net_ingredient_cost_gbp | 1 | -39.934224 | -39.934224 | False | True | percent; annual ratio weighted, monthly reference unweighted | Sensitivity range, not sampling confidence interval |
| annual aggregation | prescription_items | 1 | 7.579853 | 7.579853 | True | False | percent; annual ratio weighted, monthly reference unweighted | Sensitivity range, not sampling confidence interval |
| coverage cohort | prescription_items | 3 | 7.579949 | 7.580323 | True | False | percent observed-sum annual growth; absent cells unknown | Sensitivity range, not sampling confidence interval |
| coverage eligibility | prescription_items | 6 | 29.000000 | 29.000000 | True | False | candidate series count | Sensitivity range, not sampling confidence interval |
| dominant presentation sensitivity | net_ingredient_cost_gbp | 2 | -39.934224 | -38.662185 | False | True | percent annual growth | Sensitivity range, not sampling confidence interval |
| dominant presentation sensitivity | prescription_items | 2 | 6.576248 | 7.579853 | True | False | percent annual growth | Sensitivity range, not sampling confidence interval |
| extreme exclusion diagnostic only | ingredient_cost_per_item_gbp | 1 | -0.039439 | -0.039439 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| extreme exclusion diagnostic only | net_ingredient_cost_gbp | 1 | -167,388.088837 | -167,388.088837 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| extreme exclusion diagnostic only | prescription_items | 1 | 46,648.621750 | 46,648.621750 | True | False | metric units/month | Sensitivity range, not sampling confidence interval |
| history cohorts | prescription_items | 2 | 0.201693 | 0.604190 | True | False | median observed-month CV | Sensitivity range, not sampling confidence interval |
| mean versus median | ingredient_cost_per_item_gbp | 2 | 1.312082 | 1.620331 | True | False | metric units | Sensitivity range, not sampling confidence interval |
| mean versus median | net_ingredient_cost_gbp | 2 | 8,234,836.005000 | 9,359,461.198056 | True | False | metric units | Sensitivity range, not sampling confidence interval |
| mean versus median | prescription_items | 2 | 5,889,506.555556 | 5,903,641.000000 | True | False | metric units | Sensitivity range, not sampling confidence interval |
| regional consistency | net_ingredient_cost_gbp | 7 | -31,439.458905 | -17,465.199279 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| regional consistency | prescription_items | 7 | 3,690.117632 | 13,335.064607 | True | False | metric units/month | Sensitivity range, not sampling confidence interval |
| robust trend | ingredient_cost_per_item_gbp | 1 | -0.048418 | -0.048418 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| robust trend | net_ingredient_cost_gbp | 1 | -238,635.842500 | -238,635.842500 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| robust trend | prescription_items | 1 | 47,729.625000 | 47,729.625000 | True | False | metric units/month | Sensitivity range, not sampling confidence interval |
| trend specification | ingredient_cost_per_item_gbp | 5 | -0.045833 | -0.039432 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| trend specification | net_ingredient_cost_gbp | 5 | -203,156.376875 | -167,339.592138 | False | True | metric units/month | Sensitivity range, not sampling confidence interval |
| trend specification | prescription_items | 5 | 45,642.274306 | 46,650.037066 | True | False | metric units/month | Sensitivity range, not sampling confidence interval |

All presentation effects, paired-region comparisons, growth distributions and forecast diagnostics are
exported as CSV/Parquet. Tables preserve dates, missingness, grouping keys and unit labels. Charts
summarize actual outputs, with source notes. Source data and previous calculations remain intact.
