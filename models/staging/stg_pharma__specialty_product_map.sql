-- Grain: One record per HCP specialty.
-- Purpose: Map each HCP specialty to its primary pharmaceutical product.

WITH source AS (
    SELECT * FROM {{ source('pharma_raw', 'specialty_product_map') }}
),

standardized AS (
    SELECT
        TRIM(specialty) AS specialty,
        UPPER(TRIM(primary_product_id)) AS primary_product_id,
        _source_file,
        _loaded_at
    FROM source
)

SELECT * FROM standardized
