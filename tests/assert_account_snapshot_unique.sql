SELECT
    account_id,
    snapshot_month,
    COUNT(*) AS record_count
FROM {{ ref('stg_pharma__account_master') }}
GROUP BY
    account_id,
    snapshot_month
HAVING COUNT(*) > 1
