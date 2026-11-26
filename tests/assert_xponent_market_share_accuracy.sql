SELECT
    rx_id,
    trx_count,
    market_trx,
    market_share_pct,
    ROUND(
        trx_count * 100.0 / NULLIF(market_trx, 0),
        2
    ) AS expected_market_share_pct
FROM {{ ref('stg_pharma__xponent') }}
WHERE
    market_trx = 0
    OR market_share_pct != ROUND(
        trx_count * 100.0 / NULLIF(market_trx, 0),
        2
    )
