USE ROLE ACCOUNTADMIN;
USE WAREHOUSE PHARMA_WH;
USE DATABASE PHARMA_DB;
USE SCHEMA RAW;

--copy product table
COPY INTO PRODUCT
FROM (
    SELECT
        $1, $2, $3, $4, $5,
        $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15,
        $16, $17,
        METADATA$FILENAME,
        METADATA$START_SCAN_TIME::TIMESTAMP_NTZ
    FROM @PHARMA_STAGE/static/product.csv
)
ON_ERROR = 'ABORT_STATEMENT';

--Territory load;
COPY INTO TERRITORY
FROM (
    SELECT
        $1, $2, $3, $4, $5,
        METADATA$FILENAME,
        METADATA$START_SCAN_TIME::TIMESTAMP_NTZ
    FROM @PHARMA_STAGE/static/territory.csv
)
ON_ERROR = 'ABORT_STATEMENT';

--Specialty product map load;
COPY INTO SPECIALTY_PRODUCT_MAP
FROM (
    SELECT
        $1, $2,
        METADATA$FILENAME,
        METADATA$START_SCAN_TIME::TIMESTAMP_NTZ
    FROM @PHARMA_STAGE/static/specialty_product_map.csv
)
ON_ERROR = 'ABORT_STATEMENT';

--Account Master load;
COPY INTO ACCOUNT_MASTER
FROM (
    SELECT
        $1, $2, $3, $4, $5,
        $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15,
        $16, $17, $18, $19,
        METADATA$FILENAME,
        METADATA$START_SCAN_TIME::TIMESTAMP_NTZ
    FROM @PHARMA_STAGE/dimensions/account_master/account_master_2026_01.csv
)
ON_ERROR = 'ABORT_STATEMENT';

--HCP_Master load;
COPY INTO HCP_MASTER
FROM (
    SELECT
        $1, $2, $3, $4, $5,
        $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15,
        $16, $17, $18, $19, $20,
        $21, $22, $23, $24, $25,
        METADATA$FILENAME,
        METADATA$START_SCAN_TIME::TIMESTAMP_NTZ
    FROM @PHARMA_STAGE/dimensions/hcp_master/hcp_master_2026_01.csv
)
ON_ERROR = 'ABORT_STATEMENT';

--Roster load;
COPY INTO ROSTER
FROM (
    SELECT
        $1, $2, $3, $4, $5,
        $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15,
        $16, $17, $18,
        METADATA$FILENAME,
        METADATA$START_SCAN_TIME::TIMESTAMP_NTZ
    FROM @PHARMA_STAGE/dimensions/roster/roster_2026_01.csv
)
ON_ERROR = 'ABORT_STATEMENT';

--Xponent;
COPY INTO XPONENT
FROM (
    SELECT
        $1, $2, $3, $4, $5,
        $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15,
        $16, $17, $18,
        METADATA$FILENAME,
        METADATA$START_SCAN_TIME::TIMESTAMP_NTZ
    FROM @PHARMA_STAGE/facts/xponent/xponent_2026_01.csv
)
ON_ERROR = 'ABORT_STATEMENT';

--Calls Interactions load;
COPY INTO CALLS_INTERACTIONS
FROM (
    SELECT
        $1, $2, $3, $4, $5,
        $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15,
        $16, $17, $18, $19, $20,
        METADATA$FILENAME,
        METADATA$START_SCAN_TIME::TIMESTAMP_NTZ
    FROM @PHARMA_STAGE/facts/calls_interactions/calls_interactions_2026_01.csv
)
ON_ERROR = 'ABORT_STATEMENT';

--Samples load;
COPY INTO SAMPLES
FROM (
    SELECT
        $1, $2, $3, $4, $5,
        $6, $7, $8, $9, $10,
        $11, $12, $13, $14, $15,
        $16, $17, $18,
        METADATA$FILENAME,
        METADATA$START_SCAN_TIME::TIMESTAMP_NTZ
    FROM @PHARMA_STAGE/facts/samples/samples_2026_01.csv
)
ON_ERROR = 'ABORT_STATEMENT';

--check;
SELECT TABLE_NAME, ROW_COUNT
FROM PHARMA_DB.INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'RAW'
  AND TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;