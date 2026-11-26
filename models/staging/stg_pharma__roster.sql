WITH source AS (

    SELECT *
    FROM {{ source('pharma_raw', 'roster') }}

),

standardized AS (

    SELECT
        UPPER(TRIM(rep_id)) AS rep_id,
        TRIM(rep_first_name) AS rep_first_name,
        TRIM(rep_last_name) AS rep_last_name,
        TRIM(rep_name) AS rep_name,
        LOWER(TRIM(rep_email)) AS rep_email,
        TRIM(role_title) AS role_title,
        TRIM(channel) AS channel,
        UPPER(TRIM(territory_id)) AS territory_id,
        TRIM(territory_name) AS territory_name,
        TRIM(region) AS region,
        TRIM(zone) AS zone,
        UPPER(TRIM(manager_id)) AS manager_id,
        TRIM(manager_name) AS manager_name,
        TRIM(product_focus) AS product_focus,
        hire_date,
        TRIM(employee_status) AS employee_status,
        target_hcp_count,
        TO_DATE(TRIM(load_month) || '-01', 'YYYY-MM-DD') AS snapshot_month,
        _source_file,
        _loaded_at
    FROM source

)

SELECT *
FROM standardized
