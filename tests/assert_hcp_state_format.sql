SELECT
    hcp_id,
    state
FROM {{ ref('stg_pharma__hcp_master') }}
WHERE NOT REGEXP_LIKE(state, '^[A-Z]{2}$')
