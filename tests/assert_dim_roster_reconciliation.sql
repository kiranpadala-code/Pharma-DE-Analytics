WITH expected AS (
    SELECT rep_sk
    FROM {{ ref('int_roster__history') }}
),

actual AS (
    SELECT rep_sk
    FROM {{ ref('dim_roster') }}
)

SELECT
    expected.rep_sk AS expected_rep_sk,
    actual.rep_sk AS actual_rep_sk
FROM expected
FULL OUTER JOIN actual
    ON expected.rep_sk = actual.rep_sk
WHERE
    expected.rep_sk IS NULL
    OR actual.rep_sk IS NULL
