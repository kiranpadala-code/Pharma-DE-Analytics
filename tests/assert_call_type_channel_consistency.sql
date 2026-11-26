SELECT
    call_id,
    call_type,
    call_channel
FROM {{ ref('stg_pharma__calls_interactions') }}
WHERE NOT (
    (call_type = 'F2F' AND call_channel = 'In-Office')
    OR (call_type = 'MSL Visit' AND call_channel = 'In-Office')
    OR (call_type = 'Phone' AND call_channel = 'Phone')
    OR (call_type = 'RTE' AND call_channel = 'Email')
    OR (call_type = 'Virtual' AND call_channel IN ('Teams', 'Zoom'))
)
