SELECT
    call_id,
    call_rank_in_month
FROM {{ ref('stg_pharma__calls_interactions') }}
WHERE call_rank_in_month < 1
