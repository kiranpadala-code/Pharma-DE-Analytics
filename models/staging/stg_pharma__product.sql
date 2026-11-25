-- Grain: One record per pharmaceutical product.
-- Purpose: Standardize product master data and preserve ingestion metadata.

WITH source AS (

    SELECT *
    FROM {{ source('pharma_raw', 'product') }}

),

standardized AS (

    SELECT
        UPPER(TRIM(product_id)) AS product_id,
        UPPER(TRIM(product_code)) AS product_code,
        TRIM(brand_name) AS brand_name,
        LOWER(TRIM(generic_name)) AS generic_name,
        TRIM(product_family) AS product_family,
        TRIM(therapeutic_area) AS therapeutic_area,
        TRIM(indication) AS indication,
        TRIM(form) AS dosage_form,
        TRIM(route) AS route_of_administration,
        TRIM(strength) AS strength,
        TRIM(dosing_frequency) AS dosing_frequency,
        TRIM(manufacturer) AS manufacturer,
        approval_date,
        is_active,
        is_sampleable,
        TRIM(formulary_tier) AS formulary_tier,
        price,
        _source_file,
        _loaded_at
    FROM source

)

SELECT * FROM standardized
