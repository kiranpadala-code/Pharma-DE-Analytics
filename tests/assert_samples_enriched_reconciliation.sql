WITH expected AS (
    SELECT
        COUNT(*) AS record_count,
        SUM(qty_dropped) AS total_quantity,
        COUNT(call_id) AS linked_samples,
        COUNT_IF(call_id IS NULL) AS standalone_samples
    FROM {{ ref('stg_pharma__samples') }}
),

actual AS (
    SELECT
        COUNT(*) AS record_count,
        SUM(qty_dropped) AS total_quantity,
        COUNT(call_id) AS linked_samples,
        COUNT_IF(call_id IS NULL) AS standalone_samples
    FROM {{ ref('int_samples__enriched') }}
)

SELECT
    expected.record_count AS expected_record_count,
    actual.record_count AS actual_record_count,
    expected.total_quantity AS expected_quantity,
    actual.total_quantity AS actual_quantity,
    expected.linked_samples AS expected_linked_samples,
    actual.linked_samples AS actual_linked_samples,
    expected.standalone_samples AS expected_standalone_samples,
    actual.standalone_samples AS actual_standalone_samples
FROM expected
CROSS JOIN actual
WHERE
    expected.record_count IS DISTINCT FROM actual.record_count
    OR expected.total_quantity IS DISTINCT FROM actual.total_quantity
    OR expected.linked_samples IS DISTINCT FROM actual.linked_samples
    OR expected.standalone_samples IS DISTINCT FROM actual.standalone_samples
