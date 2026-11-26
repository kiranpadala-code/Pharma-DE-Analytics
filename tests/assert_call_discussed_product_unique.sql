WITH discussed_products AS (

    SELECT
        calls.call_id,
        TRIM(discussed.value::VARCHAR) AS brand_name
    FROM {{ ref('stg_pharma__calls_interactions') }} AS calls,
        LATERAL FLATTEN(
            INPUT => SPLIT(calls.products_discussed, ';')
        ) AS discussed

)

SELECT
    call_id,
    brand_name,
    COUNT(*) AS record_count
FROM discussed_products
GROUP BY call_id, brand_name
HAVING COUNT(*) > 1
