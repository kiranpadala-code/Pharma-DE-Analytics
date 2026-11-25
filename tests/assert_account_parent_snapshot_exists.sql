SELECT
    child.account_id,
    child.parent_account_id,
    child.snapshot_month
FROM {{ ref('stg_pharma__account_master') }} AS child
LEFT JOIN {{ ref('stg_pharma__account_master') }} AS parent
    ON
        child.parent_account_id = parent.account_id
        AND child.snapshot_month = parent.snapshot_month
WHERE
    child.parent_account_id IS NOT NULL
    AND parent.account_id IS NULL
