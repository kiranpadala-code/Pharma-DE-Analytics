WITH product AS (
    SELECT *
    FROM {{ ref('stg_pharma__product') }}
)

SELECT * EXCLUDE (_source_file, _loaded_at)
FROM product
