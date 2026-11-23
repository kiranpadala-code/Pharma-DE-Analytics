# Pharma-DE-Analytics

## Overview

Pharma-DE-Analytics is an end-to-end pharmaceutical data engineering project focused on building data transformation pipelines using dbt Core and Snowflake.

The project aims to transform raw pharmaceutical business datasets into clean, structured, reliable and analytics-ready data models to support business analysis and reporting.

## Objectives

- Build end-to-end data transformation pipelines using dbt.
- Integrate and transform multiple pharmaceutical datasets.
- Implement data cleaning, standardization and validation.
- Develop staging, intermediate and mart data models.
- Implement data quality tests and validation rules.
- Apply dimensional modelling concepts.
- Explore incremental models and historical data tracking.
- Produce analytics-ready datasets for business insights.

## Technology Stack

| Technology | Purpose |
|---|---|
| Snowflake | Cloud data warehouse |
| dbt Core | Data transformation and modelling |
| SQL | Data transformation logic |
| Git | Version control |
| GitHub | Source code management |
| VS Code | Development environment |

## Project Architecture

The project will follow a layered data transformation architecture:

1. **Raw Layer:** Source datasets loaded into Snowflake.
2. **Staging Layer:** Data cleaning, standardization and initial transformations.
3. **Intermediate Layer:** Business logic, joins and calculations.
4. **Marts Layer:** Fact and dimension models designed for analytical consumption.

## Business Areas

The project will explore pharmaceutical business domains such as:

- Pharmaceutical sales and revenue analysis
- Product and drug master data
- Healthcare Professional (HCP) analytics
- Healthcare Organization (HCO) analytics
- Prescription trends
- Territory and geographical performance

## Data Quality

Data quality will be addressed through:

- Uniqueness and null validation
- Referential integrity checks
- Accepted value validation
- Business rule validations
- Custom SQL tests

## Project Status

**Status:** Initial Planning and Development

Dataset identification, source analysis and pipeline design are the initial focus areas.

## Repository Structure

The repository structure and documentation will evolve as the project develops.

## Disclaimer

This is an independent learning and portfolio project using sample or publicly available datasets. It is not affiliated with or representative of any pharmaceutical company.
