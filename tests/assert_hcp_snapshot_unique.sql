SELECT
    hcp_id,
    snapshot_month,
    COUNT(*) AS record_count
FROM {{ ref('stg_pharma__hcp_master') }}
GROUP BY
    hcp_id,
    snapshot_month
HAVING COUNT(*) > 1
