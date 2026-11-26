SELECT
    sample_id,
    rep_id
FROM {{ ref('stg_pharma__samples') }}
WHERE NOT REGEXP_LIKE(rep_id, '^REP[0-9]{4}$')
