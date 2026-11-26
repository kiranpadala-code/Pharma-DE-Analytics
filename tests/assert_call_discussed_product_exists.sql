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
    discussed_products.call_id,
    discussed_products.brand_name
FROM discussed_products
LEFT JOIN products
    ON discussed_products.brand_name = products.brand_name
WHERE products.brand_name IS NULL
