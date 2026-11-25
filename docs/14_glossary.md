# 14 – Glossary

| Term | Meaning in this project |
|---|---|
| Account | Healthcare organization or commercial account represented in Account_master |
| AWS S3 | Amazon Simple Storage Service; cloud object storage |
| dbt | Data Build Tool; SQL transformation and testing framework |
| Dimension | Descriptive entity table used to provide context to facts |
| Fact | Table recording measurable business events or periodic measures |
| HCO | Healthcare organization |
| HCP | Healthcare professional |
| IAM | AWS Identity and Access Management |
| Idempotency | Repeating an operation produces no unintended duplicate or changed result |
| INT | Intermediate transformation layer |
| MARTS | Curated business-facing data layer |
| MERGE | Database operation that inserts and/or updates matched records |
| NPI | National Provider Identifier; identifier used for US healthcare providers/organizations |
| RAW | Source-aligned warehouse ingestion layer |
| SCD | Slowly Changing Dimension; approach for managing changing dimension attributes |
| SCD Type 1 | Overwrite an old attribute value with the latest value |
| SCD Type 2 | Preserve historical versions of dimension records |
| S3 stage | Snowflake object referencing files in an S3 location |
| STAGING | Source-standardization transformation layer |
| TRx | Total prescriptions, according to the supplied Xponent field definition |
| NRx | New prescriptions, according to the supplied Xponent field definition |
| Grain | What one row in a table represents |
| Fanout | Unintended row multiplication caused by joins |
| Orphan record | Record with a foreign key that does not resolve to a referenced entity |
| Source reconciliation | Comparing source counts/measures with loaded or transformed results |
