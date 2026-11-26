SELECT
    call_id,
    product_id,
    count(*) AS total_count
FROM
    {{ ref('int_calls__products') }}
GROUP BY call_id, product_id
HAVING count(*) > 1
