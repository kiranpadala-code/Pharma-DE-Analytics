# 00 – Project Charter

## 1. Project name

**Pharma-DE-Analytics**

Pharmaceutical Commercial Analytics Data Platform

## 2. Business context

A pharmaceutical company receives commercial data from multiple operational and market-data sources. The data covers field interactions, sample distribution, prescription performance, healthcare professionals (HCPs), healthcare organizations/accounts, products, territories, and sales representatives.

The project simulates the integration of these datasets into a cloud data warehouse so that consistent, documented, analytics-ready outputs can be produced.

## 3. Problem statement

The source datasets are separate CSV files with different grains, update patterns, and business keys. Without a governed ingestion and transformation process, it is difficult to:

- combine the datasets consistently;
- preserve monthly history;
- prevent duplicate loads;
- identify invalid or unmatched records;
- calculate commercial measures consistently; and
- provide reusable data for reporting and analysis.

## 4. Project goal

Build a reproducible end-to-end data engineering workflow that moves synthetic pharmaceutical commercial data from CSV files through AWS S3 and Snowflake, transforms it with dbt, applies automated data-quality checks, and publishes analytical datasets.

## 5. Intended users

- Data engineers responsible for ingestion and transformation.
- Analytics engineers responsible for dimensional models and marts.
- Commercial analysts consuming curated outputs.
- Hiring managers or technical reviewers evaluating the portfolio project.

## 6. Core deliverables

1. Organized source-data landing area in AWS S3.
2. Snowflake RAW tables with ingestion metadata.
3. dbt staging models for source standardization.
4. Intermediate models for reusable joins and business logic.
5. Fact and dimension models.
6. Business-facing analytical marts.
7. Automated tests and source-to-target reconciliation.
8. Repeatable pipeline execution and logging.
9. GitHub repository with architecture and operating documentation.

## 7. Guiding principles

- Preserve source data in RAW; do not silently overwrite source evidence.
- Define and validate grain before joining facts.
- Make ingestion and transformations repeatable and idempotent.
- Separate business definitions from technical implementation.
- Make assumptions visible and track unresolved decisions.
- Prefer simple, explainable architecture over unnecessary technology.
- Keep credentials and generated data out of public version control.
- Treat all generated records as synthetic.

## 8. Project status

Planning and initial source-data validation. Cloud infrastructure and transformation implementation are pending.
