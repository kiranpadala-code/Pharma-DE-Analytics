WITH enriched AS (
    SELECT
        call_id,
        account_sk,
        account_id,
        call_date
    FROM {{ ref('int_calls__enriched') }}
),

account AS (
    SELECT
        account_sk,
        account_id,
        valid_from,
        valid_to
    FROM {{ ref('int_account__history') }}
)

SELECT
    enriched.*,
    account.account_id AS expected_account_id,
    account.valid_from,
    account.valid_to
FROM enriched
INNER JOIN account
    ON enriched.account_sk = account.account_sk
WHERE
    enriched.account_id IS DISTINCT FROM account.account_id
    OR enriched.call_date < account.valid_from
    OR enriched.call_date >= account.valid_to
