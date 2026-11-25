SELECT
    territory_id,
    states_covered
FROM {{ ref('stg_pharma__territory') }}
WHERE
    regexp_like(states_covered, '^[A-Z]{2}(;[A-Z]{2})*$') = FALSE
    OR states_covered IS NULL
