WITH hcp AS (
    SELECT *
    FROM {{ ref('int_hcp__history') }}
)

SELECT
    hcp_sk,
    hcp_id,
    npi,
    first_name,
    last_name,
    full_name,
    degree,
    specialty,
    sub_specialty,
    gender,
    address_line1,
    city,
    state,
    zip,
    account_id,
    territory_id,
    tier,
    decile,
    target_segment,
    is_kol,
    is_target,
    is_active,
    years_in_practice,
    data_source,
    version_number,
    valid_from,
    valid_to,
    is_current
FROM hcp
