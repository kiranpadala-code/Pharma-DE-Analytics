WITH snapshots AS (
    SELECT
        account_id,
        snapshot_month
    FROM {{ ref('stg_pharma__account_master') }}
),

snapshot_calendar AS (
    SELECT DISTINCT snapshot_month
    FROM snapshots
),

history AS (
    SELECT *
    FROM {{ ref('int_account__history') }}
)

SELECT
    history.account_id,
    history.account_sk,
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
        history.account_id = snapshots.account_id
        AND snapshot_calendar.snapshot_month = snapshots.snapshot_month
WHERE snapshots.account_id IS NULL
