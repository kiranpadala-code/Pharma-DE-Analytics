SELECT
    rx_id,
    trx_count,
    nrx_count,
    refill_count,
    market_trx
FROM {{ ref('stg_pharma__xponent') }}
WHERE
    trx_count < 0
    OR nrx_count < 0
    OR refill_count < 0
    OR market_trx < 0
