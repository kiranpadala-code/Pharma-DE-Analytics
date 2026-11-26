SELECT
    call_id,
    call_date,
    next_call_planned_date
FROM {{ ref('stg_pharma__calls_interactions') }}
WHERE next_call_planned_date < call_date
