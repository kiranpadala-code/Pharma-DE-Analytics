WITH xponent AS (

    SELECT *
    FROM {{ ref('stg_pharma__xponent') }}

),

hcp AS (

    SELECT *
    FROM {{ ref('stg_pharma__hcp_master') }}

)

SELECT
    xponent.rx_id,
    xponent.npi,
    xponent.period_month,
    xponent.state,
    hcp.state AS expected_state,
    xponent.specialty,
    hcp.specialty AS expected_specialty
FROM xponent
INNER JOIN hcp
    ON
        xponent.npi = hcp.npi
        AND xponent.period_month = hcp.snapshot_month
WHERE
    xponent.state != hcp.state
    OR xponent.specialty != hcp.specialty
