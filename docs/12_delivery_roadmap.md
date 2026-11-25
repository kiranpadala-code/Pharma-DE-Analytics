# 12 – Delivery Roadmap

Work sequentially. Complete the acceptance criteria for a phase before starting the next one.

## Phase 0 – Project definition and source validation

**Objective:** Establish a reliable source-data baseline and design.

Tasks:
- Inventory all files and months.
- Validate schemas and record counts.
- Validate candidate keys and relationships.
- Confirm source grain and business rules.
- Document assumptions and open questions.
- Freeze source files unless a real defect is found.

**Deliverable:** Source inventory, data dictionary, business rules, and model relationship specification.

**Status:** Initial validation reported; documentation and open decisions remain.

## Phase 1 – AWS S3 setup

**Objective:** Establish a cloud landing zone.

Tasks:
- Create a private S3 bucket.
- Define dataset prefixes and month folders.
- Upload source files.
- Configure least-privilege access.
- Verify file presence and sizes.

**Deliverable:** Organized S3 landing zone.

## Phase 2 – Snowflake ingestion

**Objective:** Load files from S3 into RAW.

Tasks:
- Configure storage integration.
- Create file format and external stage.
- Create RAW tables.
- Load files.
- Capture technical metadata.
- Reconcile row counts.

**Deliverable:** Source-aligned RAW tables.

## Phase 3 – dbt staging

**Objective:** Standardize source data.

Tasks:
- Declare dbt sources.
- Build staging models.
- Cast types and standardize fields.
- Add source-level tests and documentation.

**Deliverable:** Tested staging models.

## Phase 4 – Intermediate transformations

**Objective:** Implement reusable integration logic.

Tasks:
- Build validated joins.
- Resolve grain and cardinality.
- Implement reusable business calculations.
- Test row counts and measure preservation.

**Deliverable:** Integrated intermediate models.

## Phase 5 – Dimensional models and marts

**Objective:** Publish analytics-ready structures.

Tasks:
- Build dimensions.
- Build fact models.
- Implement incremental strategies.
- Implement selected history tracking if justified.
- Build analytical marts.

**Deliverable:** Curated warehouse and business outputs.

## Phase 6 – Data quality and reconciliation

**Objective:** Establish automated confidence checks.

Tasks:
- Generic dbt tests.
- Singular business-rule tests.
- Referential integrity tests.
- Source-to-target reconciliation.
- Failure handling and diagnostic output.

**Deliverable:** Repeatable data-quality framework.

## Phase 7 – Python pipeline automation

**Objective:** Execute ingestion and dbt steps consistently.

Tasks:
- Detect new files.
- Validate and upload.
- Trigger Snowflake loading.
- Execute dbt commands.
- Capture logs and statuses.
- Test safe reruns.

**Deliverable:** Repeatable end-to-end execution.

## Phase 8 – Airflow (optional advanced phase)

**Objective:** Orchestrate the workflow using a DAG.

Tasks:
- Define tasks and dependencies.
- Add retries and failure handling.
- Configure schedules.
- Monitor execution and logs.

**Deliverable:** Airflow-orchestrated pipeline.

## Phase 9 – Finalization

**Objective:** Make the project reviewable.

Tasks:
- Generate dbt documentation.
- Update architecture and data dictionary.
- Add setup and execution instructions.
- Add representative SQL queries and results.
- Review Git history and repository hygiene.

**Deliverable:** Portfolio-ready GitHub repository.

## Priority under trial constraints

Prioritize getting data into Snowflake and building the core dbt models while the Snowflake trial is available. Do not spend the initial implementation window on optional Airflow or advanced services.
