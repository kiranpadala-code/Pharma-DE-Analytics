SELECT
    rx_id,
    state
FROM {{ ref('stg_pharma__xponent') }}
WHERE REGEXP_LIKE(state, '^[A-Z]{2}$') = FALSE
