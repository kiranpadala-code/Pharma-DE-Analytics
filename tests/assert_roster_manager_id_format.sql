SELECT
    rep_id,
    manager_id
FROM {{ ref('stg_pharma__roster') }}
WHERE REGEXP_LIKE(manager_id, '^MGR[0-9]{3}$') = FALSE
