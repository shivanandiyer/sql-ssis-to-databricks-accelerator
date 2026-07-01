-- Source: DW:Integration.Order_Staging  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Order_Staging.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.order_staging (
    Order STRING NOT NULL COMMENT 'source type: Staging',
    City STRING COMMENT 'source type: Key]',
    Customer STRING COMMENT 'source type: Key]',
    Stock STRING COMMENT 'source type: Item',
    Order DATE,
    Picked DATE,
    Salesperson STRING COMMENT 'source type: Key]',
    Picker STRING COMMENT 'source type: Key]',
    WWI STRING COMMENT 'source type: Order',
    WWI STRING COMMENT 'source type: Backorder',
    Description STRING,
    Package STRING,
    Quantity INT,
    Unit STRING COMMENT 'source type: Price]',
    Tax STRING COMMENT 'source type: Rate]',
    Total STRING COMMENT 'source type: Excluding',
    Tax STRING COMMENT 'source type: Amount]',
    Total STRING COMMENT 'source type: Including',
    Lineage STRING COMMENT 'source type: Key]',
    WWI STRING COMMENT 'source type: City',
    WWI STRING COMMENT 'source type: Customer',
    WWI STRING COMMENT 'source type: Stock',
    WWI STRING COMMENT 'source type: Salesperson',
    WWI STRING COMMENT 'source type: Picker',
    Last STRING COMMENT 'source type: Modified'
)
USING DELTA
COMMENT 'Converted from DW:Integration.Order_Staging'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Order` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Order` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS
-- AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `City` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Salesperson` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Picker` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Order -> STRING): Unrecognised SQL Server type 'Order' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Backorder -> STRING): Unrecognised SQL Server type 'Backorder' — defaulted to STRING.
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
-- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (City -> STRING): Unrecognised SQL Server type 'City' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Salesperson -> STRING): Unrecognised SQL Server type 'Salesperson' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `WWI` (Picker -> STRING): Unrecognised SQL Server type 'Picker' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Last` (Modified -> STRING): Unrecognised SQL Server type 'Modified' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.