WITH expected AS (
    SELECT product_id
    FROM {{ ref('stg_pharma__product') }}
),

actual AS (
    SELECT product_id
    FROM {{ ref('dim_product') }}
)

SELECT
    expected.product_id AS expected_product_id,
    actual.product_id AS actual_product_id
FROM expected
FULL OUTER JOIN actual
    ON expected.product_id = actual.product_id
WHERE
    expected.product_id IS NULL
    OR actual.product_id IS NULL
