WITH expected AS (
    SELECT account_sk
    FROM {{ ref('int_account__history') }}
),

actual AS (
    SELECT account_sk
    FROM {{ ref('dim_account') }}
)

SELECT
    expected.account_sk AS expected_account_sk,
    actual.account_sk AS actual_account_sk
FROM expected
FULL OUTER JOIN actual
    ON expected.account_sk = actual.account_sk
WHERE
    expected.account_sk IS NULL
    OR actual.account_sk IS NULL
