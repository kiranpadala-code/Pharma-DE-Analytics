# 13 – Architecture and Business Decision Log

Record material decisions here so that the project does not repeatedly revisit settled choices.

| ID | Date | Decision | Rationale | Status |
|---|---|---|---|---|
| DEC-001 | 2026-11-25 | Use synthetic pharmaceutical commercial datasets as project sources. | Existing generated datasets are the project baseline. | Confirmed |
| DEC-002 | 2026-11-25 | Use AWS S3 as cloud file landing/storage. | Demonstrates cloud object storage and warehouse ingestion. | Planned |
| DEC-003 | 2026-11-25 | Use Snowflake as the warehouse. | Existing trial account and SQL experience. | Planned |
| DEC-004 | 2026-11-25 | Use dbt Core for SQL transformations, tests, and documentation. | Existing local installation and completed Fundamentals course. | Planned |
| DEC-005 | 2026-11-25 | Use GitHub for version control and project documentation. | Repository already established. | Planned |
| DEC-006 | 2026-11-25 | Defer Airflow until the basic pipeline works. | Avoid premature orchestration complexity. | Planned |
| DEC-007 | 2026-11-25 | Treat current generated files as the source baseline; do not regenerate without a demonstrated defect. | Avoid repeated generator refinement. | Confirmed |

## Decision template

| Field | Entry |
|---|---|
| ID | DEC-XXX |
| Date | YYYY-MM-DD |
| Context | What decision is needed? |
| Options considered | What alternatives were evaluated? |
| Decision | What was selected? |
| Rationale | Why? |
| Consequences | What changes because of this? |
| Status | Proposed / Confirmed / Superseded |

Add a new row for decisions such as:
- Xponent append vs merge.
- HCP/Account SCD strategy.
- RAW file-level vs consolidated table approach.
- dbt incremental unique keys.
- Market share aggregation definition.
