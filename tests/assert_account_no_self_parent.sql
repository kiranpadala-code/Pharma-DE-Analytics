SELECT
    account_id,
    parent_account_id,
    snapshot_month
FROM {{ ref('stg_pharma__account_master') }}
WHERE account_id = parent_account_id
