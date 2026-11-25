SELECT
    hcp_id,
    npi
FROM {{ ref('stg_pharma__hcp_master') }}
WHERE NOT REGEXP_LIKE(npi, '^[0-9]{10}$')
