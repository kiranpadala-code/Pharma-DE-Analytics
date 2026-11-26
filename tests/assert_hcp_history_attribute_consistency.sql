WITH snapshots AS (
    SELECT *
    FROM {{ ref('stg_pharma__hcp_master') }}
),

history AS (
    SELECT *
    FROM {{ ref('int_hcp__history') }}
)

SELECT
    snapshots.hcp_id,
    snapshots.snapshot_month,
    history.hcp_sk
FROM snapshots
INNER JOIN history
    ON snapshots.hcp_id = history.hcp_id
    AND snapshots.snapshot_month >= history.valid_from
    AND (
        snapshots.snapshot_month < history.valid_to
        OR history.valid_to IS NULL
    )
WHERE
    snapshots.npi IS DISTINCT FROM history.npi
    OR snapshots.first_name IS DISTINCT FROM history.first_name
    OR snapshots.last_name IS DISTINCT FROM history.last_name
    OR snapshots.full_name IS DISTINCT FROM history.full_name
    OR snapshots.degree IS DISTINCT FROM history.degree
    OR snapshots.specialty IS DISTINCT FROM history.specialty
    OR snapshots.sub_specialty IS DISTINCT FROM history.sub_specialty
    OR snapshots.gender IS DISTINCT FROM history.gender
    OR snapshots.address_line1 IS DISTINCT FROM history.address_line1
    OR snapshots.city IS DISTINCT FROM history.city
    OR snapshots.state IS DISTINCT FROM history.state
    OR snapshots.zip IS DISTINCT FROM history.zip
    OR snapshots.account_id IS DISTINCT FROM history.account_id
    OR snapshots.territory_id IS DISTINCT FROM history.territory_id
    OR snapshots.tier IS DISTINCT FROM history.tier
    OR snapshots.decile IS DISTINCT FROM history.decile
    OR snapshots.target_segment IS DISTINCT FROM history.target_segment
    OR snapshots.is_kol IS DISTINCT FROM history.is_kol
    OR snapshots.is_target IS DISTINCT FROM history.is_target
    OR snapshots.is_active IS DISTINCT FROM history.is_active
    OR snapshots.years_in_practice IS DISTINCT FROM history.years_in_practice
    OR snapshots.data_source IS DISTINCT FROM history.data_source
