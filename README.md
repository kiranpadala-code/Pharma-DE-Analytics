# Pharma-DE-Analytics

## Overview

Pharma-DE-Analytics is an end-to-end pharmaceutical data engineering project focused on building scalable, reliable and analytics-ready data pipelines using AWS S3, Snowflake and dbt Fusion.

The project simulates pharmaceutical commercial data operations, covering data generation, cloud storage, ingestion, reconciliation, transformation, data quality and dimensional modelling.

## Objectives

- Implement end-to-end ELT pipelines.
- Integrate multiple pharmaceutical commercial datasets.
- Implement data ingestion and reconciliation.
- Perform data cleaning, standardization and validation.
- Develop staging, intermediate and mart data models.
- Implement automated data quality checks and business rule validations.
- Apply dimensional modelling concepts.
- Explore incremental processing and historical data management.
- Deliver analytics-ready datasets for business reporting.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Synthetic data generation and validation |
| AWS S3 | Cloud object storage and source file management |
| Snowflake | Cloud data warehouse and transformation compute |
| dbt Fusion | Data transformation, modelling and testing |
| SQL | Data processing and business logic |
| YAML | Configuration, documentation and test definitions |
| Git | Version control |
| GitHub | Source code management |
| VS Code | Development environment |

## Project Architecture

```text
Synthetic Data Generation (Python)
                |
                v
             AWS S3
                |
                v
        Snowflake RAW Layer
                |
                v
        dbt Staging Layer
                |
                v
      dbt Intermediate Layer
                |
                v
         dbt Marts Layer
                |
                v
       Analytics and Reporting
```

| Layer | Responsibility |
|---|---|
| RAW | Source data ingestion and preservation |
| STAGING | Data cleaning, standardization and type casting |
| INT | Dataset integration, business logic and calculations |
| MARTS | Analytical fact and dimension models |

## Source Datasets

The project uses synthetic pharmaceutical commercial data covering January to June 2026.

| Dataset | Description |
|---|---|
| product | Pharmaceutical product master |
| territory | Sales territory and geographical hierarchy |
| specialty_product_map | HCP specialty and product mapping |
| account_master | Healthcare organization master |
| hcp_master | Healthcare professional master |
| roster | Sales representative and territory assignments |
| xponent | Prescription and pharmaceutical sales data |
| calls_interactions | Sales representative and HCP interactions |
| samples | Pharmaceutical sample distribution |

## Business Domains

- Pharmaceutical sales and prescription analytics
- Product performance
- Healthcare Professional (HCP) analytics
- Healthcare Organization (HCO) analytics
- Sales representative effectiveness
- Territory and geographical performance
- HCP engagement and sample distribution

## Data Quality Framework

Data quality controls will be implemented across the pipeline using:

- Source-to-target reconciliation
- Primary key uniqueness checks
- Mandatory field validation
- Referential integrity checks
- Accepted value validation
- Cross-dataset consistency checks
- Business rule validations
- Custom SQL-based dbt tests

Selected source data violations are intentionally retained to demonstrate data quality detection and exception handling.

## Project Progress

| Phase | Status |
|---|---|
| Project planning and dataset design | Completed |
| Synthetic data generation | Completed |
| AWS S3 setup and initial file ingestion | Completed |
| Snowflake RAW layer initial ingestion | Completed |
| Initial data reconciliation and validation | Completed |
| GitHub repository setup | Completed |
| dbt connectivity and configuration | Completed |
| Source definitions | Completed (9/9) |
| Staging models | In Progress (5/9) |
| Data quality test implementation | In Progress |
| Intermediate models | Pending |
| Dimensional modelling and marts | Pending |
| Incremental processing and historical tracking | Pending |
| Pipeline orchestration | Pending |
| CI/CD automation | Pending |
| Final documentation | Pending |

### Staging Model Implementation and DQ Coverage

| Model | Generic Tests | Singular Tests | Status |
|---|---:|---:|---|
| Product | 8 | 1 | Completed |
| Territory | 8 | 1 | Completed |
| Specialty Product Map | 6 | 0 | Completed |
| Account Master | 24 | 8 | Completed |
| HCP Master | 35 | 11 | Completed |
| Roster | — | — | Pending |
| Xponent | — | — | Pending |
| Calls Interactions | — | — | Pending |
| Samples | — | — | Pending |
| **Total** | **81** | **21** | **102 tests passed** |

All implemented tests have passed against the initial static
and January 2026 datasets.

Subsequent monthly deliveries from February to June 2026
will be used to validate incremental ingestion, historical
data management and multi-period data quality controls.

## Version Control

Project source code, SQL models, configuration files and documentation are maintained using Git and GitHub.

Generated datasets and sensitive connection credentials are excluded from version control.

## Disclaimer

This is an independent learning and portfolio project using synthetic pharmaceutical datasets. It does not contain real patient, healthcare professional or proprietary pharmaceutical company data and is not affiliated with any pharmaceutical organization.