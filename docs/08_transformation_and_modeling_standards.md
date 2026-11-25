# 08 – Transformation and Modeling Standards

## 1. dbt project layers

Recommended model organization:

```text
pharma_analytics/
└── models/
    ├── staging/
    │   ├── source_system/
    │   │   ├── _source_system__sources.yml
    │   │   ├── stg_calls_interactions.sql
    │   │   ├── stg_samples.sql
    │   │   ├── stg_xponent.sql
    │   │   ├── stg_product.sql
    │   │   ├── stg_territory.sql
    │   │   ├── stg_specialty_product_map.sql
    │   │   ├── stg_account_master.sql
    │   │   ├── stg_hcp_master.sql
    │   │   └── stg_roster.sql
    ├── intermediate/
    │   ├── int_call_details.sql
    │   ├── int_sample_details.sql
    │   ├── int_prescription_details.sql
    │   └── int_product_performance.sql
    └── marts/
        ├── dimensions/
        ├── facts/
        └── analytics/
```

Adapt the folder names to the existing dbt project rather than recreating the project.

## 2. Staging standards

- One primary staging model per source table.
- Use consistent lowercase snake_case names.
- Explicitly cast data types.
- Apply consistent date and timestamp handling.
- Trim strings where appropriate.
- Convert empty strings to NULL only where semantically appropriate.
- Preserve source grain.
- Avoid complex business aggregations in staging.
- Declare source tables in YAML.
- Document model and column descriptions.

## 3. Intermediate standards

- Implement reusable joins and business transformations.
- Keep model grain explicit in model descriptions.
- Avoid fact-to-fact fanout.
- Use CTEs with meaningful names.
- Avoid `SELECT *` in curated models.
- Keep business logic reusable and testable.
- Validate join cardinality and row-count impact.

## 4. Marts standards

### Candidate dimensions

- `dim_product`
- `dim_territory`
- `dim_hcp`
- `dim_account`
- `dim_rep`
- `dim_date` (generated if required)

### Candidate facts

- `fct_calls`
- `fct_samples`
- `fct_prescriptions` (after grain confirmation)

### Candidate analytics models

- `mart_territory_performance`
- `mart_rep_performance`
- `mart_hcp_engagement`
- `mart_product_performance`
- `mart_sample_effectiveness`
- `mart_monthly_commercial_summary`

These are targets, not yet implemented models. Final columns and grain must be specified before development.

## 5. Materialization guidance

| Model type | Initial recommendation |
|---|---|
| Staging | View |
| Intermediate | View initially |
| Small dimensions | Table |
| Large/event facts | Incremental where justified |
| Analytics marts | Table or view depending on reuse and query needs |

Do not choose incremental materialization solely because it is available. Define the unique key, incremental filter, late-arriving data behavior, and full-refresh strategy first.

## 6. Naming conventions

| Object | Convention | Example |
|---|---|---|
| Source declaration | source name | `src_pharma` |
| Staging model | `stg_<source>` | `stg_calls_interactions` |
| Intermediate model | `int_<subject>` | `int_call_details` |
| Dimension | `dim_<entity>` | `dim_hcp` |
| Fact | `fct_<process>` | `fct_calls` |
| Mart | `mart_<subject>` | `mart_product_performance` |
| Singular test | descriptive SQL filename | `assert_no_negative_sample_qty.sql` |

## 7. dbt execution

Typical development commands:

```bash
dbt debug
dbt parse
dbt build
dbt test
dbt docs generate
```

Use targeted commands during development, for example:

```bash
dbt build --select stg_calls_interactions
```

Confirm the active dbt target and schema configuration before execution.

## 8. Incremental model requirements

Every incremental model must document:

- Grain and unique key.
- Source of new/changed records.
- Incremental filter.
- Merge/append behavior.
- Late-arriving record handling.
- Corrected historical record handling.
- Full-refresh procedure.
- Rerun/idempotency test.
