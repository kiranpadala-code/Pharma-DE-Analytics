SELECT
    rep_id,
    rep_first_name,
    rep_last_name,
    rep_name
FROM {{ ref('stg_pharma__roster') }}
WHERE rep_name != rep_first_name || ' ' || rep_last_name
