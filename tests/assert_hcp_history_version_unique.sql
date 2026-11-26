SELECT
    hcp_id,
    version_number,
    COUNT(*) AS record_count
FROM {{ ref('int_hcp__history') }}
GROUP BY hcp_id, version_number
HAVING COUNT(*) > 1
