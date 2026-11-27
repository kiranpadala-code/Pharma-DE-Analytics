WITH expected AS (
    SELECT hcp_sk
    FROM {{ ref('int_hcp__history') }}
),

actual AS (
    SELECT hcp_sk
    FROM {{ ref('dim_hcp') }}
)

SELECT
    expected.hcp_sk AS expected_hcp_sk,
    actual.hcp_sk AS actual_hcp_sk
FROM expected
FULL OUTER JOIN actual
    ON expected.hcp_sk = actual.hcp_sk
WHERE
    expected.hcp_sk IS NULL
    OR actual.hcp_sk IS NULL
