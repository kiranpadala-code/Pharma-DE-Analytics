SELECT *
FROM {{ ref('int_hcp__history') }}
WHERE valid_to <= valid_from
