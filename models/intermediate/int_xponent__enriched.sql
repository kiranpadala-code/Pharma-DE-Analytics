WITH xponent AS (
    SELECT *
    FROM {{ ref('stg_pharma__xponent') }}
),

hcp AS (
    SELECT *
    FROM {{ ref('int_hcp__history') }}
),

account AS (
    SELECT *
    FROM {{ ref('int_account__history') }}
),

hcp_enriched AS (
    SELECT
        xponent.*,
        hcp.hcp_sk,
        hcp.hcp_id,
        hcp.account_id,
        hcp.territory_id
    FROM xponent LEFT JOIN hcp ON
        xponent.npi = hcp.npi
        AND xponent.period_month >= hcp.valid_from
        AND (xponent.period_month < hcp.valid_to OR hcp.valid_to IS NULL)
),

account_enriched AS (
    SELECT
        hcp_enriched.*,
        account.account_sk
    FROM hcp_enriched LEFT JOIN account ON
        hcp_enriched.account_id = account.account_id
        AND hcp_enriched.period_month >= account.valid_from
        AND (
            hcp_enriched.period_month < account.valid_to
            OR account.valid_to IS NULL
        )
)

SELECT * FROM account_enriched
