SELECT
    account_id,
    bed_count
FROM {{ ref('stg_pharma__account_master') }}
WHERE bed_count < 0
