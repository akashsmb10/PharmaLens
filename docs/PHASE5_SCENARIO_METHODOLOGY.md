# Phase 5 scenario methodology

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
