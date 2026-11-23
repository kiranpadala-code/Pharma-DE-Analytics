# Data Dictionary

**Project:** Pharma-DE-Analytics  
**Status:** Proposed  
**Source Data:** Synthetic/sample pharmaceutical datasets

## 1. Overview

This document describes the source datasets, their loading patterns, historical data handling, table structures, and relationships.

## 2. Source Dataset Inventory

### 2.1 Dimension Datasets

| Dataset | Data Type | Loading Pattern | Source Files |
|---|---|---|---|
| HCP_MASTER | Dimension | SCD Type 2 | 1 initial file + 6 monthly delta files |
| PRODUCT | Dimension | Static | 1 initial file |
| ROSTER | Dimension | SCD Type 2 | 1 initial file + 6 monthly delta files |
| ACCOUNT_MASTER | Dimension | SCD Type 1 | 1 initial file + 2 updates (month 3 and month 5) |

### 2.2 Fact Datasets

| Dataset | Data Type | Loading Pattern | Source Files |
|---|---|---|---|
| XPONENT | Fact | Incremental | 6 monthly files |
| CALLS_INTERACTIONS | Fact | Incremental | 6 monthly files |
| SAMPLES | Fact | Incremental | 6 monthly files |

## 3. Detailed Table Definitions

Column-level definitions, data types, primary keys, and foreign keys will be documented here.

# Data Dictionary: HCP Commercial Analytics

> Data types follow Snowflake conventions. Sample values are illustrative; replace them with real values from your data.

