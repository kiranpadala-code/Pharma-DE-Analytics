WITH enriched AS (
    SELECT
        rx_id,
        hcp_sk,
        npi,
        hcp_id,
        account_id,
        territory_id,
        period_month
    FROM {{ ref('int_xponent__enriched') }}
),

hcp AS (
    SELECT
        hcp_sk,
        npi,
        hcp_id,
        account_id,
        territory_id,
        valid_from,
        valid_to
    FROM {{ ref('int_hcp__history') }}
)

SELECT
    enriched.*,
    hcp.valid_from,
    hcp.valid_to
FROM enriched INNER JOIN hcp
    ON
        enriched.hcp_sk = hcp.hcp_sk
WHERE
    enriched.npi IS DISTINCT FROM hcp.npi
    OR enriched.hcp_id IS DISTINCT FROM hcp.hcp_id
    OR enriched.account_id IS DISTINCT FROM hcp.account_id
    OR enriched.territory_id IS DISTINCT FROM hcp.territory_id
    OR enriched.period_month < hcp.valid_from
    OR enriched.period_month >= hcp.valid_to
