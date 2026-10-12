# Independent numerical reconciliation

1,571 checks executed; 0 failed. Full machine evidence: `outputs/phase7/validation/numerical_reconciliation.csv`; its SHA-256 is `6d17d683db6ff2e67a22a8a9eba7fa30c279045dd72db6d2079eb2fac9a61bce`. A public copy is packaged with release validation evidence.

Independent here means a separate mathematical reduction, not merely calling a production function. Raw API item/NIC totals use Decimal sums, then reconcile source/clean/fact rows. Group identities and disclosed share denominators reconcile separately. A closed-form allocation of main, pairwise and triple interactions checks the production permutation-based cost decomposition. Forecast metrics use independent reductions on common five-family successful cells; origin-only scales are recomputed from historical observations. Pairwise less/equal counts check percentile midranks independently of pandas.rank. Explicit multiplicative algebra checks scenarios and reciprocal offsets. Dashboard functions are the observed side of comparisons against independently grouped facts.

| Metric | Expected | Recomputed | Difference | Tolerance | Status | Source |
|---|---:|---:|---:|---:|---|---|
| historical items | 212022236 | 212022236 | 0 | 0 | PASS | raw API → Phase 2 cost_analytics |
| historical NIC | 336940603.1 | 336940603.1 | 0 | 0.01 | PASS | raw API → Phase 2 cost_analytics |
| 2025 item annual growth | 7.579853497 | 7.579853497 | 8.882e-16 | 1e-08 | PASS | national_annual_trends vs fact annual sums |
| 2025 NIC annual growth | -39.93422397 | -39.93422397 | 0 | 1e-08 | PASS | national_annual_trends vs fact annual sums |
| 2025 vs 2024 item_volume_effect_gbp | 7478389.502 | 7478389.502 | 0 | 0.01 | PASS | closed-form interaction allocation; independent of permutation implementation |
| 2025 vs 2024 presentation_mix_effect_gbp | 1254765.299 | 1254765.299 | 1.816e-08 | 0.01 | PASS | closed-form interaction allocation; independent of permutation implementation |
| 2025 vs 2024 within_presentation_cost_per_item_effect_gbp | -59243626.55 | -59243626.55 | 0 | 0.01 | PASS | closed-form interaction allocation; independent of permutation implementation |
| 2025 vs 2024 decomposition sum | -50510471.75 | -50510471.75 | 0 | 0.01 | PASS | three-factor closed-form identity |
| national/damped_ets/MAE | 242210.5097 | 242210.5097 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/damped_ets/RMSE | 263898.1259 | 263898.1259 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/damped_ets/WAPE | 3.684099531 | 3.684099531 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/damped_ets/MASE | 0.8883230439 | 0.8883230439 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/damped_ets/Bias | -66774.10174 | -66774.10174 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/drift/MAE | 304846.1465 | 304846.1465 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/drift/RMSE | 353818.7673 | 353818.7673 | -5.821e-11 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/drift/WAPE | 4.636807656 | 4.636807656 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/drift/MASE | 1.118347825 | 1.118347825 | -2.22e-16 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/drift/Bias | -14172.72337 | -14172.72337 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/naive/MAE | 302008.6667 | 302008.6667 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/naive/RMSE | 360899.1196 | 360899.1196 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/naive/WAPE | 4.593648677 | 4.593648677 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/naive/MASE | 1.106999654 | 1.106999654 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/naive/Bias | -98475.73333 | -98475.73333 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/ridge_alpha_10/MAE | 237672.3376 | 237672.3376 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/ridge_alpha_10/RMSE | 265741.1905 | 265741.1905 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/ridge_alpha_10/WAPE | 3.615072478 | 3.615072478 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/ridge_alpha_10/MASE | 0.8716950253 | 0.8716950253 | 1.11e-16 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/ridge_alpha_10/Bias | -95573.74523 | -95573.74523 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/seasonal_naive/MAE | 445901.6667 | 445901.6667 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/seasonal_naive/RMSE | 486838.8336 | 486838.8336 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/seasonal_naive/WAPE | 6.782307355 | 6.782307355 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/seasonal_naive/MASE | 1.640422034 | 1.640422034 | 4.441e-16 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| national/seasonal_naive/Bias | -445901.6667 | -445901.6667 | 0 | 1e-06 | PASS | stored origin/horizon prediction rows; independent Python reductions |
| accounting offset 5 | -4.761904762 | -4.761904762 | 0 | 1e-10 | PASS | reciprocal multiplicative offset |
| 2023 dashboard items | 63715915 | 63715915 | 0 | 0 | PASS | dashboard totals vs independent grouped fact |
| 2023 dashboard weighted NIC/item | 2.110661596 | 2.110661596 | 0 | 1e-10 | PASS | dashboard totals vs independent aggregate ratio |
| 2024 dashboard items | 71445431 | 71445431 | 0 | 0 | PASS | dashboard totals vs independent grouped fact |
| 2024 dashboard weighted NIC/item | 1.770360515 | 1.770360515 | 0 | 1e-10 | PASS | dashboard totals vs independent aggregate ratio |
| 2025 dashboard items | 76860890 | 76860890 | 0 | 0 | PASS | dashboard totals vs independent grouped fact |
| 2025 dashboard weighted NIC/item | 0.9884571761 | 0.9884571761 | 0 | 1e-10 | PASS | dashboard totals vs independent aggregate ratio |

Unknown comparisons pass only when both sides are unavailable; no missing value is turned into zero. Integer sums have zero tolerance, GBP accounting uses £0.01, ratios/scores use explicit small floating tolerances. Repeated execution hashes are tested. No protected result is edited when a check fails; the discrepancy is investigated first. The earlier failed draft of this checker compared all successful model rows against paired-support metrics; it was corrected to match the documented denominator, with no analytical output changes.
