SELECT
    sample_id,
    qty_dropped
FROM {{ ref('stg_pharma__samples') }}
WHERE qty_dropped <= 0
