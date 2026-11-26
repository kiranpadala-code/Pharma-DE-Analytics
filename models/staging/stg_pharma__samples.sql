WITH source AS (

    SELECT *
    FROM {{ source('pharma_raw', 'samples') }}

),

standardized AS (

    SELECT
        UPPER(TRIM(sample_id)) AS sample_id,
        UPPER(TRIM(rep_id)) AS rep_id,
        TRIM(npi) AS npi,
        UPPER(TRIM(product_id)) AS product_id,
        NULLIF(UPPER(TRIM(call_id)), '') AS call_id,
        sample_date,
        TO_DATE(TRIM(load_month) || '-01', 'YYYY-MM-DD') AS load_month,
        qty_dropped,
        TRIM(sample_unit_type) AS sample_unit_type,
        UPPER(TRIM(lot_number)) AS lot_number,
        expiry_date,
        TRIM(strength_sampled) AS strength_sampled,
        TRIM(sample_request_type) AS sample_request_type,
        was_signature_captured,
        NULLIF(TRIM(signature_method), '') AS signature_method,
        UPPER(TRIM(territory_id)) AS territory_id,
        TRIM(sample_program) AS sample_program,
        TRIM(data_source) AS data_source,
        _source_file,
        _loaded_at
    FROM source

)

SELECT *
FROM standardized
