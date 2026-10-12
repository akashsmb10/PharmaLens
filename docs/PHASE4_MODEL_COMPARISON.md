# Phase 4 model comparison

Development selection is frozen before holdout evaluation. Do not replace the selected family with
the lowest holdout score. Tables derive from stored predictions. Failure cells are removed for all
families on common support; selected-model summaries preserve all successful selected opportunities.

## Development family comparison (frozen Ridge alpha)

| aggregation_level | model | variant | n | MAE | RMSE | WAPE | sMAPE | MASE | Bias | mase_defined_rows |
|---|---|---|---|---|---|---|---|---|---|---|
| national | damped_ets | damped_ets | 15 | 168,055.456238 | 229,620.081403 | 2.691962 | 2.706167 | 0.652526 | 62,442.272799 | 15 |
| national | drift | drift | 15 | 303,784.071650 | 366,087.379256 | 4.866103 | 4.895977 | 1.172038 | 40,688.433840 | 15 |
| national | naive | naive | 15 | 284,146.866667 | 353,322.859010 | 4.551548 | 4.615488 | 1.089972 | -42,767.666667 | 15 |
| national | ridge | ridge_alpha_10 | 15 | 217,136.381345 | 270,291.370981 | 3.478155 | 3.504938 | 0.833626 | -33,637.229674 | 15 |
| national | seasonal_naive | seasonal_naive | 15 | 456,850.466667 | 471,004.002197 | 7.317966 | 7.586315 | 1.746027 | -456,850.466667 | 15 |
| region_presentation | damped_ets | damped_ets | 417 | 6,050.363941 | 10,044.643843 | 2.721108 | 2.834329 | 0.654421 | 2,068.193934 | 417 |
| region_presentation | drift | drift | 417 | 10,879.246032 | 16,602.678660 | 4.892864 | 4.895235 | 1.129692 | 1,572.687623 | 417 |
| region_presentation | naive | naive | 417 | 10,236.359712 | 16,162.745001 | 4.603730 | 4.703550 | 1.074559 | -1,402.685851 | 417 |
| region_presentation | ridge | ridge_alpha_10 | 417 | 8,189.798062 | 12,498.798906 | 3.683304 | 3.921556 | 0.899724 | -420.813799 | 417 |
| region_presentation | seasonal_naive | seasonal_naive | 417 | 18,346.839329 | 26,359.512509 | 8.251361 | 8.024107 | 1.810395 | -16,265.558753 | 417 |
| regional | damped_ets | damped_ets | 105 | 23,501.225728 | 33,332.769115 | 2.635147 | 2.665781 | 0.650488 | 7,383.090453 | 105 |
| regional | drift | drift | 105 | 43,599.478911 | 55,565.335839 | 4.888725 | 4.873350 | 1.179374 | 5,812.633406 | 105 |
| regional | naive | naive | 105 | 40,879.400000 | 53,841.727278 | 4.583728 | 4.600869 | 1.099455 | -6,109.666667 | 105 |
| regional | ridge | ridge_alpha_10 | 105 | 31,118.910374 | 40,884.306796 | 3.489303 | 3.476664 | 0.836897 | -4,191.709755 | 105 |
| regional | seasonal_naive | seasonal_naive | 105 | 65,928.714286 | 79,814.465679 | 7.392459 | 7.202698 | 1.671585 | -65,264.352381 | 105 |

## Development selection decisions

| aggregation_level | selected_model | selected_variant | selection_metric | development_score | runner_up | eligible_models | selection_sample_size | series_sample_size | selection_scope | tie_threshold_relative | tie_breaking_reason | frozen_at |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| national | damped_ets | damped_ets | MASE | 0.652526 | ridge_alpha_10 | damped_ets;drift;naive;ridge_alpha_0.1;ridge_alpha_1;ridge_alpha_10;ridge_alpha_100;seasonal_naive | 15 | 15 | Shared by aggregation level; pooled mean scaled absolute error | 0.020000 | Simplicity preference within relative MASE tolerance; deterministic alpha tie break | 2025-06-01 00:00:00 |
| region_presentation | ridge | ridge_alpha_10 | MASE | 0.897394 | ridge_alpha_1 | drift;naive;ridge_alpha_0.1;ridge_alpha_1;ridge_alpha_10;ridge_alpha_100;seasonal_naive | 420 | 15 | Shared by aggregation level; pooled mean scaled absolute error | 0.020000 | Simplicity preference within relative MASE tolerance; deterministic alpha tie break | 2025-06-01 00:00:00 |
| regional | damped_ets | damped_ets | MASE | 0.650488 | ridge_alpha_10 | damped_ets;drift;naive;ridge_alpha_0.1;ridge_alpha_1;ridge_alpha_10;ridge_alpha_100;seasonal_naive | 105 | 15 | Shared by aggregation level; pooled mean scaled absolute error | 0.020000 | Simplicity preference within relative MASE tolerance; deterministic alpha tie break | 2025-06-01 00:00:00 |

