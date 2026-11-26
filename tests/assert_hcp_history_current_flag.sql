SELECT *
FROM {{ ref('int_hcp__history') }}
WHERE is_current != (valid_to IS NULL)
