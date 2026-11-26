WITH snapshots AS (
    SELECT
        hcp_id,
        snapshot_month
    FROM {{ ref('stg_pharma__hcp_master') }}
),

snapshot_calendar AS (
    SELECT DISTINCT snapshot_month
    FROM snapshots
),

history AS (
    SELECT *
    FROM {{ ref('int_hcp__history') }}
)

SELECT
    history.hcp_id,
    history.hcp_sk,
    snapshot_calendar.snapshot_month
FROM history
INNER JOIN snapshot_calendar
    ON snapshot_calendar.snapshot_month >= history.valid_from
    AND (
        snapshot_calendar.snapshot_month < history.valid_to
        OR history.valid_to IS NULL
    )
LEFT JOIN snapshots
    ON history.hcp_id = snapshots.hcp_id
    AND snapshot_calendar.snapshot_month = snapshots.snapshot_month
WHERE snapshots.hcp_id IS NULL
