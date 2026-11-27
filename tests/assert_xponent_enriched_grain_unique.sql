SELECT
    npi,
    product_id,
    period_month,
    count(*)
FROM {{ ref('int_xponent__enriched') }}
GROUP BY npi, product_id, period_month
HAVING count(*) > 1
