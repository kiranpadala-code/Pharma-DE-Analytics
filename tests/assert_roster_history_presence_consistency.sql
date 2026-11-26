WITH snapshots AS (
    SELECT
        rep_id,
        snapshot_month
    FROM {{ ref('stg_pharma__roster') }}
),

snapshot_calendar AS (
    SELECT DISTINCT snapshot_month
    FROM snapshots
),

history AS (
    SELECT *
    FROM {{ ref('int_roster__history') }}
)

SELECT
    history.rep_id,
    history.rep_sk,
    snapshot_calendar.snapshot_month
FROM history
INNER JOIN snapshot_calendar
    ON
        history.valid_from <= snapshot_calendar.snapshot_month
        AND (
            history.valid_to > snapshot_calendar.snapshot_month
            OR history.valid_to IS NULL
        )
LEFT JOIN snapshots
    ON
        history.rep_id = snapshots.rep_id
        AND snapshot_calendar.snapshot_month = snapshots.snapshot_month
WHERE snapshots.rep_id IS NULL
