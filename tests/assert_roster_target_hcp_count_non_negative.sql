SELECT
    rep_id,
    target_hcp_count
FROM {{ ref('stg_pharma__roster') }}
WHERE target_hcp_count < 0
