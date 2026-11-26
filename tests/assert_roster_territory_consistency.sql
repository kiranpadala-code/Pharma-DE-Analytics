WITH roster AS (

    SELECT *
    FROM {{ ref('stg_pharma__roster') }}

),

territory AS (

    SELECT *
    FROM {{ ref('stg_pharma__territory') }}

)

SELECT
    roster.rep_id,
    roster.snapshot_month,
    roster.territory_id,
    roster.territory_name,
    roster.region,
    roster.zone
FROM roster
INNER JOIN territory
    ON roster.territory_id = territory.territory_id
WHERE
    roster.territory_name != territory.territory_name
    OR roster.region != territory.region
    OR roster.zone != territory.zone
