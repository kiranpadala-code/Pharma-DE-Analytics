WITH snapshots AS (
    SELECT
        rep_id,
        snapshot_month
    FROM {{ ref('stg_pharma__roster') }}
),

history AS (
    SELECT *
    FROM {{ ref('int_roster__history') }}
)

SELECT
    snapshots.rep_id,
    snapshots.snapshot_month,
    COUNT(history.rep_sk) AS matched_versions
FROM snapshots
LEFT JOIN history
    ON
        snapshots.rep_id = history.rep_id
        AND snapshots.snapshot_month >= history.valid_from
        AND (
            snapshots.snapshot_month < history.valid_to
            OR history.valid_to IS NULL
        )
GROUP BY
    snapshots.rep_id,
    snapshots.snapshot_month
HAVING COUNT(history.rep_sk) != 1
