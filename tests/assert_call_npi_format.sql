SELECT
    call_id,
    npi
FROM {{ ref('stg_pharma__calls_interactions') }}
WHERE NOT REGEXP_LIKE(npi, '^[0-9]{10}$')
