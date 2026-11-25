SELECT
    hcp_id,
    tier,
    decile
FROM {{ ref('stg_pharma__hcp_master') }}
WHERE NOT (
    (tier = 'Tier 1' AND decile BETWEEN 1 AND 3)
    OR (tier = 'Tier 2' AND decile BETWEEN 4 AND 6)
    OR (tier = 'Tier 3' AND decile BETWEEN 7 AND 10)
)
