WITH snapshots AS (
    SELECT
        hcp_id,
        snapshot_month
    FROM {{ ref('stg_pharma__hcp_master') }}
),

history AS (
    SELECT *
    FROM {{ ref('int_hcp__history') }}
)

SELECT
    snapshots.hcp_id,
    snapshots.snapshot_month,
    COUNT(history.hcp_sk) AS matched_versions
FROM snapshots
LEFT JOIN history
    ON snapshots.hcp_id = history.hcp_id
    AND snapshots.snapshot_month >= history.valid_from
    AND (
        snapshots.snapshot_month < history.valid_to
        OR history.valid_to IS NULL
    )
GROUP BY
    snapshots.hcp_id,
    snapshots.snapshot_month
HAVING COUNT(history.hcp_sk) != 1
