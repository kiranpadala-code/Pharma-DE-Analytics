SELECT
    sample_id,
    sample_date,
    expiry_date
FROM {{ ref('stg_pharma__samples') }}
WHERE expiry_date < sample_date
