SELECT *
FROM {{ ref('int_account__history') }}
WHERE is_current != (valid_to IS NULL)
