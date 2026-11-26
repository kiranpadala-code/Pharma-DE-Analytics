WITH samples AS (

    SELECT *
    FROM {{ ref('stg_pharma__samples') }}

),

products AS (

    SELECT *
    FROM {{ ref('stg_pharma__product') }}

)

SELECT
    samples.sample_id,
    samples.product_id,
    products.is_sampleable
FROM samples
INNER JOIN products
    ON samples.product_id = products.product_id
WHERE products.is_sampleable = FALSE
