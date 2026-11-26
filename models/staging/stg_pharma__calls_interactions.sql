WITH source AS (

    SELECT *
    FROM {{ source('pharma_raw', 'calls_interactions') }}

),

standardized AS (

    SELECT
        UPPER(TRIM(call_id)) AS call_id,
        UPPER(TRIM(rep_id)) AS rep_id,
        TRIM(npi) AS npi,
        UPPER(TRIM(product_id)) AS product_id,
        call_date,
        TO_DATE(TRIM(load_month) || '-01', 'YYYY-MM-DD') AS load_month,
        TRIM(call_type) AS call_type,
        TRIM(call_channel) AS call_channel,
        TRIM(call_outcome) AS call_outcome,
        TRIM(products_discussed) AS products_discussed,
        TRIM(primary_message) AS primary_message,
        was_sampled,
        was_detailed,
        call_duration_min,
        call_rank_in_month,
        UPPER(TRIM(territory_id)) AS territory_id,
        next_call_planned_date,
        is_compliant_call,
        TRIM(call_notes) AS call_notes,
        TRIM(data_source) AS data_source,
        _source_file,
        _loaded_at
    FROM source

)

SELECT *
FROM standardized
