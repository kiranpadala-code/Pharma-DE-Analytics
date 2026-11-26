WITH history AS (
    SELECT
        *,
        LEAD(valid_from) OVER (
            PARTITION BY rep_id
            ORDER BY valid_from
        ) AS next_valid_from
    FROM {{ ref('int_roster__history') }}
)

SELECT *
FROM history
WHERE
    next_valid_from IS NOT NULL
    AND (
        valid_to IS NULL
        OR valid_to > next_valid_from
    )
