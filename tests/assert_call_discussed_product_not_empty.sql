SELECT
    calls.call_id,
    calls.products_discussed,
    TRIM(discussed.value::VARCHAR) AS brand_name
FROM {{ ref('stg_pharma__calls_interactions') }} AS calls,
    LATERAL FLATTEN(
        INPUT => SPLIT(calls.products_discussed, ';')
    ) AS discussed
WHERE TRIM(discussed.value::VARCHAR) = ''
