WITH snapshots AS (
    SELECT
        account_id,
        snapshot_month
    FROM {{ ref('stg_pharma__account_master') }}
),

history AS (
    SELECT *
    FROM {{ ref('int_account__history') }}
)

SELECT
    snapshots.account_id,
    snapshots.snapshot_month,
    COUNT(history.account_sk) AS matched_versions
FROM snapshots
LEFT JOIN history
    ON
        snapshots.account_id = history.account_id
        AND snapshots.snapshot_month >= history.valid_from
        AND (
            snapshots.snapshot_month < history.valid_to
            OR history.valid_to IS NULL
        )
GROUP BY
    snapshots.account_id,
    snapshots.snapshot_month
HAVING COUNT(history.account_sk) != 1
