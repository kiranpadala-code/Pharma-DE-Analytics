SELECT
    hcp_id,
    COUNT_IF(is_current) AS current_count
FROM {{ ref('int_hcp__history') }}
GROUP BY hcp_id
HAVING COUNT_IF(is_current) > 1
