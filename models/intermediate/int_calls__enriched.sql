WITH calls AS (
    SELECT *
    FROM {{ ref('stg_pharma__calls_interactions') }}
),

hcp AS (
    SELECT *
    FROM {{ ref('int_hcp__history') }}
),

account AS (
    SELECT *
    FROM {{ ref('int_account__history') }}
),

roster AS (
    SELECT *
    FROM {{ ref('int_roster__history') }}
),

hcp_enriched AS (
    SELECT
        calls.*,
        hcp.hcp_sk,
        hcp.hcp_id,
        hcp.account_id
    FROM calls
    LEFT JOIN hcp
        ON
            calls.npi = hcp.npi
            AND calls.call_date >= hcp.valid_from
            AND (
                calls.call_date < hcp.valid_to
                OR hcp.valid_to IS NULL
            )
),

account_enriched AS (
    SELECT
        hcp_enriched.*,
        account.account_sk
    FROM hcp_enriched
    LEFT JOIN account
        ON
            hcp_enriched.account_id = account.account_id
            AND hcp_enriched.call_date >= account.valid_from
            AND (
                hcp_enriched.call_date < account.valid_to
                OR account.valid_to IS NULL
            )
),

roster_enriched AS (
    SELECT
        account_enriched.*,
        roster.rep_sk
    FROM account_enriched
    LEFT JOIN roster
        ON
            account_enriched.rep_id = roster.rep_id
            AND account_enriched.call_date >= roster.valid_from
            AND (
                account_enriched.call_date < roster.valid_to
                OR roster.valid_to IS NULL
            )
)

SELECT * FROM roster_enriched
