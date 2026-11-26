WITH calls AS (

    SELECT *
    FROM {{ ref('stg_pharma__calls_interactions') }}

),

products AS (

    SELECT *
    FROM {{ ref('stg_pharma__product') }}

),

discussed_products AS (

    SELECT
        calls.call_id,
        TRIM(discussed.value::VARCHAR) AS brand_name
    FROM calls,
        LATERAL FLATTEN(
            INPUT => SPLIT(calls.products_discussed, ';')
        ) AS discussed

)

SELECT
    calls.call_id,
    calls.product_id,
    products.brand_name AS expected_brand,
    calls.products_discussed
FROM calls
INNER JOIN products
    ON calls.product_id = products.product_id
LEFT JOIN discussed_products
    ON
        calls.call_id = discussed_products.call_id
        AND products.brand_name = discussed_products.brand_name
WHERE discussed_products.call_id IS NULL
