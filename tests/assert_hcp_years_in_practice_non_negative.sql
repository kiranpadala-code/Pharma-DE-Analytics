SELECT
    hcp_id,
    years_in_practice
FROM {{ ref('stg_pharma__hcp_master') }}
WHERE years_in_practice < 0
