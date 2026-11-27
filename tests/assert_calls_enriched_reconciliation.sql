WITH expected AS (
    SELECT
        COUNT(*) AS record_count,
        SUM(call_duration_min) AS total_duration,
        COUNT_IF(was_sampled) AS sampled_calls,
        COUNT_IF(was_detailed) AS detailed_calls,
        COUNT_IF(is_compliant_call) AS compliant_calls
    FROM {{ ref('stg_pharma__calls_interactions') }}
),

actual AS (
    SELECT
        COUNT(*) AS record_count,
        SUM(call_duration_min) AS total_duration,
        COUNT_IF(was_sampled) AS sampled_calls,
        COUNT_IF(was_detailed) AS detailed_calls,
        COUNT_IF(is_compliant_call) AS compliant_calls
    FROM {{ ref('int_calls__enriched') }}
)

SELECT
    expected.record_count AS expected_record_count,
    actual.record_count AS actual_record_count,
    expected.total_duration AS expected_duration,
    actual.total_duration AS actual_duration,
    expected.sampled_calls AS expected_sampled_calls,
    actual.sampled_calls AS actual_sampled_calls,
    expected.detailed_calls AS expected_detailed_calls,
    actual.detailed_calls AS actual_detailed_calls,
    expected.compliant_calls AS expected_compliant_calls,
    actual.compliant_calls AS actual_compliant_calls
FROM expected
CROSS JOIN actual
WHERE
    expected.record_count IS DISTINCT FROM actual.record_count
    OR expected.total_duration IS DISTINCT FROM actual.total_duration
    OR expected.sampled_calls IS DISTINCT FROM actual.sampled_calls
    OR expected.detailed_calls IS DISTINCT FROM actual.detailed_calls
    OR expected.compliant_calls IS DISTINCT FROM actual.compliant_calls
