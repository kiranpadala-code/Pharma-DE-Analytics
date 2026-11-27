WITH roster AS (
    SELECT *
    FROM {{ ref('int_roster__history') }}
)

SELECT
    rep_sk,
    rep_id,
    rep_first_name,
    rep_last_name,
    rep_name,
    rep_email,
    role_title,
    channel,
    territory_id,
    territory_name,
    region,
    zone,
    manager_id,
    manager_name,
    product_focus,
    hire_date,
    employee_status,
    target_hcp_count,
    version_number,
    valid_from,
    valid_to,
    is_current
FROM roster
