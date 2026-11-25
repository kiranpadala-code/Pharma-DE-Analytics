# 02 – Source Inventory and Profiling

## 1. Source overview

The project uses nine synthetic CSV datasets.

| Dataset | Classification | File pattern / delivery | Initial loading concept |
|---|---|---|---|
| Calls_Interactions | Fact / event | Six monthly files | Append, with duplicate protection |
| Samples | Fact / event | Six monthly files | Append, with duplicate protection |
| Xponent | Fact / periodic measure | Six monthly files | Append or merge after revision behavior is confirmed |
| Product | Reference dimension | One static file | Initial load; reload strategy to be defined |
| Territory | Reference dimension | One static file | Initial load; reload strategy to be defined |
| Specialty_product_map | Reference mapping | One static file | Initial load; reload strategy to be defined |
| Account_master | Master dimension | Three files; full initial population and later incremental additions/changes as described by project owner | Merge/upsert; assess history requirements |
| HCP_master | Master dimension | Six files; full initial population with later additions | Merge/upsert; assess history requirements |
| Roster | Master dimension | Six files; full initial population with later additions | Merge/upsert; assess history requirements |

**Month coverage:** The project owner described the six monthly files as January–February 2026 in one specification, while the supplied file validation reported January–June 2026. The actual filenames and `load_month` values must be treated as authoritative and confirmed before pipeline implementation.

## 2. Initial file validation summary

The previously performed inspection of `output.zip` reported:

| Dataset | Files | Records reported |
|---|---:|---:|
| Calls_Interactions | 6 | 3,000 |
| Samples | 6 | 301 |
| Xponent | 6 | 2,400 |
| Product | 1 | 5 |
| Territory | 1 | 10 |
| Specialty_product_map | 1 | 10 |
| Account_master | 3 | 478 |
| HCP_master | 6 | 3,194 |
| Roster | 6 | 191 |
| **Total** | **36** | **9,589** |

These counts are a baseline from the initial inspection, not a substitute for recording actual ingestion counts in Snowflake.

## 3. Initial validation observations

The initial inspection reported:

- Expected CSV files were present.
- Monthly file schemas were consistent within each dataset.
- Manifest record counts matched inspected file counts.
- No missing or duplicate candidate primary keys were reported within individual files.
- No invalid date formats or numeric values were reported in the checks performed.
- Tested fact-to-dimension references resolved.
- Xponent `trx_count` matched `nrx_count + refill_count` in the inspected records.
- `market_share_pct` approximately matched `trx_count / market_trx * 100`.
- 701 blank `trx_change_vs_prior_month` values were reported, including baseline/new combinations.
- 41 sample rows without `call_id` were reported.
- 139 blank `parent_account_id` values were reported.

Re-run these checks as executable profiling and dbt tests. Do not rely solely on this prose summary.

## 4. File-level inventory to maintain

For every file, capture:

| Attribute | Description |
|---|---|
| dataset_name | Logical source dataset |
| file_name | Exact source filename |
| source_path | Local or S3 location |
| load_month | Month represented by the file |
| row_count | Number of data rows |
| column_count | Number of columns |
| file_size_bytes | File size |
| checksum | Optional file fingerprint for duplicate detection |
| received_at | When file was received |
| validation_status | Pass / fail |
| ingestion_status | Pending / loaded / failed |
| snowflake_query_id | Query identifier, where available |

## 5. Profiling still required

Before declaring the source data frozen, confirm:

- Exact month represented by every file.
- Candidate business keys and whether they are globally unique across all months.
- Whether Xponent records can be revised for previously loaded periods.
- Whether HCP, Account, and Roster files are cumulative snapshots or delta deliveries in every month.
- Whether `product_id`, `npi`, `rep_id`, and `account_id` are stable identifiers.
- Whether all blank values identified are valid business exceptions.
- Whether `products_discussed` contains one product or multiple products.

## 6. Source freeze policy

The generated data is the baseline source for this portfolio project. Do not regenerate or redesign it merely for cosmetic improvements. Change the generator or source files only when a reproducible defect is identified and documented.
