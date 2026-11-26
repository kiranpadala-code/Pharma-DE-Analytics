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
    samples.rep_id,
    samples.npi,
    samples.product_id,
    samples.territory_id,
    samples.sample_date
FROM samples
INNER JOIN calls
    ON samples.call_id = calls.call_id
WHERE
    samples.rep_id != calls.rep_id
    OR samples.npi != calls.npi
    OR samples.product_id != calls.product_id
    OR samples.territory_id != calls.territory_id
    OR samples.sample_date != calls.call_date
