-- Input relations and parameters are registered by the Python runner, never fabricated.
CREATE SCHEMA IF NOT EXISTS phase2;
CREATE OR REPLACE TABLE phase2.parameters AS SELECT * FROM input_parameters;
CREATE OR REPLACE TABLE phase2.threshold_parameters AS SELECT * FROM input_sensitivity;
CREATE OR REPLACE TABLE phase2.staging_prescribing AS
SELECT CAST(DATE_TRUNC('month', month) AS DATE) AS month,
       product_code AS presentation_code, product_name AS presentation_name,
       region_code, region_name, unit_of_measure,
       product_code || '|' || unit_of_measure AS presentation_key,
       chemical_code, chemical_name, CAST(items AS BIGINT) AS prescription_items,
       CAST(nic_gbp AS DECIMAL(20,2)) AS net_ingredient_cost_gbp,
       total_quantity, source_row_count, data_origin
FROM input_monthly;

CREATE OR REPLACE TABLE phase2.dim_month (month DATE PRIMARY KEY, calendar_year INTEGER, calendar_month INTEGER);
INSERT INTO phase2.dim_month
SELECT CAST(d AS DATE), YEAR(d), MONTH(d)
FROM phase2.parameters, GENERATE_SERIES(start_month, end_month, INTERVAL '1 month') t(d);
CREATE OR REPLACE TABLE phase2.dim_region (region_code VARCHAR PRIMARY KEY, region_name VARCHAR);
INSERT INTO phase2.dim_region SELECT DISTINCT region_code, region_name FROM phase2.staging_prescribing;
CREATE OR REPLACE TABLE phase2.dim_presentation (
    presentation_key VARCHAR PRIMARY KEY, presentation_code VARCHAR, presentation_name VARCHAR,
    unit_of_measure VARCHAR, chemical_code VARCHAR, chemical_name VARCHAR
);
INSERT INTO phase2.dim_presentation
SELECT DISTINCT presentation_key, presentation_code, presentation_name, unit_of_measure, chemical_code, chemical_name
FROM phase2.staging_prescribing;
CREATE OR REPLACE TABLE phase2.fact_monthly_prescribing (
    month DATE, region_code VARCHAR, presentation_key VARCHAR,
    prescription_items BIGINT NOT NULL, net_ingredient_cost_gbp DECIMAL(20,2) NOT NULL,
    total_quantity DOUBLE NOT NULL, source_row_count BIGINT NOT NULL,
    PRIMARY KEY (month, region_code, presentation_key)
);
INSERT INTO phase2.fact_monthly_prescribing
SELECT month, region_code, presentation_key, prescription_items, net_ingredient_cost_gbp, total_quantity, source_row_count
FROM phase2.staging_prescribing;
-- Logical foreign keys are checked explicitly in 02 to allow transactional idempotent table refreshes.
CREATE OR REPLACE VIEW phase2.vw_fact_enriched AS
SELECT f.*, p.presentation_code, p.presentation_name, p.unit_of_measure, r.region_name
FROM phase2.fact_monthly_prescribing f
INNER JOIN phase2.dim_presentation p USING (presentation_key)
INNER JOIN phase2.dim_region r USING (region_code);
