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
    xponent.period_month
FROM xponent
LEFT JOIN hcp
    ON
        xponent.npi = hcp.npi
        AND xponent.period_month = hcp.snapshot_month
WHERE hcp.npi IS NULL
