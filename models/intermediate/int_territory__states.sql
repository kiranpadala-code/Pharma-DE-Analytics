WITH territory AS (

    SELECT * FROM {{ ref('stg_pharma__territory') }}

),

normalized AS (

    SELECT
        territory.territory_id,
        territory.territory_name,
        territory.region,
        territory.zone,
        TRIM(UPPER(states.value::VARCHAR)) AS state_code,
        territory._source_file,
        territory._loaded_at
    FROM territory,
        LATERAL FLATTEN(
            INPUT => SPLIT(territory.states_covered, ';')
        ) AS states

)

SELECT *
FROM normalized
