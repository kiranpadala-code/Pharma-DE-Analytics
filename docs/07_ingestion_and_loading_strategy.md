# 07 – Ingestion and Loading Strategy

## 1. Objective

Move source CSV files into Snowflake RAW through an organized, traceable, repeatable ingestion process.

## 2. Proposed S3 structure

```text
s3://<bucket-name>/
└── pharma/
    └── raw/
        ├── calls_interactions/
        │   └── load_month=2026-01/
        ├── samples/
        │   └── load_month=2026-01/
        ├── xponent/
        │   └── load_month=2026-01/
        ├── product/
        ├── territory/
        ├── specialty_product_map/
        ├── account_master/
        │   └── load_month=2026-01/
        ├── hcp_master/
        │   └── load_month=2026-01/
        └── roster/
            └── load_month=2026-01/
```

The exact naming convention and partition/prefix structure will be finalized during the S3 phase.

## 3. Proposed Snowflake ingestion components

1. AWS IAM role/policy for approved access.
2. Snowflake storage integration.
3. External stage pointing to the approved S3 prefix.
4. CSV file format with explicit delimiter, header, quote, escape, and null handling.
5. RAW tables with source columns and technical ingestion metadata.
6. `COPY INTO` or an equivalent controlled load process.
7. Load-history and reconciliation checks.

## 4. Dataset loading strategy

| Dataset | Initial strategy | Subsequent strategy | Important condition |
|---|---|---|---|
| Calls_Interactions | Load all baseline files | Append new events with duplicate protection | Confirm call_id stability |
| Samples | Load all baseline files | Append new events with duplicate protection | Confirm sample_id stability |
| Xponent | Load all baseline files | Append or MERGE | Confirm whether periods can be revised |
| Product | Load reference data | Full refresh or MERGE | Confirm whether product attributes change |
| Territory | Load reference data | Full refresh or MERGE | Confirm whether territory definitions change |
| Specialty_product_map | Load reference mapping | Full refresh or MERGE | Confirm mapping update behavior |
| Account_master | Load initial baseline | MERGE/upsert | Confirm snapshot vs delta and history needs |
| HCP_master | Load initial baseline | MERGE/upsert | Confirm snapshot vs delta and history needs |
| Roster | Load initial baseline | MERGE/upsert | Confirm snapshot vs delta and history needs |

## 5. Initial and incremental processing

### Initial load

- Inventory all baseline files.
- Validate file structure and content.
- Upload files to S3.
- Load all applicable historical records to RAW.
- Capture file-level load metadata.
- Reconcile file row counts with Snowflake load counts.

### Subsequent load

- Identify newly delivered files.
- Validate file name, schema, month, and content.
- Detect already processed files.
- Upload new files to S3.
- Load only eligible files.
- Apply append or merge logic according to dataset behavior.
- Reconcile counts and measures.
- Record success/failure status.

## 6. Idempotency and duplicate prevention

The pipeline must be safe to rerun.

Proposed controls:

- Track source filename and load identifier.
- Optionally calculate a file checksum.
- Maintain an ingestion audit table.
- Do not mark a file as successfully processed until the load and validation complete.
- Use stable business keys for MERGE where appropriate.
- Define how to handle a corrected file with the same name but different contents.
- Test reruns explicitly.

## 7. RAW metadata

Proposed technical columns:

| Column | Purpose |
|---|---|
| `_SOURCE_FILE` | File that supplied the row |
| `_LOADED_AT` | Ingestion timestamp |
| `_LOAD_ID` | Unique ingestion execution identifier |

Do not confuse source `load_month` with technical ingestion timestamp.

## 8. Error handling

- Reject or quarantine files with missing required columns or invalid structure.
- Preserve enough information to diagnose rejected rows.
- Do not silently discard malformed records.
- Record load errors and Snowflake query identifiers.
- Prevent downstream dbt execution when required RAW ingestion has failed.

## 9. Loading strategy decisions still open

- Exact file naming convention.
- Whether to use one RAW table per dataset or separate landing tables by source file before consolidation.
- Corrected-file handling.
- Xponent restatement policy.
- Master-data snapshot/delta semantics.
- Whether `load_month` is source business metadata or file delivery metadata in every dataset.
