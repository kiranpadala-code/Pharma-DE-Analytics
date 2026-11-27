WITH enriched AS (
    SELECT
        sample_id,
        hcp_sk,
        npi,
        hcp_id,
        account_id,
        sample_date
    FROM {{ ref('int_samples__enriched') }}
),

hcp AS (
    SELECT
        hcp_sk,
        npi,
        hcp_id,
        account_id,
        valid_from,
        valid_to
    FROM {{ ref('int_hcp__history') }}
)

SELECT
    enriched.*,
    hcp.npi AS expected_npi,
    hcp.hcp_id AS expected_hcp_id,
    hcp.account_id AS expected_account_id,
    hcp.valid_from,
    hcp.valid_to
FROM enriched
INNER JOIN hcp
    ON enriched.hcp_sk = hcp.hcp_sk
WHERE
    enriched.npi IS DISTINCT FROM hcp.npi
    OR enriched.hcp_id IS DISTINCT FROM hcp.hcp_id
    OR enriched.account_id IS DISTINCT FROM hcp.account_id
    OR enriched.sample_date < hcp.valid_from
    OR enriched.sample_date >= hcp.valid_to
