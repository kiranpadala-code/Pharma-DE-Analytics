WITH snapshots AS (
    SELECT *
    FROM {{ ref('stg_pharma__roster') }}
),

history AS (
    SELECT *
    FROM {{ ref('int_roster__history') }}
)

SELECT
    snapshots.rep_id,
    snapshots.snapshot_month,
    history.rep_sk
FROM snapshots
INNER JOIN history
    ON
        snapshots.rep_id = history.rep_id
        AND snapshots.snapshot_month >= history.valid_from
        AND (
            snapshots.snapshot_month < history.valid_to
            OR history.valid_to IS NULL
        )
WHERE
    snapshots.rep_first_name IS DISTINCT FROM history.rep_first_name
    OR snapshots.rep_last_name IS DISTINCT FROM history.rep_last_name
    OR snapshots.rep_name IS DISTINCT FROM history.rep_name
    OR snapshots.rep_email IS DISTINCT FROM history.rep_email
    OR snapshots.role_title IS DISTINCT FROM history.role_title
    OR snapshots.channel IS DISTINCT FROM history.channel
    OR snapshots.territory_id IS DISTINCT FROM history.territory_id
    OR snapshots.territory_name IS DISTINCT FROM history.territory_name
    OR snapshots.region IS DISTINCT FROM history.region
    OR snapshots.zone IS DISTINCT FROM history.zone
    OR snapshots.manager_id IS DISTINCT FROM history.manager_id
    OR snapshots.manager_name IS DISTINCT FROM history.manager_name
    OR snapshots.product_focus IS DISTINCT FROM history.product_focus
    OR snapshots.hire_date IS DISTINCT FROM history.hire_date
    OR snapshots.employee_status IS DISTINCT FROM history.employee_status
    OR snapshots.target_hcp_count IS DISTINCT FROM history.target_hcp_count
