WITH hcp AS (
    SELECT
        hcp_id,
        account_id,
        snapshot_month
    FROM {{ ref('stg_pharma__hcp_master') }}
),

accounts AS (
    SELECT
        account_id,
        snapshot_month
    FROM {{ ref('stg_pharma__account_master') }}
),

account_snapshots AS (
    SELECT DISTINCT snapshot_month
    FROM accounts
),

applicable_snapshots AS (
    SELECT
        hcp.hcp_id,
        hcp.account_id,
        hcp.snapshot_month,
        MAX(account_snapshots.snapshot_month) AS account_snapshot_month
    FROM hcp
    LEFT JOIN account_snapshots
        ON hcp.snapshot_month >= account_snapshots.snapshot_month
    GROUP BY
        hcp.hcp_id,
        hcp.account_id,
        hcp.snapshot_month
)

SELECT
    applicable_snapshots.hcp_id,
    applicable_snapshots.account_id,
    applicable_snapshots.snapshot_month,
    applicable_snapshots.account_snapshot_month
FROM applicable_snapshots
LEFT JOIN accounts
    ON
        applicable_snapshots.account_id = accounts.account_id
        AND applicable_snapshots.account_snapshot_month
        = accounts.snapshot_month
WHERE accounts.account_id IS NULL
