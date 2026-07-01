-- Source: DW:Dimension.City  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Dimension/Tables/City.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.silver.city (
    City STRING NOT NULL COMMENT 'source type: Key]',
    WWI STRING NOT NULL COMMENT 'source type: City',
    City STRING NOT NULL,
    State STRING NOT NULL COMMENT 'source type: Province]',
    Country STRING NOT NULL,
    Continent STRING NOT NULL,
    Sales STRING NOT NULL COMMENT 'source type: Territory]',
    Region STRING NOT NULL,
    Subregion STRING NOT NULL,
    Location STRING COMMENT 'source type: [sys].[geography]',
    Latest STRING NOT NULL COMMENT 'source type: Recorded',
    Valid STRING NOT NULL COMMENT 'source type: From]',
    Valid STRING NOT NULL COMMENT 'source type: To]',
    Lineage STRING NOT NULL COMMENT 'source type: Key]'
)
USING DELTA
COMMENT 'Converted from DW:Dimension.City'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `City` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `City` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS
-- IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `WWI` (City -> STRING): Unrecognised SQL Server type 'City' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `State` (Province] -> STRING): Unrecognised SQL Server type 'Province]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Sales` (Territory] -> STRING): Unrecognised SQL Server type 'Territory]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Location` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend
-- storing as WKT STRING and adding an H3 index column, or adopting a geospatial library (Databricks
-- Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.
-- Column `Latest` (Recorded -> STRING): Unrecognised SQL Server type 'Recorded' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.