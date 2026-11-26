SELECT
    sample_id,
    sample_request_type,
    call_id
FROM {{ ref('stg_pharma__samples') }}
WHERE
    (sample_request_type = 'HCP Request' AND call_id IS NOT NULL)
    OR (
        sample_request_type IN (
            'Routine Drop',
            'New Patient Start',
            'Follow-up'
        )
        AND call_id IS NULL
    )
