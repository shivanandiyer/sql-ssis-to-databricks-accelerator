-- Source: DW:Integration.Sale_Staging  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Sale_Staging.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.sale_staging (
    Sale STRING NOT NULL COMMENT 'source type: Staging',
    City STRING COMMENT 'source type: Key]',
    Customer STRING COMMENT 'source type: Key]',
    Bill STRING COMMENT 'source type: To',
    Stock STRING COMMENT 'source type: Item',
    Invoice DATE,
    Delivery DATE,
    Salesperson STRING COMMENT 'source type: Key]',
    WWI STRING COMMENT 'source type: Invoice',
    Description STRING,
    Package STRING,
    Quantity INT,
    Unit STRING COMMENT 'source type: Price]',
    Tax STRING COMMENT 'source type: Rate]',
    Total STRING COMMENT 'source type: Excluding',
    Tax STRING COMMENT 'source type: Amount]',
    Profit DECIMAL(18,2),
    Total STRING COMMENT 'source type: Including',
    Total STRING COMMENT 'source type: Dry',
    Total STRING COMMENT 'source type: Chiller',
    WWI STRING COMMENT 'source type: City',
    WWI STRING COMMENT 'source type: Customer',
    WWI STRING COMMENT 'source type: Bill',
    WWI STRING COMMENT 'source type: Stock',
    WWI STRING COMMENT 'source type: Salesperson',
    Last STRING COMMENT 'source type: Modified'
)
USING DELTA
COMMENT 'Converted from DW:Integration.Sale_Staging'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Sale` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Sale` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS
-- IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `City` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Bill` (To -> STRING): Unrecognised SQL Server type 'To' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Salesperson` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Unit` (Price] -> STRING): Unrecognised SQL Server type 'Price]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Tax` (Rate] -> STRING): Unrecognised SQL Server type 'Rate]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Total` (Excluding -> STRING): Unrecognised SQL Server type 'Excluding' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Tax` (Amount] -> STRING): Unrecognised SQL Server type 'Amount]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Total` (Including -> STRING): Unrecognised SQL Server type 'Including' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Total` (Dry -> STRING): Unrecognised SQL Server type 'Dry' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Total` (Chiller -> STRING): Unrecognised SQL Server type 'Chiller' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (City -> STRING): Unrecognised SQL Server type 'City' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Bill -> STRING): Unrecognised SQL Server type 'Bill' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Salesperson -> STRING): Unrecognised SQL Server type 'Salesperson' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Last` (Modified -> STRING): Unrecognised SQL Server type 'Modified' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.