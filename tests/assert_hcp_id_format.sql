SELECT hcp_id
FROM {{ ref('stg_pharma__hcp_master') }}
WHERE NOT REGEXP_LIKE(hcp_id, '^HCP[0-9]{5}$')