## Table of Contents
- [hcp_master](#hcp_master)
- [product](#product)
- [roster](#roster)
- [account_master](#account_master)
- [xponent](#xponent)
- [calls_interactions](#calls_interactions)
- [samples](#samples)

---

## 3.1 hcp_master

- **Type:** Dimension (SCD Type 2)
- **Description:** Master list of healthcare professionals (HCPs) with demographics, specialty, targeting attributes and account affiliation
- **Grain:** One row per HCP per version (per `load_month`)
- **Primary key:** `hcp_id` + `load_month`
- **Business key:** `npi`

| Column | Data Type | Description | Sample Values / Notes |
|--------|-----------|-------------|-----------------------|
| `hcp_id` | VARCHAR | Internal HCP identifier | `HCP000123` |
| `npi` | VARCHAR(10) | National Provider Identifier; join key to `xponent`, `calls_interactions`, `samples` | `1234567890`. Keep as string to preserve leading zeros |
| `first_name` | VARCHAR | HCP first name | `Anita` |
| `last_name` | VARCHAR | HCP last name | `Sharma` |
| `full_name` | VARCHAR | Concatenated full name | `Anita Sharma` |
| `degree` | VARCHAR | Professional degree | `MD`, `DO`, `NP`, `PA` |
| `specialty` | VARCHAR | Primary specialty | `Cardiology`, `Endocrinology` |
| `sub_specialty` | VARCHAR | Sub-specialty | `Interventional Cardiology`. Nullable |
| `gender` | VARCHAR | HCP gender | `M`, `F` |
| `address_line1` | VARCHAR | Practice street address | `123 Main St` |
| `city` | VARCHAR | Practice city | `Boston` |
| `state` | VARCHAR(2) | Practice state code | `MA` |
| `zip` | VARCHAR(10) | Postal code | `02118`. Keep as string |
| `account_id` | VARCHAR | FK to `account_master.account_id` | `ACC00456` |
| `tier` | VARCHAR | Targeting tier | `A`, `B`, `C` |
| `decile` | NUMBER(2) | Prescribing potential decile | 1 to 10 (10 = highest) |
| `target_segment` | VARCHAR | Commercial targeting segment | `High Value`, `Growth` |
| `is_kol` | BOOLEAN | Key opinion leader flag | `TRUE`/`FALSE` |
| `is_target` | BOOLEAN | Currently a target HCP | `TRUE`/`FALSE` |
| `is_active` | BOOLEAN | Active in practice | `TRUE`/`FALSE` |
| `years_in_practice` | NUMBER(3) | Years since start of practice | `15` |
| `data_source` | VARCHAR | Originating system or vendor | `Veeva`, `IQVIA` |
| `record_created_date` | DATE | Date the record version was created | `2025-01-15` |
| `load_month` | VARCHAR(7) | Monthly load or snapshot period | `2025-01` |

**Relationships**
- `hcp_master.account_id` → `account_master.account_id`
- `hcp_master.npi` ← `xponent.npi`, `calls_interactions.npi`, `samples.npi`

---

## 3.2 product

- **Type:** Dimension (Static)
- **Description:** Product catalog with brand, clinical and pricing attributes.
- **Grain:** One row per product.
- **Primary key:** `product_id`

| Column | Data Type | Description | Sample Values / Notes |
|--------|-----------|-------------|-----------------------|
| `product_id` | VARCHAR | Unique product identifier | `PRD001` |
| `product_code` | VARCHAR | Internal product code | `CARDIO-10MG` |
| `brand_name` | VARCHAR | Marketed brand name | `BrandX` |
| `generic_name` | VARCHAR | Generic (INN) name | `Atorvastatin` |
| `product_family` | VARCHAR | Product family or franchise | `Statins` |
| `therapeutic_area` | VARCHAR | Therapeutic area | `Cardiovascular` |
| `indication` | VARCHAR | Approved indication | `Hyperlipidemia` |
| `ndc` | VARCHAR(13) | National Drug Code | `00071-0155-23`. Keep as string |
| `formulation` | VARCHAR | Dosage form | `Tablet`, `Injection` |
| `strength` | VARCHAR | Product strength | `10 mg` |
| `route_of_administration` | VARCHAR | Route of administration | `Oral`, `Subcutaneous` |
| `dosing_frequency` | VARCHAR | Dosing schedule | `Once daily` |
| `manufacturer` | VARCHAR | Manufacturer name | `Pharma Co` |
| `launch_date` | DATE | Market launch date | `2018-06-01` |
| `is_active` | BOOLEAN | Currently marketed | `TRUE`/`FALSE` |
| `formulary_tier` | VARCHAR | Typical formulary tier | `Tier 2` |
| `avg_wholesale_price_usd` | NUMBER(12,2) | Average wholesale price in USD | `412.50` |

**Relationships**
- `product.product_id` ← `xponent.product_id`, `calls_interactions.product_id`, `samples.product_id`

---

## 3.3 roster

- **Type:** Dimension (SCD Type 2)
- **Description:** Field force roster with rep, territory and manager hierarchy.
- **Grain:** One row per rep per version (per `load_month`).
- **Primary key:** `rep_id` + `load_month`

| Column | Data Type | Description | Sample Values / Notes |
|--------|-----------|-------------|-----------------------|
| `rep_id` | VARCHAR | Unique rep identifier | `REP0042` |
| `rep_first_name` | VARCHAR | Rep first name | `Rahul` |
| `rep_last_name` | VARCHAR | Rep last name | `Mehta` |
| `rep_name` | VARCHAR | Full rep name | `Rahul Mehta` |
| `rep_email` | VARCHAR | Work email | `rahul.mehta@company.com`. PII |
| `role_title` | VARCHAR | Job title | `Sales Representative`, `KAM` |
| `channel` | VARCHAR | Engagement channel | `Field`, `Inside Sales`, `Digital` |
| `territory_id` | VARCHAR | Territory identifier | `T-NE-101` |
| `territory_name` | VARCHAR | Territory name | `Boston North` |
| `region` | VARCHAR | Sales region | `Northeast` |
| `zone` | VARCHAR | Sales zone | `Zone 1` |
| `manager_id` | VARCHAR | Manager's `rep_id` (self-reference) | `REP0010` |
| `manager_name` | VARCHAR | Manager name | `Priya Nair` |
| `product_focus` | VARCHAR | Primary product(s) promoted | `BrandX` |
| `hire_date` | DATE | Hire date | `2021-03-15` |
| `employee_status` | VARCHAR | Employment status | `Active`, `Vacant`, `Leave` |
| `target_hcp_count` | NUMBER(5) | Number of HCPs targeted by this rep | `120` |
| `load_month` | VARCHAR(7) | Monthly load or snapshot period | `2025-01` |

**Relationships**
- `roster.manager_id` → `roster.rep_id`
- `roster.rep_id` ← `calls_interactions.rep_id`, `samples.rep_id`

---

## 3.4 account_master

- **Type:** Dimension (SCD Type 1, overwrite)
- **Description:** Healthcare organizations (hospitals, clinics, IDNs) with segmentation and formulary attributes.
- **Grain:** One row per account.
- **Primary key:** `account_id`

| Column | Data Type | Description | Sample Values / Notes |
|--------|-----------|-------------|-----------------------|
| `account_id` | VARCHAR | Unique account identifier | `ACC00456` |
| `account_name` | VARCHAR | Organization name | `Mass General Hospital` |
| `account_type` | VARCHAR | Type of organization | `Hospital`, `Clinic`, `IDN` |
| `account_segment` | VARCHAR | Commercial segment | `Key Account`, `Standard` |
| `hco_npi` | VARCHAR(10) | Organizational NPI | `1098765432` |
| `parent_account_id` | VARCHAR | Parent account (self-reference) | `ACC00100`. Nullable |
| `address_line1` | VARCHAR | Street address | `55 Fruit St` |
| `city` | VARCHAR | City | `Boston` |
| `state` | VARCHAR(2) | State code | `MA` |
| `zip` | VARCHAR(10) | Postal code | `02114` |
| `region` | VARCHAR | Sales region | `Northeast` |
| `bed_count` | NUMBER(6) | Number of beds | `1000`. Null for non-hospitals |
| `is_teaching_hospital` | BOOLEAN | Teaching hospital flag | `TRUE`/`FALSE` |
| `is_magnet_hospital` | BOOLEAN | Magnet-recognized hospital flag | `TRUE`/`FALSE` |
| `formulary_access` | VARCHAR | Formulary access status | `Open`, `Restricted`, `Closed` |
| `is_active` | BOOLEAN | Active account | `TRUE`/`FALSE` |
| `record_created_date` | DATE | Record creation date | `2020-05-10` |
| `record_updated_date` | DATE | Last update date | `2025-01-20` |
| `load_month` | VARCHAR(7) | Monthly load period | `2025-01` |

**Relationships**
- `account_master.parent_account_id` → `account_master.account_id`
- `account_master.account_id` ← `hcp_master.account_id`

---

## 3.5 xponent

- **Type:** Fact (Incremental, 6 monthly files)
- **Description:** Prescription (Rx) activity at HCP-product level, including TRx/NRx volumes, market share and payer context.
- **Grain:** One row per `rx_id` (confirm: typically HCP x product x period).
- **Primary key:** `rx_id`

| Column | Data Type | Description | Sample Values / Notes |
|--------|-----------|-------------|-----------------------|
| `rx_id` | VARCHAR | Unique Rx record identifier | `RX0000001` |
| `npi` | VARCHAR(10) | Prescriber NPI, FK to `hcp_master.npi` | `1234567890` |
| `product_id` | VARCHAR | FK to `product.product_id` | `PRD001` |
| `period` | DATE | Prescription period | `2025-01-01` |
| `load_month` | VARCHAR(7) | Month the file was loaded | `2025-01` |
| `trx_count` | NUMBER(10) | Total prescriptions (new plus refill) | `25` |
| `nrx_count` | NUMBER(10) | New prescriptions | `8` |
| `refill_count` | NUMBER(10) | Refill prescriptions | `17` |
| `trx_change_vs_prior_month` | NUMBER(10,2) | TRx change vs prior month | `+3`, `-2`. Check whether absolute or %, and null for the first month |
| `market_trx` | NUMBER(10) | Total TRx in the competitive market | `120` |
| `market_share_pct` | NUMBER(5,2) | `trx_count / market_trx * 100` | `20.83` |
| `state` | VARCHAR(2) | Prescriber state | `MA` |
| `specialty` | VARCHAR | Prescriber specialty | `Cardiology` |
| `channel` | VARCHAR | Dispensing channel | `Retail`, `Mail Order`, `Specialty` |
| `days_supply_avg` | NUMBER(5,1) | Average days supply per Rx | `30.0` |
| `payer_type` | VARCHAR | Payer category | `Commercial`, `Medicare`, `Medicaid` |
| `formulary_status_at_time` | VARCHAR | Formulary status when Rx was written | `Preferred`, `Non-Preferred` |
| `data_source` | VARCHAR | Source vendor | `IQVIA Xponent` |

**Relationships**
- `xponent.npi` → `hcp_master.npi`
- `xponent.product_id` → `product.product_id`

---

## 3.6 calls_interactions

- **Type:** Fact (Incremental, 6 monthly files)
- **Description:** Rep-to-HCP interactions (calls, visits, virtual engagements) with outcomes, messaging and compliance flags.
- **Grain:** One row per call.
- **Primary key:** `call_id`

| Column | Data Type | Description | Sample Values / Notes |
|--------|-----------|-------------|-----------------------|
| `call_id` | VARCHAR | Unique call identifier | `CALL000001` |
| `rep_id` | VARCHAR | FK to `roster.rep_id` | `REP0042` |
| `npi` | VARCHAR(10) | FK to `hcp_master.npi` | `1234567890` |
| `product_id` | VARCHAR | FK to `product.product_id` (primary product) | `PRD001` |
| `call_date` | DATE | Date of the call | `2025-01-14` |
| `load_month` | VARCHAR(7) | Month the file was loaded | `2025-01` |
| `call_type` | VARCHAR | Type of call | `Detail`, `Follow-up`, `Lunch & Learn` |
| `call_channel` | VARCHAR | Interaction channel | `In-person`, `Phone`, `Video`, `Email` |
| `call_outcome` | VARCHAR | Outcome of the call | `Completed`, `Not Available`, `Declined` |
| `products_discussed` | VARCHAR | Products discussed | `BrandX; BrandY`. Delimited list, so consider splitting |
| `primary_message` | VARCHAR | Key message delivered | `Efficacy`, `Safety` |
| `was_sampled` | BOOLEAN | Samples dropped during call | `TRUE`/`FALSE` |
| `was_detailed` | BOOLEAN | Product detailed during call | `TRUE`/`FALSE` |
| `call_duration_min` | NUMBER(5,1) | Call duration in minutes | `12.5` |
| `call_rank_in_month` | NUMBER(3) | Sequence of the call within the month (per rep or HCP, confirm) | `3` |
| `territory_id` | VARCHAR | Territory at time of call | `T-NE-101` |
| `next_call_planned_date` | DATE | Planned follow-up date | `2025-02-10`. Nullable |
| `is_compliant_call` | BOOLEAN | Passed compliance checks | `TRUE`/`FALSE` |
| `call_notes` | VARCHAR | Free-text notes | Sensitive, so review before exposing |
| `data_source` | VARCHAR | Source system | `Veeva CRM` |

**Relationships**
- `calls_interactions.rep_id` → `roster.rep_id`
- `calls_interactions.npi` → `hcp_master.npi`
- `calls_interactions.product_id` → `product.product_id`
- `calls_interactions.call_id` ← `samples.call_id`

---

## 3.7 samples

- **Type:** Fact (Incremental, 6 monthly files)
- **Description:** Product sample drops to HCPs, with lot tracking and signature capture for compliance.
- **Grain:** One row per sample drop.
- **Primary key:** `sample_id`

| Column | Data Type | Description | Sample Values / Notes |
|--------|-----------|-------------|-----------------------|
| `sample_id` | VARCHAR | Unique sample record identifier | `SMP000001` |
| `rep_id` | VARCHAR | FK to `roster.rep_id` | `REP0042` |
| `npi` | VARCHAR(10) | FK to `hcp_master.npi` | `1234567890` |
| `product_id` | VARCHAR | FK to `product.product_id` | `PRD001` |
| `call_id` | VARCHAR | FK to `calls_interactions.call_id` | `CALL000001`. Nullable if the drop is not tied to a call |
| `sample_date` | DATE | Date of sample drop | `2025-01-14` |
| `load_month` | VARCHAR(7) | Month the file was loaded | `2025-01` |
| `qty_dropped` | NUMBER(6) | Units dropped | `4` |
| `sample_unit_type` | VARCHAR | Unit type | `Box`, `Pack`, `Pen` |
| `lot_number` | VARCHAR | Manufacturing lot number | `LOT2024A123` |
| `expiry_date` | DATE | Lot expiry date | `2026-03-31` |
| `strength_sampled` | VARCHAR | Strength sampled | `10 mg` |
| `sample_request_type` | VARCHAR | How the sample was requested | `Rep Initiated`, `HCP Requested` |
| `was_signature_captured` | BOOLEAN | Signature obtained | `TRUE`/`FALSE` |
| `signature_method` | VARCHAR | How signature was captured | `Electronic`, `Paper` |
| `territory_id` | VARCHAR | Territory at time of drop | `T-NE-101` |
| `sample_program` | VARCHAR | Sample program name | `Standard`, `Starter Pack` |
| `data_source` | VARCHAR | Source system | `Veeva CRM` |

**Relationships**
- `samples.rep_id` → `roster.rep_id`
- `samples.npi` → `hcp_master.npi`
- `samples.product_id` → `product.product_id`
- `samples.call_id` → `calls_interactions.call_id`

---


## Entity Relationship Summary

### Entity Relationship Diagram

```text
account_master ──< hcp_master ──< xponent >── product
                       │              │
                       ├──< calls_interactions >── product
                       │              │
roster ────────────────┴──────────────┴──< samples >── product
```

### Table Relationships

| Table | Related Table | Relationship Description |
|---|---|---|
| `hcp_master` | `account_master` | Identifies the account or hospital with which the HCP is affiliated. |
| `xponent` | `hcp_master` | Identifies the HCP who prescribed the drug. |
| `xponent` | `product` | Identifies the prescribed drug. |
| `calls_interactions` | `hcp_master` | Identifies the HCP contacted during the interaction. |
| `calls_interactions` | `product` | Identifies the product discussed during the interaction. |
| `calls_interactions` | `roster` | Identifies the sales representative who made the call and their assigned territory. |
| `samples` | `hcp_master` | Identifies the HCP who received the samples. |
| `samples` | `product` | Identifies the product samples distributed. |
| `samples` | `roster` | Identifies the sales representative who distributed the samples. |




## 4. Data Loading and Historical Handling

| Dataset | Expected Processing Behaviour |
|---|---|
| HCP_MASTER | Maintain historical versions of HCP records using SCD Type 2 |
| PRODUCT | Load static reference data |
| ROSTER | Maintain historical versions using SCD Type 2 |
| ACCOUNT_MASTER | Overwrite existing records using SCD Type 1 |
| XPONENT | Append/process monthly incremental records |
| CALLS_INTERACTIONS | Append/process monthly incremental records |
| SAMPLES | Append/process monthly incremental records |


## 5. Assumptions and Notes

- Source files are expected to arrive monthly where applicable.
- SCD Type 2 preserves historical changes.
- SCD Type 1 overwrites previous values.
- Incremental fact datasets require appropriate duplicate handling and incremental processing logic.
- Actual column definitions and key constraints are pending validation.
