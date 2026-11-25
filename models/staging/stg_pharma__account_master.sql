-- Grain: One record per account per snapshot month.
-- Purpose: Standardize account master data and preserve historical snapshots.

WITH source AS (
    SELECT * FROM {{ source('pharma_raw', 'account_master') }}
),

standardized AS (
    SELECT
        UPPER(TRIM(account_id)) AS account_id,
        TRIM(account_name) AS account_name,
        TRIM(account_type) AS account_type,
        TRIM(account_segment) AS account_segment,
        TRIM(hco_npi) AS hco_npi,
        NULLIF(UPPER(TRIM(parent_account_id)), '') AS parent_account_id,
        TRIM(address_line1) AS address_line1,
        TRIM(city) AS city,
        UPPER(TRIM(state)) AS state,
        TRIM(zip) AS zip,
        TRIM(region) AS region,
        bed_count,
        is_teaching_hospital,
        is_magnet_hospital,
        TRIM(formulary_access) AS formulary_access,
        is_active,
        record_created_date,
        record_updated_date,
        TO_DATE(TRIM(load_month) || '-01', 'YYYY-MM-DD') AS snapshot_month,
        _source_file,
        _loaded_at
    FROM source
)

SELECT * FROM standardized
