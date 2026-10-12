-- Stable BI contracts; missing calendar-spine observations stay NULL.
CREATE OR REPLACE VIEW phase2.vw_forecast_candidates AS
SELECT * FROM phase2.vw_region_presentation_summary WHERE forecast_eligible;
CREATE OR REPLACE VIEW phase2.vw_presentation_regional_costs AS
SELECT region_code,region_name,presentation_key,presentation_code,presentation_name,unit_of_measure,
 SUM(prescription_items)::BIGINT AS prescription_items,SUM(net_ingredient_cost_gbp) AS net_ingredient_cost_gbp,
 SUM(total_quantity) AS total_quantity,
 SUM(net_ingredient_cost_gbp)/NULLIF(SUM(prescription_items),0) AS ingredient_cost_per_item_gbp,
 SUM(net_ingredient_cost_gbp)/NULLIF(SUM(total_quantity),0) AS ingredient_cost_per_native_unit_gbp
FROM phase2.vw_fact_enriched GROUP BY ALL;
