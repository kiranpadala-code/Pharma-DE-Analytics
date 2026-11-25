# 03 – Source Data Dictionary

This document records the supplied source columns. Descriptions are working interpretations based on column names and the project context; confirm ambiguous meanings with the generator or business rules before implementing transformations.

## 1. Calls_Interactions

**Classification:** Fact / event  
**Expected grain:** One row per `call_id` (candidate; validate uniqueness across all files).

| Column | Working description |
|---|---|
| call_id | Unique identifier for a call interaction |
| rep_id | Sales representative identifier |
| npi | HCP National Provider Identifier |
| product_id | Product associated with the call |
| call_date | Date of the call |
| load_month | Source delivery month |
| call_type | Type/category of call |
| call_channel | Channel used for the interaction |
| call_outcome | Outcome of the interaction |
| products_discussed | Product(s) discussed during the call |
| primary_message | Main product or business message |
| was_sampled | Indicates whether samples were associated with the call |
| was_detailed | Indicates whether a product was detailed |
| call_duration_min | Call duration in minutes |
| call_rank_in_month | Call sequence/rank within a month; exact definition to confirm |
| territory_id | Territory associated with the call |
| next_call_planned_date | Planned follow-up date |
| is_compliant_call | Source compliance indicator |
| call_notes | Free-text notes |
| data_source | Originating source/system label |

## 2. Samples

**Classification:** Fact / event  
**Expected grain:** One row per `sample_id` (candidate; validate uniqueness across all files).

| Column | Working description |
|---|---|
| sample_id | Unique sample-distribution record identifier |
| rep_id | Representative distributing the sample |
| npi | HCP receiving the sample |
| product_id | Sampled product |
| call_id | Related call identifier, if applicable |
| sample_date | Date of sample distribution |
| load_month | Source delivery month |
| qty_dropped | Quantity distributed |
| sample_unit_type | Unit of measure |
| lot_number | Product lot/batch identifier |
| expiry_date | Sample lot expiry date |
| strength_sampled | Strength of sampled product |
| sample_request_type | Type of sample request |
| was_signature_captured | Indicates whether a signature was captured |
| signature_method | Method used to capture signature |
| territory_id | Territory associated with distribution |
| sample_program | Sample program identifier/name |
| data_source | Originating source/system label |

## 3. Xponent

**Classification:** Periodic fact / market measure  
**Expected grain:** Candidate grain is one row per NPI + product + reporting period. Confirm whether `rx_id` is unique and whether multiple channels or payer categories create additional grain.

| Column | Working description |
|---|---|
| rx_id | Prescription record identifier; uniqueness to validate |
| npi | HCP identifier |
| product_id | Product identifier |
| period | Prescription reporting period |
| load_month | Source delivery month |
| trx_count | Total prescriptions |
| nrx_count | New prescriptions |
| refill_count | Refill prescriptions |
| trx_change_vs_prior_month | Change in TRx versus prior month; exact unit/definition to confirm |
| market_trx | Market total prescriptions for the relevant comparison group |
| market_share_pct | Product market share percentage |
| state | State associated with the record |
| specialty | HCP specialty |
| channel | Prescription channel |
| days_supply_avg | Average days supply |
| payer_type | Payer category |
| formulary_status_at_time | Formulary status at the reporting time |
| data_source | Originating source/system label |

## 4. Product

**Classification:** Reference dimension  
**Expected grain:** One row per `product_id`.

| Column | Working description |
|---|---|
| product_id | Product business identifier |
| product_code | Short product code |
| brand_name | Brand name |
| generic_name | Generic ingredient/name |
| product_family | Product family |
| therapeutic_area | Therapeutic area |
| indication | Approved/represented indication |
| form | Dosage form |
| route | Route of administration |
| strength | Product strength |
| dosing_frequency | Dosing frequency |
| manufacturer | Manufacturer |
| approval_date | Approval date |
| is_active | Active product indicator |
| is_sampleable | Indicates sample eligibility |
| formulary_tier | Formulary tier |
| price | Price field; currency, basis and effective date to confirm |

## 5. Territory

**Classification:** Reference dimension  
**Expected grain:** One row per `territory_id`.

| Column | Working description |
|---|---|
| territory_id | Territory identifier |
| territory_name | Territory name |
| region | Region |
| zone | Zone |
| states_covered | State or states covered; confirm whether this is a delimited multi-value field |

## 6. Specialty_product_map

**Classification:** Reference mapping  
**Expected grain:** One row per specialty + primary_product_id, subject to uniqueness validation.

| Column | Working description |
|---|---|
| specialty | Medical specialty |
| primary_product_id | Product mapped as primary for the specialty |

## 7. Account_master

**Classification:** Master dimension  
**Expected grain:** One current account per `account_id`; source files may contain repeated snapshots/updates.

| Column | Working description |
|---|---|
| account_id | Account identifier |
| account_name | Account name |
| account_type | Account type |
| account_segment | Commercial segment |
| hco_npi | Healthcare organization NPI, where applicable |
| parent_account_id | Parent account identifier for hierarchy |
| address_line1 | Street address |
| city | City |
| state | State |
| zip | Postal code |
| region | Region |
| bed_count | Hospital bed count |
| is_teaching_hospital | Teaching hospital indicator |
| is_magnet_hospital | Magnet hospital indicator |
| formulary_access | Formulary access indicator/status |
| is_active | Active account indicator |
| record_created_date | Source record creation date |
| record_updated_date | Source record update date |
| load_month | Source delivery month |

## 8. HCP_master

**Classification:** Master dimension  
**Expected grain:** One HCP per stable HCP identifier; confirm `hcp_id` and `npi` uniqueness rules.

| Column | Working description |
|---|---|
| hcp_id | Internal HCP identifier |
| npi | HCP NPI |
| first_name | First name |
| last_name | Last name |
| full_name | Full name |
| degree | Professional degree |
| specialty | Medical specialty |
| sub_specialty | Medical subspecialty |
| gender | Source gender attribute |
| address_line1 | Street address |
| city | City |
| state | State |
| zip | Postal code |
| account_id | Associated account identifier |
| territory_id | Assigned territory |
| tier | HCP tier |
| decile | HCP decile |
| target_segment | Target segment |
| is_kol | Key opinion leader indicator |
| is_target | Target HCP indicator |
| is_active | Active HCP indicator |
| years_in_practice | Years in practice |
| data_source | Originating source/system label |
| record_created_date | Source record creation date |
| load_month | Source delivery month |

## 9. Roster

**Classification:** Master dimension  
**Expected grain:** One representative per `rep_id` in a current-state view; source history/update behavior to confirm.

| Column | Working description |
|---|---|
| rep_id | Representative identifier |
| rep_first_name | First name |
| rep_last_name | Last name |
| rep_name | Full name |
| rep_email | Work email |
| role_title | Job title |
| channel | Commercial channel |
| territory_id | Assigned territory |
| territory_name | Territory name |
| region | Region |
| zone | Zone |
| manager_id | Manager identifier |
| manager_name | Manager name |
| product_focus | Product focus |
| hire_date | Hire date |
| employee_status | Employment status |
| target_hcp_count | Target HCP count |
| load_month | Source delivery month |

## 10. Technical metadata (planned additions)

The following are proposed warehouse ingestion metadata fields, not source CSV columns:

- `_SOURCE_FILE`
- `_LOADED_AT`
- `_LOAD_ID`

Add them in RAW or the ingestion process without changing the meaning of source business columns.