## Final holdout family comparison

| aggregation_level | model | variant | n | MAE | RMSE | WAPE | sMAPE | MASE | Bias | mase_defined_rows |
|---|---|---|---|---|---|---|---|---|---|---|
| national | damped_ets | damped_ets | 15 | 242,210.509664 | 263,898.125872 | 3.684100 | 3.694201 | 0.888323 | -66,774.101742 | 15 |
| national | drift | drift | 15 | 304,846.146525 | 353,818.767287 | 4.636808 | 4.651418 | 1.118348 | -14,172.723371 | 15 |
| national | naive | naive | 15 | 302,008.666667 | 360,899.119551 | 4.593649 | 4.621575 | 1.107000 | -98,475.733333 | 15 |
| national | ridge | ridge_alpha_10 | 15 | 237,672.337558 | 265,741.190491 | 3.615072 | 3.623867 | 0.871695 | -95,573.745229 | 15 |
| national | seasonal_naive | seasonal_naive | 15 | 445,901.666667 | 486,838.833631 | 6.782307 | 6.968013 | 1.640422 | -445,901.666667 | 15 |
| region_presentation | damped_ets | damped_ets | 417 | 8,799.546039 | 12,119.015662 | 3.746997 | 3.773084 | 0.885641 | -2,754.687413 | 417 |
| region_presentation | drift | drift | 417 | 10,914.442648 | 16,226.851476 | 4.647557 | 4.617762 | 1.075119 | -528.511383 | 417 |
| region_presentation | naive | naive | 417 | 11,042.609113 | 16,527.207460 | 4.702132 | 4.709791 | 1.097024 | -3,522.829736 | 417 |
| region_presentation | ridge | ridge_alpha_10 | 417 | 8,705.099318 | 12,018.693522 | 3.706780 | 3.828928 | 0.893876 | -2,693.838607 | 417 |
| region_presentation | seasonal_naive | seasonal_naive | 417 | 17,452.093525 | 24,933.343004 | 7.431400 | 7.303474 | 1.700044 | -15,784.050360 | 417 |
| regional | damped_ets | damped_ets | 105 | 35,399.647805 | 40,625.700926 | 3.769080 | 3.766715 | 0.914208 | -12,045.747643 | 105 |
| regional | drift | drift | 105 | 43,651.034143 | 53,928.667758 | 4.647624 | 4.609686 | 1.117376 | -2,024.674767 | 105 |
| regional | naive | naive | 105 | 43,689.180952 | 54,868.869716 | 4.651685 | 4.638976 | 1.120797 | -14,067.961905 | 105 |
| regional | ridge | ridge_alpha_10 | 105 | 34,211.975906 | 40,166.077492 | 3.642626 | 3.643738 | 0.885645 | -13,593.125966 | 105 |
| regional | seasonal_naive | seasonal_naive | 105 | 63,700.238095 | 77,230.137138 | 6.782307 | 6.660722 | 1.584009 | -63,700.238095 | 105 |

## National horizon comparison: final holdout

