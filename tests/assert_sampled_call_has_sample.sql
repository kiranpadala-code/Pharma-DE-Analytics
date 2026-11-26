WITH calls AS (

    SELECT *
    FROM {{ ref('stg_pharma__calls_interactions') }}

),

samples AS (

    SELECT *
    FROM {{ ref('stg_pharma__samples') }}

)

SELECT
    calls.call_id,
    calls.rep_id,
    calls.npi,
    calls.call_date
FROM calls
LEFT JOIN samples
    ON calls.call_id = samples.call_id
WHERE
    calls.was_sampled = TRUE
    AND samples.sample_id IS NULL
