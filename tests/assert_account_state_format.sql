SELECT
    account_id,
    state
FROM {{ ref('stg_pharma__account_master') }}
WHERE NOT REGEXP_LIKE(state, '^[A-Z]{2}$')
