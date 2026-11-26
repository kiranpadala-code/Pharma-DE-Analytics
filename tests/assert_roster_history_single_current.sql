SELECT
    rep_id,
    COUNT_IF(is_current) AS current_count
FROM {{ ref('int_roster__history') }}
GROUP BY rep_id
HAVING COUNT_IF(is_current) > 1