| split_type | aggregation_level | model | variant | horizon | n | MAE | RMSE | WAPE | sMAPE | MASE | Bias | mase_defined_rows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| holdout | national | damped_ets | damped_ets | 1 | 6 | 274,536.059637 | 293,105.666325 | 4.175892 | 4.194346 | 1.007852 | -78,754.087158 | 6 |
| holdout | national | damped_ets | damped_ets | 2 | 5 | 207,187.641873 | 233,248.519833 | 3.167205 | 3.163615 | 0.758500 | -26,982.634102 | 5 |
| holdout | national | damped_ets | damped_ets | 3 | 4 | 237,500.769444 | 253,546.525695 | 3.589913 | 3.607215 | 0.871309 | -98,543.458169 | 4 |
| holdout | national | drift | drift | 1 | 6 | 434,320.215739 | 467,213.787886 | 6.606325 | 6.641494 | 1.591797 | -64,763.462204 | 6 |
| holdout | national | drift | drift | 2 | 5 | 261,616.445895 | 300,152.041822 | 3.999239 | 3.999907 | 0.958718 | 60,534.408358 | 5 |
| holdout | national | drift | drift | 3 | 4 | 164,672.168493 | 171,484.123664 | 2.489082 | 2.480693 | 0.607711 | -31,670.529783 | 4 |
| holdout | national | naive | naive | 1 | 6 | 443,098.500000 | 468,708.981361 | 6.739849 | 6.796739 | 1.623444 | -108,865.833333 | 6 |
| holdout | national | naive | naive | 2 | 5 | 240,096.800000 | 288,467.907748 | 3.670276 | 3.673850 | 0.875818 | -31,629.200000 | 5 |
| holdout | national | naive | naive | 3 | 4 | 167,763.750000 | 234,267.631745 | 2.535812 | 2.543485 | 0.621309 | -166,448.750000 | 4 |
| holdout | national | ridge | ridge_alpha_10 | 1 | 6 | 267,836.599293 | 287,197.623506 | 4.073989 | 4.091226 | 0.982931 | -96,350.949138 | 6 |
| holdout | national | ridge | ridge_alpha_10 | 2 | 5 | 214,048.028361 | 253,478.350821 | 3.272077 | 3.266469 | 0.783537 | -68,477.722396 | 5 |
| holdout | national | ridge | ridge_alpha_10 | 3 | 4 | 221,956.331451 | 246,538.274664 | 3.354953 | 3.369575 | 0.815039 | -128,277.967909 | 4 |
| holdout | national | seasonal_naive | seasonal_naive | 1 | 6 | 439,268.166667 | 478,378.440996 | 6.681587 | 6.859874 | 1.605267 | -439,268.166667 | 6 |
| holdout | national | seasonal_naive | seasonal_naive | 2 | 5 | 424,408.600000 | 471,025.596014 | 6.487786 | 6.646962 | 1.561401 | -424,408.600000 | 5 |
| holdout | national | seasonal_naive | seasonal_naive | 3 | 4 | 482,718.250000 | 517,875.369081 | 7.296468 | 7.531535 | 1.791931 | -482,718.250000 | 4 |

## Lowest development MASE by horizon (diagnostic, not separate operational selection)

| horizon | model | variant | n | MASE | MAE | WAPE |
|---|---|---|---|---|---|---|
| 1 | damped_ets | damped_ets | 6 | 0.692050 | 177,130.113211 | 2.840518 |
| 2 | damped_ets | damped_ets | 5 | 0.729139 | 188,441.705923 | 3.038994 |
| 3 | damped_ets | damped_ets | 4 | 0.497473 | 128,960.658672 | 2.045053 |

## Lowest observed holdout MASE by horizon (descriptive only)

| horizon | model | variant | n | MASE | MAE | WAPE |
|---|---|---|---|---|---|---|
| 1 | ridge | ridge_alpha_10 | 6 | 0.982931 | 267,836.599293 | 4.073989 |
| 2 | damped_ets | damped_ets | 5 | 0.758500 | 207,187.641873 | 3.167205 |
| 3 | drift | drift | 4 | 0.607711 | 164,672.168493 | 2.489082 |

## Frozen selected national model by horizon

| split_type | aggregation_level | horizon | n | MAE | RMSE | WAPE | sMAPE | MASE | Bias | mase_defined_rows |
|---|---|---|---|---|---|---|---|---|---|---|
| holdout | national | 1 | 6 | 274,536.059637 | 293,105.666325 | 4.175892 | 4.194346 | 1.007852 | -78,754.087158 | 6 |
| holdout | national | 2 | 5 | 207,187.641873 | 233,248.519833 | 3.167205 | 3.163615 | 0.758500 | -26,982.634102 | 5 |
| holdout | national | 3 | 4 | 237,500.769444 | 253,546.525695 | 3.589913 | 3.607215 | 0.871309 | -98,543.458169 | 4 |

## Regional selected-model performance

