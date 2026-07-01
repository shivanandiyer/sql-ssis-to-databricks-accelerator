-- Source: DW:Integration.StockHolding_Staging  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/StockHolding_Staging.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.stockholding_staging (
    Stock STRING NOT NULL COMMENT 'source type: Holding',
    Stock STRING COMMENT 'source type: Item',
    Quantity STRING COMMENT 'source type: On',
    Bin STRING COMMENT 'source type: Location]',
    Last STRING COMMENT 'source type: Stocktake',
    Last STRING COMMENT 'source type: Cost',
    Reorder STRING COMMENT 'source type: Level]',
    Target STRING COMMENT 'source type: Stock',
    WWI STRING COMMENT 'source type: Stock'
)
USING DELTA
COMMENT 'Converted from DW:Integration.StockHolding_Staging'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Stock` (Holding -> STRING): Unrecognised SQL Server type 'Holding' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Stock` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS
-- AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Quantity` (On -> STRING): Unrecognised SQL Server type 'On' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Bin` (Location] -> STRING): Unrecognised SQL Server type 'Location]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Last` (Stocktake -> STRING): Unrecognised SQL Server type 'Stocktake' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Last` (Cost -> STRING): Unrecognised SQL Server type 'Cost' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Reorder` (Level] -> STRING): Unrecognised SQL Server type 'Level]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Target` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.