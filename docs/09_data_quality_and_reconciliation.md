# 09 – Data Quality and Reconciliation Framework

## 1. Objective

Ensure that data is complete, valid, consistent, referentially sound, and reconciled from source files through curated Snowflake outputs.

## 2. Quality dimensions

| Dimension | Meaning | Example |
|---|---|---|
| Completeness | Required values are populated | `call_id` is not null |
| Uniqueness | Keys are not duplicated | `sample_id` unique |
| Validity | Values meet defined constraints | sample quantity positive |
| Referential integrity | Foreign keys resolve | product_id exists in Product |
| Consistency | Related values agree | TRx decomposition, if applicable |
| Timeliness | Expected delivery is available | monthly file received |
| Reconciliation | Counts/measures agree across layers | source rows equal loaded rows |

## 3. Source/file checks

- Expected file present.
- Expected columns present.
- Unexpected schema drift detected.
- File is not empty.
- File month agrees with filename and expected delivery.
- Candidate key null/duplicate checks.
- Date and numeric parsing checks.
- Duplicate file detection.

## 4. dbt generic tests

Use where applicable:

- `not_null`
- `unique`
- `relationships`
- `accepted_values`

Apply tests to business keys and required columns based on confirmed rules. Do not require optional columns to be non-null.

## 5. Candidate custom tests

| Test | Dataset | Rule status |
|---|---|---|
| No negative call duration | Calls_Interactions | Proposed |
| No non-positive sample quantity | Samples | Proposed |
| Sample expiry not before sample date | Samples | Proposed |
| TRx equals NRx plus refills | Xponent | Observed; confirm definition |
| Market share calculation within tolerance | Xponent | Observed; confirm denominator/rounding |
| Fact foreign keys resolve | Facts | Initial profiling reported passing |
| No duplicate dimension business keys | Dimensions | Proposed |
| No fact row multiplication after dimension joins | Curated facts | Proposed |
| No duplicate file processing | Ingestion audit | Proposed |

## 6. Reconciliation controls

For every file and dataset, capture:

- Source row count.
- Rows loaded.
- Rows rejected.
- Rows inserted.
- Rows updated.
- Rows skipped as already processed.
- Final target count.
- Load execution identifier.

For measures, reconcile at a matching grain. Examples:

- Sum of source `qty_dropped` versus RAW and curated sample totals.
- Sum of source `trx_count` versus RAW and curated prescription totals.
- Source call count versus curated call count.

Do not compare aggregates at different grains or after joins that can multiply records.

## 7. Failure handling

- Critical ingestion failure: stop dependent transformations.
- Critical dbt test failure: do not declare the output publish-ready.
- Non-critical warning: record and assess; do not silently ignore.
- Preserve error details and execution identifiers.
- Rerun only after correcting the cause or documenting an approved exception.

## 8. Quality reporting

A future quality summary should include:

| Field | Meaning |
|---|---|
| run_id | Pipeline run identifier |
| model_name | Tested model |
| test_name | Test executed |
| status | Pass/fail/warn |
| failures | Failed row count |
| execution_time | Test execution timestamp |
| failure_sample | Optional diagnostic records/reference |

Do not invent a pass percentage without defining its denominator and whether tests or rows are being counted.
