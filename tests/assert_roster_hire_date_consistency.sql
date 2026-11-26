SELECT
    rep_id,
    rep_name,
    hire_date,
    snapshot_month,
    employee_status
FROM {{ ref('stg_pharma__roster') }}
WHERE hire_date > snapshot_month
