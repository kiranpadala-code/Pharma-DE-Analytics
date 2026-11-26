SELECT
    call_id,
    rep_id
FROM {{ ref('stg_pharma__calls_interactions') }}
WHERE NOT REGEXP_LIKE(rep_id, '^REP[0-9]{4}$')
