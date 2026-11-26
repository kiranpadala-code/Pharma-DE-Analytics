WITH calls AS (

    SELECT *
    FROM {{ ref('stg_pharma__calls_interactions') }}

),

hcp AS (

    SELECT *
    FROM {{ ref('stg_pharma__hcp_master') }}

)

SELECT
    calls.call_id,
    calls.npi,
    calls.call_date
FROM calls
LEFT JOIN hcp
    ON
        calls.npi = hcp.npi
        AND DATE_TRUNC('MONTH', calls.call_date) = hcp.snapshot_month
WHERE hcp.npi IS NULL
