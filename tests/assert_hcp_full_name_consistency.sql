SELECT
    hcp_id,
    first_name,
    last_name,
    full_name
FROM {{ ref('stg_pharma__hcp_master') }}
WHERE full_name != first_name || ' ' || last_name
