WITH snapshots AS (
    SELECT *
    FROM {{ ref('stg_pharma__account_master') }}
),

history AS (
    SELECT *
    FROM {{ ref('int_account__history') }}
)

SELECT
    snapshots.account_id,
    snapshots.snapshot_month,
    history.account_sk
FROM snapshots
INNER JOIN history
    ON
        snapshots.account_id = history.account_id
        AND snapshots.snapshot_month >= history.valid_from
        AND (
            snapshots.snapshot_month < history.valid_to
            OR history.valid_to IS NULL
        )
WHERE
    snapshots.account_name IS DISTINCT FROM history.account_name
    OR snapshots.account_type IS DISTINCT FROM history.account_type
    OR snapshots.account_segment IS DISTINCT FROM history.account_segment
    OR snapshots.hco_npi IS DISTINCT FROM history.hco_npi
    OR snapshots.parent_account_id IS DISTINCT FROM history.parent_account_id
    OR snapshots.address_line1 IS DISTINCT FROM history.address_line1
    OR snapshots.city IS DISTINCT FROM history.city
    OR snapshots.state IS DISTINCT FROM history.state
    OR snapshots.zip IS DISTINCT FROM history.zip
    OR snapshots.region IS DISTINCT FROM history.region
    OR snapshots.bed_count IS DISTINCT FROM history.bed_count
    OR snapshots.is_teaching_hospital IS DISTINCT FROM history.is_teaching_hospital
    OR snapshots.is_magnet_hospital IS DISTINCT FROM history.is_magnet_hospital
    OR snapshots.formulary_access IS DISTINCT FROM history.formulary_access
    OR snapshots.is_active IS DISTINCT FROM history.is_active
