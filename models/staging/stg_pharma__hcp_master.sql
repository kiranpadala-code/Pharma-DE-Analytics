WITH source AS (
    SELECT * FROM {{ source('pharma_raw', 'hcp_master') }}
),

standardized AS (
    SELECT
        UPPER(TRIM(hcp_id)) AS hcp_id,
        TRIM(npi) AS npi,
        TRIM(first_name) AS first_name,
        TRIM(last_name) AS last_name,
        TRIM(full_name) AS full_name,
        UPPER(TRIM(degree)) AS degree,
        TRIM(specialty) AS specialty,
        TRIM(sub_specialty) AS sub_specialty,
        TRIM(gender) AS gender,
        TRIM(address_line1) AS address_line1,
        TRIM(city) AS city,
        UPPER(TRIM(state)) AS state,
        TRIM(zip) AS zip,
        UPPER(TRIM(account_id)) AS account_id,
        UPPER(TRIM(territory_id)) AS territory_id,
        TRIM(tier) AS tier,
        decile,
        TRIM(target_segment) AS target_segment,
        is_kol,
        is_target,
        is_active,
        years_in_practice,
        TRIM(data_source) AS data_source,
        record_created_date,
        TO_DATE(TRIM(load_month) || '-01', 'YYYY-MM-DD') AS snapshot_month,
        _source_file,
        _loaded_at
    FROM source
)

SELECT * FROM standardized
