WITH samples AS (

    SELECT *
    FROM {{ ref('stg_pharma__samples') }}

),

roster AS (

    SELECT *
    FROM {{ ref('stg_pharma__roster') }}

)

SELECT
    samples.sample_id,
    samples.rep_id,
    samples.sample_date,
    roster.hire_date
FROM samples
INNER JOIN roster
    ON
        samples.rep_id = roster.rep_id
        AND DATE_TRUNC('MONTH', samples.sample_date) = roster.snapshot_month
WHERE samples.sample_date < roster.hire_date
