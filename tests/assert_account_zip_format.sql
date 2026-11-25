SELECT
    account_id,
    zip
FROM {{ ref('stg_pharma__account_master') }}
WHERE NOT REGEXP_LIKE(zip, '^[0-9]{5}$')
