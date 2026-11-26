WITH calls AS (

    SELECT
        src.call_id,
        src.product_id AS primary_product_id,
        TRIM(discussed.value::VARCHAR) AS brand_name,
        src._source_file,
        src._loaded_at
    FROM {{ ref('stg_pharma__calls_interactions') }} AS src,
        LATERAL FLATTEN(input => SPLIT(src.products_discussed, ';'))
            AS discussed

),

products AS (

    SELECT
        product_id,
        brand_name
    FROM {{ ref('stg_pharma__product') }}

),

normalized AS (

    SELECT
        calls.call_id,
        products.product_id,
        calls.brand_name,
        calls.primary_product_id = products.product_id AS is_primary_product,
        calls._source_file,
        calls._loaded_at
    FROM calls
    INNER JOIN products ON calls.brand_name = products.brand_name

)

SELECT *
FROM normalized
