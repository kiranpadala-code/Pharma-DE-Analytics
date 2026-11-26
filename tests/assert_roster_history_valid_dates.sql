SELECT *
FROM {{ ref('int_roster__history') }}
WHERE valid_to <= valid_from
