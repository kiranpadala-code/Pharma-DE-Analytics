WITH account AS (
    SELECT *
    FROM {{ ref('int_account__history') }}
)

SELECT
    account_sk,
    account_id,
    account_name,
    account_type,
    account_segment,
    hco_npi,
    parent_account_id,
    address_line1,
    city,
    state,
    zip,
    region,
    bed_count,
    is_teaching_hospital,
    is_magnet_hospital,
    formulary_access,
    is_active,
    version_number,
    valid_from,
    valid_to,
    is_current
FROM account
