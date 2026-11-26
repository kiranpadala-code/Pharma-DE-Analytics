SELECT *
FROM {{ ref('int_account__history') }}
WHERE valid_to <= valid_from
