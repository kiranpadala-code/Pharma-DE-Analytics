-- Grain: One record per territory.
-- Purpose: Provide details of territory and its hierarchy.
WITH source AS (
    SELECT * FROM {{ source('pharma_raw', 'territory') }}
),

standardized AS (
    SELECT
        UPPER(TRIM(territory_id)) AS territory_id,
        TRIM(territory_name) AS territory_name,
        TRIM(region) AS region,
        TRIM(zone) AS zone,
        UPPER(TRIM(states_covered)) AS states_covered,
        _source_file,
        _loaded_at
    FROM source
)

SELECT * FROM standardized
