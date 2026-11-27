WITH samples AS (
    SELECT *
    FROM {{ ref('stg_pharma__samples') }}
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
        samples.*,
        hcp.hcp_sk,
        hcp.hcp_id,
        hcp.account_id
    FROM samples
    LEFT JOIN hcp
        ON
            samples.npi = hcp.npi
            AND samples.sample_date >= hcp.valid_from
            AND (
                samples.sample_date < hcp.valid_to
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
            AND hcp_enriched.sample_date >= account.valid_from
            AND (
                hcp_enriched.sample_date < account.valid_to
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
            AND account_enriched.sample_date >= roster.valid_from
            AND (
                account_enriched.sample_date < roster.valid_to
                OR roster.valid_to IS NULL
            )
)

SELECT * FROM roster_enriched
