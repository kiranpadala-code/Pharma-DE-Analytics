# 15 – Pipeline Runbook (Template)

> Complete this document as pipeline components are implemented. Do not treat placeholder commands as executable until confirmed in the project environment.

## 1. Environment

| Item | Value |
|---|---|
| Repository | Pharma-DE-Analytics |
| dbt project | pharma_analytics |
| Snowflake database | PHARMA_DB |
| Snowflake warehouse | PHARMA_WH (confirm current object) |
| AWS bucket | To be recorded |
| dbt target | To be recorded |
| Runtime / Python version | To be recorded |

Do not record passwords, tokens, private keys, or secret values here.

## 2. Pre-run checks

- [ ] Correct Git branch and latest code pulled.
- [ ] Credentials available through secure local configuration.
- [ ] Expected source files present.
- [ ] File validation passed.
- [ ] S3 access verified.
- [ ] Snowflake warehouse available.
- [ ] No previous run is still processing the same files.

## 3. Execution sequence

| Step | Operation | Command / method | Status |
|---|---|---|---|
| 1 | Validate source files | To be added | Pending |
| 2 | Upload files to S3 | To be added | Pending |
| 3 | Load Snowflake RAW | To be added | Pending |
| 4 | Validate RAW counts | To be added | Pending |
| 5 | Build dbt models | `dbt build` or targeted selection | Pending |
| 6 | Review test results | dbt output / artifacts | Pending |
| 7 | Reconcile source and target | To be added | Pending |
| 8 | Record run status | To be added | Pending |

## 4. Failure handling

For every failure, record:
- Run ID.
- Date/time.
- Failed task/model.
- Error message.
- Source file or model involved.
- Root cause.
- Corrective action.
- Rerun outcome.

## 5. Post-run checks

- [ ] All expected files accounted for.
- [ ] No unintended duplicate records.
- [ ] RAW row counts reconciled.
- [ ] dbt build completed.
- [ ] Required tests passed.
- [ ] Analytical outputs refreshed.
- [ ] Execution status documented.

## 6. Run history

| Run ID | Date/time | Source month | Status | Notes |
|---|---|---|---|---|
| | | | | |
