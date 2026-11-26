SELECT
    account_id,
    version_number,
    COUNT(*) AS record_count
FROM {{ ref('int_account__history') }}
GROUP BY account_id, version_number
HAVING COUNT(*) > 1
