WITH expected AS (
    SELECT
        count(*) AS record_count,
        sum(trx_count) AS total_trx_count,
        sum(nrx_count) AS total_nrx_count,
        sum(refill_count) AS total_refill_count,
        sum(market_trx) AS total_market_trx_count
    FROM {{ ref('stg_pharma__xponent') }}
),

actual AS (
    SELECT
        count(*) AS record_count,
        sum(trx_count) AS total_trx_count,
        sum(nrx_count) AS total_nrx_count,
        sum(refill_count) AS total_refill_count,
        sum(market_trx) AS total_market_trx_count
    FROM {{ ref('int_xponent__enriched') }}
)

SELECT
    expected.*,
    actual.*
FROM expected CROSS JOIN actual
WHERE
    expected.record_count IS DISTINCT FROM actual.record_count
    OR expected.total_trx_count IS DISTINCT FROM actual.total_trx_count
    OR expected.total_nrx_count IS DISTINCT FROM actual.total_nrx_count
    OR expected.total_refill_count IS DISTINCT FROM actual.total_refill_count
    OR expected.total_market_trx_count IS DISTINCT FROM actual.total_market_trx_count
