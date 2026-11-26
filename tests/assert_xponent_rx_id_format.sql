SELECT rx_id
FROM {{ ref('stg_pharma__xponent') }}
WHERE REGEXP_LIKE(rx_id, '^RX[0-9]{7}$') = FALSE
