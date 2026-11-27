WITH expected AS (
    SELECT territory_id
    FROM {{ ref('stg_pharma__territory') }}
),

actual AS (
    SELECT territory_id
    FROM {{ ref('dim_territory') }}
)

SELECT
    expected.territory_id AS expected_territory_id,
    actual.territory_id AS actual_territory_id
FROM expected
FULL OUTER JOIN actual
    ON expected.territory_id = actual.territory_id
WHERE
    expected.territory_id IS NULL
    OR actual.territory_id IS NULL
