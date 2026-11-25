# 04 – Business Rules, Assumptions and Constraints

## 1. Purpose

This document defines the business meaning and constraints that transformations and tests must preserve. A rule must not be implemented as a hard validation until its definition is confirmed.

**Status labels**
- **Confirmed from project specification:** explicitly stated by the project owner.
- **Observed in initial profiling:** reported by the initial file inspection; revalidate with executable checks.
- **Proposed:** recommended design, not yet approved as a source truth.
- **To confirm:** ambiguous or missing definition.

## 2. General rules

| ID | Rule | Status |
|---|---|---|
| BR-001 | All supplied records are synthetic and generated for portfolio/learning use. | Confirmed |
| BR-002 | The source delivery format is CSV. | Confirmed |
| BR-003 | Preserve source business values in RAW; standardize in dbt staging. | Proposed |
| BR-004 | Every source file must be traceable to its filename and ingestion run. | Proposed |
| BR-005 | Reprocessing the same file must not create duplicate target records. | Proposed |
| BR-006 | Null values must be evaluated according to field meaning; do not replace all nulls with defaults. | Proposed |

## 3. Fact-table rules

### Calls_Interactions

| ID | Rule | Status |
|---|---|---|
| CALL-001 | Candidate grain is one row per `call_id`. | To confirm across all files |
| CALL-002 | `rep_id`, `npi`, `product_id`, and `territory_id` should resolve to their corresponding master/reference entities where the business event requires them. | Proposed; initial relationships reported as passing |
| CALL-003 | `call_duration_min` must not be negative. | Proposed |
| CALL-004 | `next_call_planned_date` may be null when no follow-up is planned. | To confirm |
| CALL-005 | `products_discussed` may represent multiple products; determine its encoding before modeling. | To confirm |
| CALL-006 | `call_rank_in_month` must be defined before it is used as a performance measure. | To confirm |

### Samples

| ID | Rule | Status |
|---|---|---|
| SMP-001 | Candidate grain is one row per `sample_id`. | To confirm across all files |
| SMP-002 | `qty_dropped` should be positive for a completed distribution. | Proposed |
| SMP-003 | `expiry_date` should not be earlier than `sample_date`. | Proposed |
| SMP-004 | `call_id` can be nullable if sample distribution can occur outside a recorded call. | To confirm; 41 null call IDs were reported in initial profiling |
| SMP-005 | When `call_id` is populated, it should resolve to a call record if the source relationship is intended. | Proposed |
| SMP-006 | A call with `was_sampled = true` should have a related sample record only if this is guaranteed by source business logic. | To confirm; initial profiling reported matching records for sampled calls |

### Xponent

| ID | Rule | Status |
|---|---|---|
| XP-001 | Candidate grain is NPI + product + reporting period; channel/payer may require additional grain dimensions. | To confirm |
| XP-002 | `trx_count`, `nrx_count`, and `refill_count` should be non-negative. | Proposed |
| XP-003 | `trx_count = nrx_count + refill_count` if the supplied source definition follows this decomposition. | Observed in initial profiling; confirm generator definition |
| XP-004 | `market_trx` must be positive when market share is calculated. | Proposed |
| XP-005 | `market_share_pct` should be consistent with the documented numerator and denominator. | Observed in initial profiling; confirm calculation and rounding |
| XP-006 | `trx_change_vs_prior_month` may be null when no prior-period comparison exists. | Observed in initial profiling |
| XP-007 | Confirm whether historical reporting periods can be restated in later files. | To confirm |

## 4. Dimension and reference rules

| ID | Dataset | Rule | Status |
|---|---|---|---|
| DIM-001 | Product | `product_id` should identify one product. | Proposed |
| DIM-002 | Territory | `territory_id` should identify one territory. | Proposed |
| DIM-003 | Specialty_product_map | Specialty-to-product mapping should be unique at its declared grain. | Proposed |
| DIM-004 | HCP_master | Determine whether `npi` is globally unique and stable for the project. | To confirm |
| DIM-005 | Account_master | `account_id` identifies an account; `parent_account_id` may be null for top-level accounts. | Proposed |
| DIM-006 | Roster | `rep_id` identifies a representative; employee status may change over time. | Proposed |
| DIM-007 | HCP_master | HCP account and territory assignments may change; decide whether history is required. | To confirm |
| DIM-008 | Account_master | Account attributes may change; decide whether current state or historical state is required. | To confirm |

## 5. Monthly delivery and incremental rules

| ID | Rule | Status |
|---|---|---|
| INC-001 | Calls and Samples are expected to be event-like monthly deliveries and are candidates for append loading with deduplication. | Proposed |
| INC-002 | Xponent is a periodic measure and should be append-loaded only if periods are immutable; otherwise use a merge/revision strategy. | To confirm |
| INC-003 | Account, HCP, and Roster files must be profiled to determine whether each delivery is a full snapshot or delta. | To confirm |
| INC-004 | Initial dimension loads must establish the baseline before later updates are applied. | Proposed |
| INC-005 | File identity/checksum or a stable business key must be used to prevent accidental duplicate processing. | Proposed |
| INC-006 | A rerun must be safe and produce the same final state. | Proposed |

## 6. Join and aggregation rules

- Do not join detailed fact tables directly to one another when this can multiply rows.
- Join facts to dimensions using validated keys and appropriate effective-date logic where historical dimensions are implemented.
- Aggregate each fact to a compatible grain before combining measures from different facts.
- Do not assume prescription activity is caused by representative calls or sample distribution.
- Do not attribute territory-level prescriptions to an individual representative without a defensible attribution rule.
- Do not average percentages without confirming the appropriate denominator and weighting.
- Do not sum a repeated market-level denominator across product/HCP rows.

## 7. Open business decisions

Resolve these before finalizing relevant models:

1. What exactly is the grain of Xponent, and is `rx_id` unique?
2. Does `products_discussed` contain one product or multiple products?
3. What is the unit and calculation of `trx_change_vs_prior_month`?
4. Is `market_trx` repeated across multiple HCPs/products?
5. What currency and pricing basis does `Product.price` use?
6. Are Account/HCP/Roster files snapshots or deltas for each delivery?
7. Which attributes need historical tracking (SCD Type 2)?
8. Can sample records exist without a call?
9. Are call compliance rules defined by source fields or external policy?
10. What is the business definition of `call_rank_in_month`?

Update this file when decisions are confirmed. Record significant design decisions in `13_decision_log.md`.
