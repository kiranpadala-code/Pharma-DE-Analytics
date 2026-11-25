SELECT
    product_id,
    product_code,
    price
FROM {{ ref('stg_pharma__product') }}
WHERE price <= 0 OR price IS NULL
