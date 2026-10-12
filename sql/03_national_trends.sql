CREATE OR REPLACE VIEW phase2.vw_national_monthly_kpis AS
WITH totals AS (
 SELECT month,SUM(prescription_items)::BIGINT AS prescription_items,SUM(net_ingredient_cost_gbp) AS net_ingredient_cost_gbp,
 COUNT(DISTINCT region_code) AS observed_regions,COUNT(DISTINCT presentation_key) AS observed_presentations
 FROM phase2.fact_monthly_prescribing GROUP BY month
), spine AS (
 SELECT m.month,m.calendar_year,m.calendar_month,t.prescription_items,t.net_ingredient_cost_gbp,
 t.observed_regions,t.observed_presentations
 FROM phase2.dim_month m LEFT JOIN totals t USING(month)
), periods AS (
 SELECT *,LAG(prescription_items) OVER w AS previous_month_items,LAG(net_ingredient_cost_gbp) OVER w AS previous_month_cost_gbp,
 LAG(prescription_items,12) OVER w AS prior_year_items,LAG(net_ingredient_cost_gbp,12) OVER w AS prior_year_cost_gbp,
 CASE WHEN COUNT(prescription_items) OVER w3=3 THEN AVG(prescription_items) OVER w3 END AS items_rolling_3m,
 CASE WHEN COUNT(prescription_items) OVER w6=6 THEN AVG(prescription_items) OVER w6 END AS items_rolling_6m,
 CASE WHEN COUNT(prescription_items) OVER w12=12 THEN AVG(prescription_items) OVER w12 END AS items_rolling_12m,
 CASE WHEN COUNT(net_ingredient_cost_gbp) OVER w3=3 THEN AVG(net_ingredient_cost_gbp) OVER w3 END AS cost_rolling_3m_gbp,
 CASE WHEN COUNT(net_ingredient_cost_gbp) OVER w6=6 THEN AVG(net_ingredient_cost_gbp) OVER w6 END AS cost_rolling_6m_gbp,
 CASE WHEN COUNT(net_ingredient_cost_gbp) OVER w12=12 THEN AVG(net_ingredient_cost_gbp) OVER w12 END AS cost_rolling_12m_gbp
 FROM spine WINDOW w AS(ORDER BY month),w3 AS(ORDER BY month ROWS BETWEEN 2 PRECEDING AND CURRENT ROW),
 w6 AS(ORDER BY month ROWS BETWEEN 5 PRECEDING AND CURRENT ROW),w12 AS(ORDER BY month ROWS BETWEEN 11 PRECEDING AND CURRENT ROW)
)
SELECT *,net_ingredient_cost_gbp/NULLIF(prescription_items,0) AS ingredient_cost_per_item_gbp,
 100.0*(prescription_items-previous_month_items)/NULLIF(previous_month_items,0) AS items_mom_growth_pct,
 100.0*(net_ingredient_cost_gbp-previous_month_cost_gbp)/NULLIF(previous_month_cost_gbp,0) AS cost_mom_growth_pct,
 100.0*(prescription_items-prior_year_items)/NULLIF(prior_year_items,0) AS items_yoy_growth_pct,
 100.0*(net_ingredient_cost_gbp-prior_year_cost_gbp)/NULLIF(prior_year_cost_gbp,0) AS cost_yoy_growth_pct
FROM periods;
CREATE OR REPLACE VIEW phase2.vw_national_annual_kpis AS
WITH a AS (
 SELECT calendar_year,SUM(prescription_items)::BIGINT AS prescription_items,SUM(net_ingredient_cost_gbp) AS net_ingredient_cost_gbp,
 COUNT(prescription_items) AS observed_months FROM phase2.vw_national_monthly_kpis GROUP BY calendar_year
), b AS (
 SELECT *,LAG(prescription_items) OVER(ORDER BY calendar_year) AS prior_year_items,
 LAG(net_ingredient_cost_gbp) OVER(ORDER BY calendar_year) AS prior_year_cost_gbp,
 LAG(observed_months) OVER(ORDER BY calendar_year) AS prior_year_observed_months FROM a
)
SELECT *,net_ingredient_cost_gbp/NULLIF(prescription_items,0) AS ingredient_cost_per_item_gbp,
 CASE WHEN observed_months=12 AND prior_year_observed_months=12 THEN 100.0*(prescription_items-prior_year_items)/NULLIF(prior_year_items,0) END AS items_annual_growth_pct,
 CASE WHEN observed_months=12 AND prior_year_observed_months=12 THEN 100.0*(net_ingredient_cost_gbp-prior_year_cost_gbp)/NULLIF(prior_year_cost_gbp,0) END AS cost_annual_growth_pct
FROM b;
