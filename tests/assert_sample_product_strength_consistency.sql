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
    samples.strength_sampled,
    products.strength AS expected_strength
FROM samples
INNER JOIN products
    ON samples.product_id = products.product_id
WHERE samples.strength_sampled != products.strength
