# 01 – Scope and Success Criteria

## 1. In scope

- Synthetic CSV source data covering January–June 2026, subject to the actual files present.
- Nine source datasets: Calls_Interactions, Samples, Xponent, Product, Territory, Specialty_product_map, Account_master, HCP_master, and Roster.
- AWS S3 as the cloud landing/storage layer.
- Snowflake as the warehouse.
- dbt Core for transformations, tests, documentation, and lineage.
- Python for file validation and ingestion support.
- GitHub for version control and project documentation.
- Optional Apache Airflow orchestration after a working pipeline exists.
- Analytics-ready outputs for call activity, samples, prescription performance, HCP engagement, representative activity, territory performance, and product performance.

## 2. Out of scope

- Real patient-level data or protected health information.
- Real prescription claims processing.
- Clinical recommendations or patient treatment decisions.
- Production regulatory compliance certification.
- Proof that sample distribution causes prescription growth.
- Enterprise-scale streaming or near-real-time processing.
- Mandatory use of Spark, Kafka, AWS Glue, Lambda, or other services not needed for the stated objective.

## 3. Geographic and time boundaries

- Reporting period in the supplied synthetic data: January–June 2026.
- Geographic coverage: only the states and territories present in the source data.
- Do not infer missing geographic coverage.

## 4. Success criteria

The project is considered complete when:

- All expected source files are inventoried and loaded.
- File schema and load metadata are retained.
- Re-running ingestion does not create duplicate records.
- Incremental and master-data loading strategies are implemented and tested.
- dbt staging, intermediate, fact, dimension, and mart models build successfully.
- Primary-key, not-null, accepted-value, relationship, and custom business tests are implemented where applicable.
- Source-to-target row counts and key measures reconcile.
- Pipeline failures are visible through logs and execution status.
- A new monthly delivery can be processed using documented steps.
- A reviewer can understand the architecture, model definitions, assumptions, and how to run the project.

## 5. Definition of done by layer

| Layer | Definition of done |
|---|---|
| Source | Files inventoried; schema, keys, grain and assumptions documented |
| S3 | Files stored under documented prefixes |
| RAW | Source-aligned tables loaded with file and load metadata |
| STAGING | Types, naming and basic standardization applied |
| INTERMEDIATE | Reusable joins and business calculations validated |
| MARTS | Documented, analytics-ready facts, dimensions and summary outputs |
| Quality | Tests run and failures investigated |
| Automation | Pipeline can be rerun safely and reports status |
| Documentation | Setup, design, data definitions and run instructions are current |
