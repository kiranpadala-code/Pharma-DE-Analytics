SELECT rep_id
FROM {{ ref('stg_pharma__roster') }}
WHERE REGEXP_LIKE(rep_id, '^REP[0-9]{4}$') = FALSE
