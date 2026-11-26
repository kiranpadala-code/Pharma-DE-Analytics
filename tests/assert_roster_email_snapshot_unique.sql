SELECT
    rep_email,
    snapshot_month,
    COUNT(*) AS record_count
FROM {{ ref('stg_pharma__roster') }}
GROUP BY rep_email, snapshot_month
HAVING COUNT(*) > 1
