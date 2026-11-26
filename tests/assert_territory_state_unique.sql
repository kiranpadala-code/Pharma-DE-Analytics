SELECT
    territory_id,
    state_code,
    count(*) AS total_count
FROM
    {{ ref('int_territory__states') }}
GROUP BY territory_id, state_code
HAVING count(*) > 1
