CREATE OR REPLACE VIEW phase2.vw_region_presentation_mix AS
SELECT region_code,region_name,presentation_key,presentation_code,presentation_name,unit_of_measure,
 SUM(prescription_items)::BIGINT AS prescription_items,SUM(net_ingredient_cost_gbp) AS net_ingredient_cost_gbp,
 100.0*SUM(prescription_items)/NULLIF(SUM(SUM(prescription_items)) OVER(PARTITION BY region_code),0) AS regional_items_mix_pct
FROM phase2.vw_fact_enriched
GROUP BY region_code,region_name,presentation_key,presentation_code,presentation_name,unit_of_measure;
CREATE OR REPLACE VIEW phase2.vw_region_presentation_summary AS
WITH a AS (
 SELECT region_code,presentation_key,SUM(prescription_items)::BIGINT AS prescription_items,
 SUM(net_ingredient_cost_gbp) AS net_ingredient_cost_gbp,
 STDDEV_SAMP(prescription_items ORDER BY month)/NULLIF(AVG(prescription_items),0) AS monthly_items_cv,
 SUM(CASE WHEN month>=p.end_month-INTERVAL '11 months' THEN prescription_items END)::BIGINT AS recent_12m_items,
 SUM(CASE WHEN month BETWEEN p.end_month-INTERVAL '23 months' AND p.end_month-INTERVAL '12 months' THEN prescription_items END)::BIGINT AS previous_12m_items,
 COUNT(*) FILTER(WHERE month>=p.end_month-INTERVAL '11 months') AS recent_12m_observed,
 COUNT(*) FILTER(WHERE month BETWEEN p.end_month-INTERVAL '23 months' AND p.end_month-INTERVAL '12 months') AS previous_12m_observed
 FROM phase2.fact_monthly_prescribing CROSS JOIN phase2.parameters p GROUP BY region_code,presentation_key
), b AS (
 SELECT c.*,a.prescription_items,a.net_ingredient_cost_gbp,a.monthly_items_cv,a.recent_12m_items,a.previous_12m_items,
 a.recent_12m_observed,a.previous_12m_observed,
 CASE WHEN recent_12m_observed=12 AND previous_12m_observed=12 THEN 100.0*(recent_12m_items-previous_12m_items)/NULLIF(previous_12m_items,0) END AS recent_annual_items_growth_pct,
 c.observed_month_count>=p.minimum_history_months AND c.full_window_coverage_pct>=p.minimum_coverage_pct
 AND c.internal_missing_month_count<=p.maximum_internal_gaps AND a.prescription_items>=p.minimum_total_items AS forecast_eligible,
 m.regional_items_mix_pct
 FROM phase2.vw_series_coverage c LEFT JOIN a USING(region_code,presentation_key)
 LEFT JOIN phase2.vw_region_presentation_mix m USING(region_code,presentation_key) CROSS JOIN phase2.parameters p
)
SELECT *,CASE WHEN forecast_eligible THEN 'complete_sufficient_volume'
 WHEN observed_month_count=0 THEN 'no_observed_history'
 ELSE 'fails_history_coverage_gap_or_volume_threshold' END AS eligibility_reason,
 CASE WHEN forecast_eligible THEN RANK() OVER(PARTITION BY forecast_eligible ORDER BY prescription_items DESC) END AS eligible_activity_rank,
 CASE WHEN forecast_eligible AND recent_annual_items_growth_pct IS NOT NULL THEN
 RANK() OVER(PARTITION BY forecast_eligible ORDER BY recent_annual_items_growth_pct DESC NULLS LAST) END AS eligible_growth_rank,
 100.0*net_ingredient_cost_gbp/NULLIF(SUM(net_ingredient_cost_gbp) OVER(),0) AS national_cost_share_pct,
 SUM(POWER(regional_items_mix_pct/100.0,2)) OVER(PARTITION BY region_code) AS regional_presentation_items_hhi
FROM b;
CREATE OR REPLACE VIEW phase2.vw_threshold_sensitivity AS
SELECT t.minimum_history_months,t.minimum_total_items,t.minimum_coverage_pct,
 COUNT(*) FILTER(WHERE c.observed_month_count>=t.minimum_history_months
 AND c.prescription_items>=t.minimum_total_items AND c.full_window_coverage_pct>=t.minimum_coverage_pct
 AND c.internal_missing_month_count<=p.maximum_internal_gaps) AS eligible_series_count
FROM phase2.threshold_parameters t CROSS JOIN phase2.vw_region_presentation_summary c CROSS JOIN phase2.parameters p GROUP BY ALL;
