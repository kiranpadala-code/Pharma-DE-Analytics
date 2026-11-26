SELECT
    call_id,
    COALESCE(COUNT_IF(is_primary_product), 0) AS primary_product_count
FROM {{ ref('int_calls__products') }}
GROUP BY call_id
HAVING primary_product_count != 1
