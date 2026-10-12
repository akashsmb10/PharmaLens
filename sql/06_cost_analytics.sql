-- Ratios use aggregated numerators/denominators, not a mean of row-level ratios.
CREATE OR REPLACE VIEW phase2.vw_cost_analytics AS
WITH a AS (
 SELECT month,region_code,presentation_key,presentation_code,presentation_name,region_name,unit_of_measure,
 prescription_items,net_ingredient_cost_gbp,total_quantity,
 net_ingredient_cost_gbp/NULLIF(prescription_items,0) AS ingredient_cost_per_item_gbp,
 net_ingredient_cost_gbp/NULLIF(total_quantity,0) AS ingredient_cost_per_native_unit_gbp,
 net_ingredient_cost_gbp*100.0/NULLIF(total_quantity,0) AS ingredient_cost_per_100_native_units_gbp
 FROM phase2.vw_fact_enriched
), b AS (
 SELECT *,LAG(ingredient_cost_per_item_gbp) OVER w AS previous_observed_cost_per_item_gbp,
 LAG(month) OVER w AS previous_observed_month FROM a WINDOW w AS(PARTITION BY region_code,presentation_key ORDER BY month)
)
SELECT *,CASE WHEN DATE_DIFF('month',previous_observed_month,month)=1
 THEN 100.0*(ingredient_cost_per_item_gbp-previous_observed_cost_per_item_gbp)/NULLIF(previous_observed_cost_per_item_gbp,0)
 END AS cost_per_item_mom_growth_pct,
 'per_100_tablets_or_100ml_within_identical_presentation_not_dose_equivalent' AS quantity_comparison_basis
FROM b;
-- Exact symmetric two-factor identity: C=V*P, with P=aggregate cost/item (includes mix).
-- No claim that the unit-cost effect isolates prices or clinical presentation substitution.
CREATE OR REPLACE VIEW phase2.vw_cost_change_decomposition AS
WITH periods AS (
 SELECT 'monthly' AS comparison_type,month AS period,prescription_items,net_ingredient_cost_gbp,
 previous_month_items AS baseline_items,previous_month_cost_gbp AS baseline_cost_gbp
 FROM phase2.vw_national_monthly_kpis
 UNION ALL
 SELECT 'annual',MAKE_DATE(calendar_year,1,1),prescription_items,net_ingredient_cost_gbp,prior_year_items,prior_year_cost_gbp
 FROM phase2.vw_national_annual_kpis WHERE observed_months=12 AND prior_year_observed_months=12
), a AS (
 SELECT *,net_ingredient_cost_gbp/NULLIF(prescription_items,0) AS current_cost_per_item_gbp,
 baseline_cost_gbp/NULLIF(baseline_items,0) AS baseline_cost_per_item_gbp
 FROM periods WHERE baseline_items IS NOT NULL
), b AS (
 SELECT *,net_ingredient_cost_gbp-baseline_cost_gbp AS observed_cost_change_gbp,
 (prescription_items-baseline_items)*(current_cost_per_item_gbp+baseline_cost_per_item_gbp)/2.0 AS item_volume_effect_gbp,
 (current_cost_per_item_gbp-baseline_cost_per_item_gbp)*(prescription_items+baseline_items)/2.0 AS aggregate_unit_cost_and_mix_effect_gbp
 FROM a
)
SELECT *,observed_cost_change_gbp-item_volume_effect_gbp-aggregate_unit_cost_and_mix_effect_gbp AS reconciliation_residual_gbp,
 'symmetric_exact_two_factor_cost_per_item_contains_presentation_mix' AS method
FROM b;
