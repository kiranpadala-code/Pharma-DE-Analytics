SELECT
    call_id,
    call_duration_min
FROM {{ ref('stg_pharma__calls_interactions') }}
WHERE call_duration_min <= 0
