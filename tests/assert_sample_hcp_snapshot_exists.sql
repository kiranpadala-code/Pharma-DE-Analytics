WITH samples AS (

    SELECT *
    FROM {{ ref('stg_pharma__samples') }}

),

hcp AS (

    SELECT *
    FROM {{ ref('stg_pharma__hcp_master') }}

)

SELECT
    samples.sample_id,
    samples.npi,
    samples.sample_date
FROM samples
LEFT JOIN hcp
    ON
        samples.npi = hcp.npi
        AND DATE_TRUNC('MONTH', samples.sample_date) = hcp.snapshot_month
WHERE hcp.npi IS NULL
