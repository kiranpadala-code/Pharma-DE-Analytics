SELECT
    npi,
    snapshot_month,
    COUNT(*) AS record_count
FROM {{ ref('stg_pharma__hcp_master') }}
GROUP BY
    npi,
    snapshot_month
HAVING COUNT(*) > 1
