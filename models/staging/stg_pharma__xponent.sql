WITH source AS (

    SELECT *
    FROM {{ source('pharma_raw', 'xponent') }}

),

standardized AS (

    SELECT
        UPPER(TRIM(rx_id)) AS rx_id,
        TRIM(npi) AS npi,
        UPPER(TRIM(product_id)) AS product_id,
        TO_DATE(TRIM(period) || '-01', 'YYYY-MM-DD') AS period_month,
        TO_DATE(TRIM(load_month) || '-01', 'YYYY-MM-DD') AS load_month,
        trx_count,
        nrx_count,
        refill_count,
        trx_change_vs_prior_month,
        market_trx,
        market_share_pct,
        UPPER(TRIM(state)) AS state,
        TRIM(specialty) AS specialty,
        TRIM(channel) AS channel,
        days_supply_avg,
        TRIM(payer_type) AS payer_type,
        TRIM(formulary_status_at_time) AS formulary_status_at_time,
        TRIM(data_source) AS data_source,
        _source_file,
        _loaded_at
    FROM source

)

SELECT *
FROM standardized
