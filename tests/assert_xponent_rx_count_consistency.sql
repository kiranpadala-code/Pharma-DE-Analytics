SELECT
    rx_id,
    trx_count,
    nrx_count,
    refill_count
FROM {{ ref('stg_pharma__xponent') }}
WHERE trx_count != nrx_count + refill_count
