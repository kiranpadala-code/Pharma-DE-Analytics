SELECT
    npi,
    product_id,
    period_month,
    COUNT(*) AS record_count
FROM {{ ref('stg_pharma__xponent') }}
GROUP BY npi, product_id, period_month
HAVING COUNT(*) > 1
