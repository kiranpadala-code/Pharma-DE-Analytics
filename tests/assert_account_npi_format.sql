SELECT
    account_id,
    hco_npi
FROM {{ ref('stg_pharma__account_master') }}
WHERE NOT REGEXP_LIKE(hco_npi, '^[0-9]{10}$')
