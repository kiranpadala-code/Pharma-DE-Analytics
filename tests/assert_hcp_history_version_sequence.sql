WITH history AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY hcp_id
            ORDER BY valid_from
        ) AS expected_version_number
    FROM {{ ref('int_hcp__history') }}
)

SELECT *
FROM history
WHERE version_number != expected_version_number
