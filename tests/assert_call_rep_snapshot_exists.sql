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
    calls.call_date
FROM calls
LEFT JOIN roster
    ON
        calls.rep_id = roster.rep_id
        AND DATE_TRUNC('MONTH', calls.call_date) = roster.snapshot_month
WHERE roster.rep_id IS NULL
