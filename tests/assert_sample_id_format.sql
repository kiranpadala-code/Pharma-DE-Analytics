SELECT sample_id
FROM {{ ref('stg_pharma__samples') }}
WHERE NOT REGEXP_LIKE(sample_id, '^SAMP[0-9]{7}$')
