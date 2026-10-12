-- Cross observed region and valid presentation-unit dimensions; do NOT cross incompatible units.
CREATE OR REPLACE VIEW phase2.vw_series_calendar AS
WITH bounds AS (
 SELECT region_code,presentation_key,MIN(month) AS first_observed_month,MAX(month) AS last_observed_month
 FROM phase2.fact_monthly_prescribing GROUP BY ALL
)
SELECT m.month,r.region_code,r.region_name,p.presentation_key,p.presentation_code,p.presentation_name,p.unit_of_measure,
 f.prescription_items,f.net_ingredient_cost_gbp,f.total_quantity,
 b.first_observed_month,b.last_observed_month,f.month IS NOT NULL AS is_observed,
 CASE WHEN f.month IS NOT NULL THEN 'observed'
      WHEN b.first_observed_month IS NULL THEN 'never_observed_applicability_unknown'
      WHEN m.month<b.first_observed_month THEN 'before_first_observation_not_proven_launch'
      WHEN m.month>b.last_observed_month THEN 'after_last_observation_not_proven_discontinuation'
      ELSE 'internal_gap_reporting_or_no_activity_unknown' END AS coverage_status
FROM phase2.dim_month m CROSS JOIN phase2.dim_region r CROSS JOIN phase2.dim_presentation p
LEFT JOIN phase2.fact_monthly_prescribing f USING(month,region_code,presentation_key)
LEFT JOIN bounds b USING(region_code,presentation_key);
CREATE OR REPLACE VIEW phase2.vw_series_coverage AS
WITH switches AS (
 SELECT *,CASE WHEN is_observed= LAG(is_observed) OVER(PARTITION BY region_code,presentation_key ORDER BY month)
 THEN 0 ELSE 1 END AS switched FROM phase2.vw_series_calendar
), islands AS (
 SELECT *,SUM(switched) OVER(PARTITION BY region_code,presentation_key ORDER BY month) AS island FROM switches
), runs AS (
 SELECT region_code,presentation_key,island,is_observed,COUNT(*) AS run_length FROM islands GROUP BY ALL
), lengths AS (
 SELECT region_code,presentation_key,
 COALESCE(MAX(CASE WHEN is_observed THEN run_length END),0) AS longest_consecutive_observed_run,
 COALESCE(MAX(CASE WHEN NOT is_observed THEN run_length END),0) AS longest_missing_interval
 FROM runs GROUP BY ALL
), summary AS (
 SELECT region_code,region_name,presentation_key,presentation_code,presentation_name,unit_of_measure,
 MIN(first_observed_month) AS first_observed_month,MAX(last_observed_month) AS last_observed_month,
 COUNT(*) AS window_months,COUNT(*) FILTER(WHERE is_observed) AS observed_month_count,
 COUNT(*) FILTER(WHERE coverage_status='internal_gap_reporting_or_no_activity_unknown') AS internal_missing_month_count,
 COUNT(*) FILTER(WHERE coverage_status='before_first_observation_not_proven_launch') AS before_first_observed_count,
 COUNT(*) FILTER(WHERE coverage_status='after_last_observation_not_proven_discontinuation') AS after_last_observed_count,
 COUNT(*) FILTER(WHERE coverage_status='never_observed_applicability_unknown') AS never_observed_month_count,
 COUNT(*) FILTER(WHERE NOT is_observed) AS full_window_missing_count,
 COUNT(*) FILTER(WHERE is_observed AND prescription_items=0) AS observed_zero_item_months,
 100.0*COUNT(*) FILTER(WHERE is_observed)/COUNT(*) AS full_window_coverage_pct
 FROM phase2.vw_series_calendar GROUP BY ALL
)
SELECT s.*,l.longest_consecutive_observed_run,l.longest_missing_interval FROM summary s INNER JOIN lengths l USING(region_code,presentation_key);
CREATE OR REPLACE VIEW phase2.vw_missing_series_months AS
SELECT * FROM phase2.vw_series_calendar WHERE NOT is_observed;
