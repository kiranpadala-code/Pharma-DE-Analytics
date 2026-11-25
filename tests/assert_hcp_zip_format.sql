SELECT
    hcp_id,
    zip
FROM {{ ref('stg_pharma__hcp_master') }}
WHERE NOT REGEXP_LIKE(zip, '^[0-9]{5}$')
