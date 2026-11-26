SELECT
    sample_id,
    lot_number
FROM {{ ref('stg_pharma__samples') }}
WHERE NOT REGEXP_LIKE(lot_number, '^LOT-[0-9]{4}-[A-Z0-9]{5}$')
