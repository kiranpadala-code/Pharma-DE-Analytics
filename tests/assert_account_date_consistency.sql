SELECT
    account_id,
    record_created_date,
    record_updated_date
FROM {{ ref('stg_pharma__account_master') }}
WHERE record_created_date > record_updated_date
