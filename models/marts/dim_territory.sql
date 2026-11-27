WITH territory AS (
    SELECT *
    FROM {{ ref('stg_pharma__territory') }}
)

SELECT
    territory_id,
    territory_name,
    region,
    zone
FROM territory