| split_type | region_code | region_name | model | variant | n | MAE | RMSE | WAPE | sMAPE | MASE | Bias | mase_defined_rows |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| holdout | Y56 | LONDON | damped_ets | damped_ets | 15 | 31,471.902746 | 35,627.339785 | 3.687662 | 3.703811 | 0.902890 | -21,713.342601 | 15 |
| holdout | Y58 | SOUTH WEST | damped_ets | damped_ets | 15 | 21,800.882933 | 23,984.267833 | 3.643091 | 3.651080 | 0.916923 | -6,316.624845 | 15 |
| holdout | Y59 | SOUTH EAST | damped_ets | damped_ets | 15 | 30,132.669040 | 33,208.513704 | 3.863861 | 3.869299 | 1.027080 | -10,646.514166 | 15 |
| holdout | Y60 | MIDLANDS | damped_ets | damped_ets | 15 | 49,344.811800 | 53,421.475968 | 3.866114 | 3.879283 | 0.889676 | -13,145.282519 | 15 |
| holdout | Y61 | EAST OF ENGLAND | damped_ets | damped_ets | 15 | 25,807.123375 | 28,140.649736 | 3.423911 | 3.430253 | 0.866515 | -8,727.364699 | 15 |
| holdout | Y62 | NORTH WEST | damped_ets | damped_ets | 15 | 34,610.538881 | 37,631.853685 | 4.072453 | 4.087773 | 0.928264 | -8,786.275103 | 15 |
| holdout | Y63 | NORTH EAST AND YORKSHIRE | damped_ets | damped_ets | 15 | 54,629.605862 | 59,530.400052 | 3.734525 | 3.745505 | 0.868110 | -14,984.829570 | 15 |

## Failures and coverage

| split_type | aggregation_level | model | failed_forecasts |
|---|---|---|---|
| development | region_presentation | damped_ets | 3 |
| holdout | region_presentation | damped_ets | 3 |

Every failure remains a row in model_failures.csv and backtest_predictions.csv, with origin,
target, horizon, requested model and optimizer warnings/status. Any failed development opportunity
excludes that configuration from shared-level selection. A lower successful-row score does not
override this guard. Metrics based on different supports are not silently ranked together.
Region/presentation common-support comparisons lose the ETS-failed cells for every family; the
selected Ridge all-opportunity summary includes those cells and therefore has a different n.

## Hierarchical forecast comparison

| split_type | horizon | n | MAE | RMSE | WAPE | sMAPE | MASE | Bias | mase_defined_rows | approach |
|---|---|---|---|---|---|---|---|---|---|---|
| development | 1 | 6 | 177,130.113211 | 248,013.612787 | 2.840518 | 2.862044 | 0.692050 | 50,370.985455 | 6 | direct_national |
| development | 2 | 5 | 188,441.705923 | 261,458.244771 | 3.038994 | 3.055202 | 0.729139 | 103,127.783564 | 5 | direct_national |
| development | 3 | 4 | 128,960.658672 | 141,433.858387 | 2.045053 | 2.036059 | 0.497473 | 29,692.315357 | 4 | direct_national |
| holdout | 1 | 6 | 274,536.059637 | 293,105.666325 | 4.175892 | 4.194346 | 1.007852 | -78,754.087158 | 6 | direct_national |
| holdout | 2 | 5 | 207,187.641873 | 233,248.519833 | 3.167205 | 3.163615 | 0.758500 | -26,982.634102 | 5 | direct_national |
| holdout | 3 | 4 | 237,500.769444 | 253,546.525695 | 3.589913 | 3.607215 | 0.871309 | -98,543.458169 | 4 | direct_national |
| development | 1 | 6 | 175,239.393851 | 242,812.473450 | 2.810197 | 2.832724 | 0.684555 | 41,100.260255 | 6 | sum_all_seven_regions |
| development | 2 | 5 | 179,515.218298 | 250,612.040439 | 2.895037 | 2.914093 | 0.693894 | 92,657.089084 | 5 | sum_all_seven_regions |
| development | 3 | 4 | 117,996.908406 | 131,880.700548 | 1.871190 | 1.863795 | 0.453893 | 16,334.372657 | 4 | sum_all_seven_regions |
| holdout | 1 | 6 | 271,170.292007 | 289,263.985406 | 4.124696 | 4.143279 | 0.995085 | -94,685.167046 | 6 | sum_all_seven_regions |
| holdout | 2 | 5 | 218,615.610522 | 241,022.241784 | 3.341900 | 3.337873 | 0.800588 | -46,232.284842 | 5 | sum_all_seven_regions |
| holdout | 3 | 4 | 249,215.803725 | 264,623.915950 | 3.766991 | 3.786290 | 0.914915 | -116,382.769014 | 4 | sum_all_seven_regions |

Direct and regional-sum forecasts remain separate. Coherence differences are not corrected or
declared statistical errors. Screened presentation series do not form a complete national total.
