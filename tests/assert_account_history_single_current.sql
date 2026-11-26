SELECT
    account_id,
    COUNT_IF(is_current) AS current_count
FROM {{ ref('int_account__history') }}
GROUP BY account_id
HAVING COUNT_IF(is_current) > 1
