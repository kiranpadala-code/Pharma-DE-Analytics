SELECT
    rep_id,
    version_number,
    COUNT(*) AS record_count
FROM {{ ref('int_roster__history') }}
GROUP BY rep_id, version_number
HAVING COUNT(*) > 1
