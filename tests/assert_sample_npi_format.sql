SELECT
    sample_id,
    npi
FROM {{ ref('stg_pharma__samples') }}
WHERE NOT REGEXP_LIKE(npi, '^[0-9]{10}$')
