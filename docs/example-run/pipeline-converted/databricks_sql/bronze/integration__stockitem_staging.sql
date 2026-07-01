-- Source: DW:Integration.StockItem_Staging  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/StockItem_Staging.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.stockitem_staging (
    Stock STRING NOT NULL COMMENT 'source type: Item',
    WWI STRING NOT NULL COMMENT 'source type: Stock',
    Stock STRING NOT NULL COMMENT 'source type: Item]',
    Color STRING NOT NULL,
    Selling STRING NOT NULL COMMENT 'source type: Package]',
    Buying STRING NOT NULL COMMENT 'source type: Package]',
    Brand STRING NOT NULL,
    Size STRING NOT NULL,
    Lead STRING NOT NULL COMMENT 'source type: Time',
    Quantity STRING NOT NULL COMMENT 'source type: Per',
    Is STRING NOT NULL COMMENT 'source type: Chiller',
    Barcode STRING,
    Tax STRING NOT NULL COMMENT 'source type: Rate]',
    Unit STRING NOT NULL COMMENT 'source type: Price]',
    Recommended STRING COMMENT 'source type: Retail',
    Typical STRING NOT NULL COMMENT 'source type: Weight',
    Photo BINARY,
    Valid STRING NOT NULL COMMENT 'source type: From]',
    Valid STRING NOT NULL COMMENT 'source type: To]'
)
USING DELTA
COMMENT 'Converted from DW:Integration.StockItem_Staging'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Stock` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS
-- AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Stock` (Item] -> STRING): Unrecognised SQL Server type 'Item]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Selling` (Package] -> STRING): Unrecognised SQL Server type 'Package]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Buying` (Package] -> STRING): Unrecognised SQL Server type 'Package]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Lead` (Time -> STRING): No native TIME type in Spark SQL; stored as STRING
-- (HH:MM:SS.fffffff). Consider STRING or cast to TIMESTAMP with a fixed date if arithmetic is
-- required.
-- Column `Quantity` (Per -> STRING): Unrecognised SQL Server type 'Per' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Is` (Chiller -> STRING): Unrecognised SQL Server type 'Chiller' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Tax` (Rate] -> STRING): Unrecognised SQL Server type 'Rate]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Unit` (Price] -> STRING): Unrecognised SQL Server type 'Price]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Recommended` (Retail -> STRING): Unrecognised SQL Server type 'Retail' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Typical` (Weight -> STRING): Unrecognised SQL Server type 'Weight' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.