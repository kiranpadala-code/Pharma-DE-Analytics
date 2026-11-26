SELECT
    call_id,
    call_outcome,
    was_sampled,
    was_detailed
FROM {{ ref('stg_pharma__calls_interactions') }}
WHERE NOT (
    (
        call_outcome = 'Sampled'
        AND was_sampled = TRUE
        AND was_detailed = TRUE
    )
    OR (
        call_outcome IN ('Detailed', 'Positive Engagement')
        AND was_sampled = FALSE
        AND was_detailed = TRUE
    )
    OR (
        call_outcome IN (
            'Gatekeeper Block',
            'Left Material',
            'No Contact',
            'Objection Raised'
        )
        AND was_sampled = FALSE
        AND was_detailed = FALSE
    )
)
