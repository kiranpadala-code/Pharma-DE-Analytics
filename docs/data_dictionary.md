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

### 3.1 HCP_MASTER
To be documented.

### 3.2 PRODUCT
To be documented.

### 3.3 ROSTER
To be documented.

### 3.4 ACCOUNT_MASTER
To be documented.

### 3.5 XPONENT
To be documented.

### 3.6 CALLS_INTERACTIONS
To be documented.

### 3.7 SAMPLES
To be documented.

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

## 5. Table Relationships

To be documented after identifying primary keys and foreign keys.

## 6. Assumptions and Notes

- Source files are expected to arrive monthly where applicable.
- SCD Type 2 preserves historical changes.
- SCD Type 1 overwrites previous values.
- Incremental fact datasets require appropriate duplicate handling and incremental processing logic.
- Actual column definitions and key constraints are pending validation.
