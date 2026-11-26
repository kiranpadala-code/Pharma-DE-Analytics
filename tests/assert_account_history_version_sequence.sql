WITH history AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY account_id
            ORDER BY valid_from
        ) AS expected_version_number
    FROM {{ ref('int_account__history') }}
)

SELECT *
FROM history
WHERE version_number != expected_version_number
