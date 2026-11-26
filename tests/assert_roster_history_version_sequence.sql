WITH history AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY rep_id
            ORDER BY valid_from
        ) AS expected_version_number
    FROM {{ ref('int_roster__history') }}
)

SELECT *
FROM history
WHERE version_number != expected_version_number
