WITH enriched AS (
    SELECT
        call_id,
        rep_sk,
        rep_id,
        territory_id,
        call_date
    FROM {{ ref('int_calls__enriched') }}
),

roster AS (
    SELECT
        rep_sk,
        rep_id,
        territory_id,
        valid_from,
        valid_to
    FROM {{ ref('int_roster__history') }}
)

SELECT
    enriched.*,
    roster.rep_id AS expected_rep_id,
    roster.territory_id AS expected_territory_id,
    roster.valid_from,
    roster.valid_to
FROM enriched
INNER JOIN roster
    ON enriched.rep_sk = roster.rep_sk
WHERE
    enriched.rep_id IS DISTINCT FROM roster.rep_id
    OR enriched.territory_id IS DISTINCT FROM roster.territory_id
    OR enriched.call_date < roster.valid_from
    OR enriched.call_date >= roster.valid_to
