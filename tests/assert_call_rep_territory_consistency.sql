WITH calls AS (

    SELECT *
    FROM {{ ref('stg_pharma__calls_interactions') }}

),

roster AS (

    SELECT *
    FROM {{ ref('stg_pharma__roster') }}

)

SELECT
    calls.call_id,
    calls.rep_id,
    calls.territory_id,
    roster.territory_id AS expected_territory_id
FROM calls
INNER JOIN roster
    ON
        calls.rep_id = roster.rep_id
        AND DATE_TRUNC('MONTH', calls.call_date) = roster.snapshot_month
WHERE calls.territory_id != roster.territory_id
