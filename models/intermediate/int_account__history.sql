WITH accounts AS (
    SELECT *
    FROM {{ ref('stg_pharma__account_master') }}
),

snapshot_calendar AS (
    SELECT
        snapshot_month,
        LEAD(snapshot_month)
            OVER (ORDER BY snapshot_month)
            AS next_snapshot_month,
        LAG(snapshot_month)
            OVER (ORDER BY snapshot_month)
            AS prev_snapshot_month
    FROM (
        SELECT DISTINCT snapshot_month
        FROM accounts
    ) AS distinct_snapshot
),

hashed AS (
    SELECT
        *,
        HASH(
            account_name,
            address_line1,
            account_type,
            city,
            account_segment,
            state,
            hco_npi,
            zip,
            parent_account_id,
            region,
            bed_count,
            formulary_access,
            is_teaching_hospital,
            is_active,
            is_magnet_hospital
        ) AS attribute_hash
    FROM accounts
),

compared AS (
    SELECT
        *,
        LAG(attribute_hash)
            OVER (PARTITION BY account_id ORDER BY snapshot_month)
            AS prev_attribute_hash,
        LEAD(snapshot_month)
            OVER (PARTITION BY account_id ORDER BY snapshot_month)
            AS next_account_snapshot_month,
        LAG(snapshot_month)
            OVER (PARTITION BY account_id ORDER BY snapshot_month)
            AS prev_account_snapshot_month
    FROM hashed
),

presence_check AS (
    SELECT
        compared.*,
        snapshot_calendar.next_snapshot_month,
        snapshot_calendar.prev_snapshot_month,
        CASE
            WHEN
                snapshot_calendar.next_snapshot_month IS NOT NULL
                AND (
                    compared.next_account_snapshot_month IS NULL
                    OR compared.next_account_snapshot_month
                    > snapshot_calendar.next_snapshot_month
                )
                THEN snapshot_calendar.next_snapshot_month
        END AS disappeared_at
    FROM compared
    INNER JOIN snapshot_calendar
        ON compared.snapshot_month = snapshot_calendar.snapshot_month
),

change_flags AS (
    SELECT
        *,
        CASE
            WHEN
                attribute_hash != prev_attribute_hash
                OR prev_attribute_hash IS NULL
                OR prev_account_snapshot_month < prev_snapshot_month
                THEN 1
            ELSE 0
        END AS version_start_flag
    FROM presence_check
),

version_groups AS (
    SELECT
        *,
        SUM(version_start_flag) OVER (
            PARTITION BY account_id
            ORDER BY snapshot_month
            ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
        ) AS version_group
    FROM change_flags
),

version_boundaries AS (
    SELECT
        *,
        MAX(disappeared_at)
            OVER (PARTITION BY account_id, version_group)
            AS version_disappeared_at
    FROM version_groups
),

changes AS (
    SELECT *
    FROM version_boundaries
    WHERE version_start_flag = 1
),

versioned AS (
    SELECT
        *,
        snapshot_month AS valid_from,
        LEAST_IGNORE_NULLS(
            LEAD(snapshot_month) OVER (
                PARTITION BY account_id
                ORDER BY snapshot_month
            ),
            version_disappeared_at
        ) AS valid_to
    FROM changes
),

final AS (
    SELECT
        MD5(
            account_id || '|' || TO_CHAR(valid_from, 'YYYY-MM-DD')
        ) AS account_sk,
        account_id,
        account_name,
        account_type,
        account_segment,
        hco_npi,
        parent_account_id,
        address_line1,
        city,
        state,
        zip,
        region,
        bed_count,
        is_teaching_hospital,
        is_magnet_hospital,
        formulary_access,
        is_active,
        record_created_date,
        record_updated_date,
        attribute_hash,
        version_group AS version_number,
        valid_from,
        valid_to,
        valid_to IS NULL AS is_current,
        _source_file,
        _loaded_at
    FROM versioned
)

SELECT * FROM final
