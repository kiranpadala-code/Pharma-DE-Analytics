SELECT
    hcp_id,
    record_created_date,
    snapshot_month
FROM {{ ref('stg_pharma__hcp_master') }}
WHERE record_created_date > snapshot_month
