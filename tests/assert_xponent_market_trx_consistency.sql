SELECT
    rx_id,
    trx_count,
    market_trx
FROM {{ ref('stg_pharma__xponent') }}
WHERE market_trx < trx_count
