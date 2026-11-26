SELECT
    rx_id,
    npi
FROM {{ ref('stg_pharma__xponent') }}
WHERE REGEXP_LIKE(npi, '^[0-9]{10}$') = FALSE
