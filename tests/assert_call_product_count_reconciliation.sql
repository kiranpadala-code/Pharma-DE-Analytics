WITH expected AS (

    SELECT
        call_id,
        ARRAY_SIZE(SPLIT(products_discussed, ';')) AS exp_count
    FROM {{ ref('stg_pharma__calls_interactions') }}

),

actual AS (

    SELECT
        call_id,
        COUNT(*) AS actual_count
    FROM {{ ref('int_calls__products') }}
    GROUP BY call_id

)

SELECT
    expected.call_id,
    expected.exp_count,
    COALESCE(actual.actual_count, 0) AS actual_count,
    expected.exp_count - COALESCE(actual.actual_count, 0) AS count_difference
FROM expected
LEFT JOIN actual
    ON expected.call_id = actual.call_id
WHERE count_difference != 0
