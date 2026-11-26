SELECT
    manager_id,
    snapshot_month,
    COUNT(DISTINCT manager_name) AS name_count
FROM {{ ref('stg_pharma__roster') }}
GROUP BY manager_id, snapshot_month
HAVING COUNT(DISTINCT manager_name) > 1
