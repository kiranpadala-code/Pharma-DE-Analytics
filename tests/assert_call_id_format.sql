SELECT call_id
FROM {{ ref('stg_pharma__calls_interactions') }}
WHERE NOT REGEXP_LIKE(call_id, '^CALL[0-9]{7}$')
