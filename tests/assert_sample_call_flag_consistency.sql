WITH samples AS (

    SELECT *
    FROM {{ ref('stg_pharma__samples') }}

),

calls AS (

    SELECT *
    FROM {{ ref('stg_pharma__calls_interactions') }}

)

SELECT
    samples.sample_id,
    samples.call_id,
    calls.was_sampled
FROM samples
INNER JOIN calls
    ON samples.call_id = calls.call_id
WHERE calls.was_sampled = FALSE
