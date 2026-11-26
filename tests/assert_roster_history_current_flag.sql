SELECT *
FROM {{ ref('int_roster__history') }}
WHERE is_current != (valid_to IS NULL)
