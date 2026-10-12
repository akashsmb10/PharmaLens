CREATE OR REPLACE VIEW phase2.vw_presentation_monthly_trends AS
WITH a AS (
 SELECT month,presentation_key,SUM(prescription_items)::BIGINT AS prescription_items,
 SUM(net_ingredient_cost_gbp) AS net_ingredient_cost_gbp,SUM(total_quantity) AS total_quantity,
 COUNT(DISTINCT region_code) AS observed_regions FROM phase2.fact_monthly_prescribing GROUP BY ALL
), b AS (
 SELECT m.month,m.calendar_year,p.*,a.prescription_items,a.net_ingredient_cost_gbp,a.total_quantity,a.observed_regions
 FROM phase2.dim_month m CROSS JOIN phase2.dim_presentation p LEFT JOIN a USING(month,presentation_key)
), c AS (
 SELECT *,LAG(prescription_items) OVER w AS previous_month_items,LAG(prescription_items,12) OVER w AS prior_year_items,
 LAG(net_ingredient_cost_gbp) OVER w AS previous_month_cost_gbp,
 LAG(net_ingredient_cost_gbp,12) OVER w AS prior_year_cost_gbp,
 LAG(100.0*prescription_items/NULLIF(national_items,0),12) OVER w AS prior_year_items_share_pct
 FROM (SELECT *,SUM(prescription_items) OVER(PARTITION BY month) AS national_items FROM b)
 WINDOW w AS(PARTITION BY presentation_key ORDER BY month)
)
SELECT *,100.0*prescription_items/NULLIF(national_items,0) AS items_share_pct,
 100.0*prescription_items/NULLIF(national_items,0)-prior_year_items_share_pct AS items_share_yoy_change_pp,
 net_ingredient_cost_gbp/NULLIF(prescription_items,0) AS ingredient_cost_per_item_gbp,
 100.0*(prescription_items-previous_month_items)/NULLIF(previous_month_items,0) AS items_mom_growth_pct,
 100.0*(prescription_items-prior_year_items)/NULLIF(prior_year_items,0) AS items_yoy_growth_pct,
 100.0*(net_ingredient_cost_gbp-previous_month_cost_gbp)/NULLIF(previous_month_cost_gbp,0) AS cost_mom_growth_pct,
 100.0*(net_ingredient_cost_gbp-prior_year_cost_gbp)/NULLIF(prior_year_cost_gbp,0) AS cost_yoy_growth_pct,
 prescription_items-prior_year_items AS items_yoy_change,
 100.0*(prescription_items-prior_year_items)/NULLIF(SUM(prescription_items-prior_year_items) OVER(PARTITION BY month),0) AS national_yoy_change_contribution_pct
FROM c;
CREATE OR REPLACE VIEW phase2.vw_presentation_annual_trends AS
WITH a AS (
 SELECT calendar_year,presentation_key,presentation_code,presentation_name,unit_of_measure,
 SUM(prescription_items)::BIGINT AS prescription_items,SUM(net_ingredient_cost_gbp) AS net_ingredient_cost_gbp,
 SUM(total_quantity) AS total_quantity,COUNT(prescription_items) AS observed_months
 FROM phase2.vw_presentation_monthly_trends GROUP BY ALL
), b AS (
 SELECT *,LAG(prescription_items) OVER w AS prior_year_items,LAG(net_ingredient_cost_gbp) OVER w AS prior_year_cost_gbp,
 LAG(observed_months) OVER w AS prior_year_observed_months FROM a WINDOW w AS(PARTITION BY presentation_key ORDER BY calendar_year)
)
SELECT *,100.0*prescription_items/NULLIF(SUM(prescription_items) OVER(PARTITION BY calendar_year),0) AS items_share_pct,
 CASE WHEN observed_months=12 AND prior_year_observed_months=12 THEN 100.0*(prescription_items-prior_year_items)/NULLIF(prior_year_items,0) END AS items_annual_growth_pct,
 CASE WHEN observed_months=12 AND prior_year_observed_months=12 THEN 100.0*(net_ingredient_cost_gbp-prior_year_cost_gbp)/NULLIF(prior_year_cost_gbp,0) END AS cost_annual_growth_pct,
 net_ingredient_cost_gbp-prior_year_cost_gbp AS observed_cost_change_gbp,
 100.0*(net_ingredient_cost_gbp-prior_year_cost_gbp)/NULLIF(SUM(net_ingredient_cost_gbp-prior_year_cost_gbp) OVER(PARTITION BY calendar_year),0) AS observed_cost_change_contribution_pct
FROM b;
CREATE OR REPLACE VIEW phase2.vw_presentation_performance AS
WITH a AS (
 SELECT presentation_key,presentation_code,presentation_name,unit_of_measure,
 SUM(prescription_items)::BIGINT AS prescription_items,SUM(net_ingredient_cost_gbp) AS net_ingredient_cost_gbp,
 SUM(total_quantity) AS total_quantity,COUNT(prescription_items) AS observed_national_months
 FROM phase2.vw_presentation_monthly_trends GROUP BY ALL
), b AS (
 SELECT *,100.0*prescription_items/NULLIF(SUM(prescription_items) OVER(),0) AS items_share_pct,
 100.0*net_ingredient_cost_gbp/NULLIF(SUM(net_ingredient_cost_gbp) OVER(),0) AS cost_share_pct FROM a
)
SELECT *,net_ingredient_cost_gbp/NULLIF(prescription_items,0) AS ingredient_cost_per_item_gbp,
 net_ingredient_cost_gbp/NULLIF(total_quantity,0) AS ingredient_cost_per_native_unit_gbp,
 RANK() OVER(ORDER BY prescription_items DESC) AS items_rank,
 RANK() OVER(ORDER BY net_ingredient_cost_gbp DESC) AS cost_rank,
 -- Native-unit ranking is descriptive; strengths/forms differ even within one physical unit.
 RANK() OVER(PARTITION BY unit_of_measure ORDER BY total_quantity DESC) AS native_quantity_rank,
 SUM(items_share_pct) OVER(ORDER BY prescription_items DESC,presentation_key ROWS UNBOUNDED PRECEDING) AS cumulative_items_share_pct
FROM b;
CREATE OR REPLACE VIEW phase2.vw_presentation_concentration AS
WITH a AS (
 SELECT *,ROW_NUMBER() OVER(ORDER BY prescription_items DESC,presentation_key) AS pareto_position
 FROM phase2.vw_presentation_performance
)
SELECT *,SUM(POWER(items_share_pct/100.0,2)) OVER() AS items_hhi_0_to_1,
 SUM(CASE WHEN pareto_position<=4 THEN items_share_pct ELSE 0 END) OVER() AS top_four_items_share_pct,
 CASE WHEN cumulative_items_share_pct-items_share_pct<80 THEN TRUE ELSE FALSE END AS needed_to_reach_80pct
FROM a;
