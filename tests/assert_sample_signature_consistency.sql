SELECT
    sample_id,
    was_signature_captured,
    signature_method
FROM {{ ref('stg_pharma__samples') }}
WHERE NOT (
    (
        was_signature_captured = TRUE
        AND signature_method IN ('iPad', 'Paper', 'eDetails')
    )
    OR (
        was_signature_captured = FALSE
        AND signature_method = 'Not Required'
    )
)
