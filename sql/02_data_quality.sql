CREATE OR REPLACE VIEW phase2.vw_model_quality AS
SELECT 'fact_duplicate_keys' AS check_name, COUNT(*)::BIGINT AS failure_count FROM (
 SELECT month,region_code,presentation_key FROM phase2.fact_monthly_prescribing GROUP BY ALL HAVING COUNT(*)>1)
UNION ALL SELECT 'missing_month_foreign_key',COUNT(*) FROM phase2.fact_monthly_prescribing f LEFT JOIN phase2.dim_month d USING(month) WHERE d.month IS NULL
UNION ALL SELECT 'missing_region_foreign_key',COUNT(*) FROM phase2.fact_monthly_prescribing f LEFT JOIN phase2.dim_region d USING(region_code) WHERE d.region_code IS NULL
UNION ALL SELECT 'missing_presentation_foreign_key',COUNT(*) FROM phase2.fact_monthly_prescribing f LEFT JOIN phase2.dim_presentation d USING(presentation_key) WHERE d.presentation_key IS NULL
UNION ALL SELECT 'join_row_count_difference',ABS((SELECT COUNT(*) FROM phase2.vw_fact_enriched)-(SELECT COUNT(*) FROM phase2.fact_monthly_prescribing))
UNION ALL SELECT 'negative_items_or_quantity',COUNT(*) FROM phase2.fact_monthly_prescribing WHERE prescription_items<0 OR total_quantity<0;

-- Independently reproduce Phase 1's three-IQR method per observed region/presentation/metric.
CREATE OR REPLACE VIEW phase2.vw_metric_observations AS
SELECT month,region_code,presentation_key,'items' AS metric,prescription_items::DOUBLE AS value FROM phase2.fact_monthly_prescribing
UNION ALL SELECT month,region_code,presentation_key,'nic_gbp',net_ingredient_cost_gbp::DOUBLE FROM phase2.fact_monthly_prescribing
UNION ALL SELECT month,region_code,presentation_key,'total_quantity',total_quantity FROM phase2.fact_monthly_prescribing;
CREATE OR REPLACE VIEW phase2.vw_metric_neighbors AS
SELECT *, LAG(value) OVER w AS previous_observed_value, LEAD(value) OVER w AS next_observed_value,
 LAG(month) OVER w AS previous_observed_month, LEAD(month) OVER w AS next_observed_month
FROM phase2.vw_metric_observations
WINDOW w AS (PARTITION BY region_code,presentation_key,metric ORDER BY month);
CREATE OR REPLACE VIEW phase2.vw_extreme_value_review AS
WITH fences AS (
 SELECT region_code,presentation_key,metric,COUNT(*) AS observed_months,
 QUANTILE_CONT(value,.25) AS q1,QUANTILE_CONT(value,.75) AS q3
 FROM phase2.vw_metric_observations GROUP BY ALL
), flagged AS (
 SELECT n.*,q1,q3,q1-3*(q3-q1) AS lower_fence,q3+3*(q3-q1) AS upper_fence
 FROM phase2.vw_metric_neighbors n INNER JOIN fences f USING(region_code,presentation_key,metric)
 WHERE observed_months>=12 AND q3>q1 AND (value<q1-3*(q3-q1) OR value>q3+3*(q3-q1))
)
SELECT x.*,p.presentation_code,p.presentation_name,p.unit_of_measure,r.region_name,
 'three_IQR_per_series_metric_minimum_12_observations' AS detection_method,
 DATE_DIFF('month',previous_observed_month,x.month) AS months_since_previous_observation,
 DATE_DIFF('month',x.month,next_observed_month) AS months_until_next_observation,
 f.net_ingredient_cost_gbp/NULLIF(f.prescription_items,0) AS ingredient_cost_per_item_gbp,
 f.prescription_items AS current_prescription_items,f.total_quantity AS current_total_quantity,
 f.net_ingredient_cost_gbp AS current_net_ingredient_cost_gbp,
 previous.net_ingredient_cost_gbp/NULLIF(previous.prescription_items,0) AS previous_calendar_cost_per_item_gbp,
 100.0*(f.net_ingredient_cost_gbp/NULLIF(f.prescription_items,0)-previous.net_ingredient_cost_gbp/NULLIF(previous.prescription_items,0))
 /NULLIF(previous.net_ingredient_cost_gbp/NULLIF(previous.prescription_items,0),0) AS cost_per_item_mom_change_pct,
 'review_required_no_error_or_causal_attribution_established' AS interpretation
FROM flagged x INNER JOIN phase2.dim_presentation p USING(presentation_key)
INNER JOIN phase2.dim_region r USING(region_code)
INNER JOIN phase2.fact_monthly_prescribing f USING(month,region_code,presentation_key)
LEFT JOIN phase2.fact_monthly_prescribing previous
 ON previous.region_code=x.region_code AND previous.presentation_key=x.presentation_key
 AND previous.month=x.month-INTERVAL '1 month';
