SELECT
    rx_id,
    market_share_pct
FROM {{ ref('stg_pharma__xponent') }}
WHERE market_share_pct NOT BETWEEN 0 AND 100
