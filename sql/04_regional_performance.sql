CREATE OR REPLACE VIEW phase2.vw_regional_monthly_trends AS
WITH a AS (
 SELECT month,region_code,SUM(prescription_items)::BIGINT AS prescription_items,SUM(net_ingredient_cost_gbp) AS net_ingredient_cost_gbp
 FROM phase2.fact_monthly_prescribing GROUP BY ALL
), b AS (
 SELECT m.month,m.calendar_year,r.region_code,r.region_name,a.prescription_items,a.net_ingredient_cost_gbp
 FROM phase2.dim_month m CROSS JOIN phase2.dim_region r LEFT JOIN a USING(month,region_code)
), c AS (
 SELECT *,LAG(prescription_items) OVER w AS previous_month_items,LAG(prescription_items,12) OVER w AS prior_year_items,
 LAG(net_ingredient_cost_gbp) OVER w AS previous_month_cost_gbp,LAG(net_ingredient_cost_gbp,12) OVER w AS prior_year_cost_gbp
 FROM b WINDOW w AS(PARTITION BY region_code ORDER BY month)
)
SELECT *,net_ingredient_cost_gbp/NULLIF(prescription_items,0) AS ingredient_cost_per_item_gbp,
 100.0*prescription_items/NULLIF(SUM(prescription_items) OVER(PARTITION BY month),0) AS items_share_pct,
 100.0*(prescription_items-previous_month_items)/NULLIF(previous_month_items,0) AS items_mom_growth_pct,
 100.0*(prescription_items-prior_year_items)/NULLIF(prior_year_items,0) AS items_yoy_growth_pct,
 100.0*(net_ingredient_cost_gbp-previous_month_cost_gbp)/NULLIF(previous_month_cost_gbp,0) AS cost_mom_growth_pct,
 100.0*(net_ingredient_cost_gbp-prior_year_cost_gbp)/NULLIF(prior_year_cost_gbp,0) AS cost_yoy_growth_pct,
 prescription_items-prior_year_items AS items_yoy_change,
 100.0*(prescription_items-prior_year_items)/NULLIF(SUM(prescription_items-prior_year_items) OVER(PARTITION BY month),0) AS national_yoy_change_contribution_pct
FROM c;
CREATE OR REPLACE VIEW phase2.vw_regional_annual_trends AS
WITH a AS (
 SELECT calendar_year,region_code,region_name,SUM(prescription_items)::BIGINT AS prescription_items,
 SUM(net_ingredient_cost_gbp) AS net_ingredient_cost_gbp,COUNT(prescription_items) AS observed_months
 FROM phase2.vw_regional_monthly_trends GROUP BY ALL
), b AS (
 SELECT *,LAG(prescription_items) OVER w AS prior_year_items,LAG(net_ingredient_cost_gbp) OVER w AS prior_year_cost_gbp,
 LAG(observed_months) OVER w AS prior_year_observed_months FROM a WINDOW w AS(PARTITION BY region_code ORDER BY calendar_year)
)
SELECT *,CASE WHEN observed_months=12 AND prior_year_observed_months=12 THEN 100.0*(prescription_items-prior_year_items)/NULLIF(prior_year_items,0) END AS items_annual_growth_pct,
 CASE WHEN observed_months=12 AND prior_year_observed_months=12 THEN 100.0*(net_ingredient_cost_gbp-prior_year_cost_gbp)/NULLIF(prior_year_cost_gbp,0) END AS cost_annual_growth_pct,
 prescription_items-prior_year_items AS annual_items_change,
 100.0*(prescription_items-prior_year_items)/NULLIF(SUM(prescription_items-prior_year_items) OVER(PARTITION BY calendar_year),0) AS national_annual_change_contribution_pct
FROM b;
CREATE OR REPLACE VIEW phase2.vw_regional_performance AS
WITH totals AS (
 SELECT region_code,region_name,SUM(prescription_items)::BIGINT AS prescription_items,SUM(net_ingredient_cost_gbp) AS net_ingredient_cost_gbp,
 STDDEV_SAMP(prescription_items ORDER BY month)/NULLIF(AVG(prescription_items),0) AS monthly_items_cv,
 MAX(CASE WHEN calendar_year=(SELECT MAX(calendar_year) FROM phase2.dim_month) THEN items_yoy_growth_pct END) AS maximum_latest_year_monthly_growth_pct
 FROM phase2.vw_regional_monthly_trends GROUP BY ALL
), endpoints AS (
 SELECT region_code,MAX(CASE WHEN calendar_year=YEAR(p.start_month) THEN prescription_items END) AS first_year_items,
 MAX(CASE WHEN calendar_year=YEAR(p.end_month) THEN prescription_items END) AS last_year_items,
 MAX(CASE WHEN calendar_year=YEAR(p.end_month) THEN items_annual_growth_pct END) AS latest_annual_items_growth_pct
 FROM phase2.vw_regional_annual_trends CROSS JOIN phase2.parameters p GROUP BY region_code
)
SELECT t.*,e.first_year_items,e.last_year_items,e.latest_annual_items_growth_pct,
 100.0*(last_year_items-first_year_items)/NULLIF(first_year_items,0) AS first_to_last_annual_items_growth_pct,
 100.0*prescription_items/NULLIF(SUM(prescription_items) OVER(),0) AS items_share_pct,
 100.0*net_ingredient_cost_gbp/NULLIF(SUM(net_ingredient_cost_gbp) OVER(),0) AS cost_share_pct,
 net_ingredient_cost_gbp/NULLIF(prescription_items,0) AS ingredient_cost_per_item_gbp,
 RANK() OVER(ORDER BY prescription_items DESC) AS items_rank,
 DENSE_RANK() OVER(ORDER BY net_ingredient_cost_gbp DESC) AS cost_rank,
 'unadjusted_no_population_denominator' AS comparison_basis
FROM totals t INNER JOIN endpoints e USING(region_code);
