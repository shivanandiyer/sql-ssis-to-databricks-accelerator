-- Source: OLTP:Application.Countries_Archive  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/Countries_Archive.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.application__countries_archive (
    CountryID INT NOT NULL,
    CountryName STRING NOT NULL,
    FormalName STRING NOT NULL,
    IsoAlpha3Code STRING,
    IsoNumericCode INT,
    CountryType STRING,
    LatestRecordedPopulation BIGINT,
    Continent STRING NOT NULL,
    Region STRING NOT NULL,
    Subregion STRING NOT NULL,
    Border STRING COMMENT 'source type: [sys].[geography]',
    LastEditedBy INT NOT NULL,
    ValidFrom TIMESTAMP NOT NULL,
    ValidTo TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Application.Countries_Archive'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Border` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend
-- storing as WKT STRING and adding an H3 index column, or adopting a geospatial library (Databricks
-- Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.