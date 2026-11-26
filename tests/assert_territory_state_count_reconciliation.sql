WITH expected AS (

    SELECT
        territory_id,
        ARRAY_SIZE(SPLIT(states_covered, ';')) AS exp_count
    FROM {{ ref('stg_pharma__territory') }}

),

actual AS (

    SELECT
        territory_id,
        COUNT(*) AS actual_count
    FROM {{ ref('int_territory__states') }}
    GROUP BY territory_id

)

SELECT
    expected.territory_id,
    expected.exp_count,
    COALESCE(actual.actual_count, 0) AS actual_count,
    expected.exp_count - COALESCE(actual.actual_count, 0) AS count_difference
FROM expected
LEFT JOIN actual
    ON expected.territory_id = actual.territory_id
WHERE count_difference != 0
