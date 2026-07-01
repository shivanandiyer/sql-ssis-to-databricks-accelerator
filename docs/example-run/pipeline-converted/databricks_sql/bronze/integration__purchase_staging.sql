-- Source: DW:Integration.Purchase_Staging  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Purchase_Staging.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.purchase_staging (
    Purchase STRING NOT NULL COMMENT 'source type: Staging',
    Date STRING COMMENT 'source type: Key]',
    Supplier STRING COMMENT 'source type: Key]',
    Stock STRING COMMENT 'source type: Item',
    WWI STRING COMMENT 'source type: Purchase',
    Ordered STRING COMMENT 'source type: Outers]',
    Ordered STRING COMMENT 'source type: Quantity]',
    Received STRING COMMENT 'source type: Outers]',
    Package STRING,
    Is STRING COMMENT 'source type: Order',
    WWI STRING COMMENT 'source type: Supplier',
    WWI STRING COMMENT 'source type: Stock',
    Last STRING COMMENT 'source type: Modified'
)
USING DELTA
COMMENT 'Converted from DW:Integration.Purchase_Staging'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Purchase` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Purchase` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Purchase -> STRING): Unrecognised SQL Server type 'Purchase' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Ordered` (Outers] -> STRING): Unrecognised SQL Server type 'Outers]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Ordered` (Quantity] -> STRING): Unrecognised SQL Server type 'Quantity]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Received` (Outers] -> STRING): Unrecognised SQL Server type 'Outers]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Is` (Order -> STRING): Unrecognised SQL Server type 'Order' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Supplier -> STRING): Unrecognised SQL Server type 'Supplier' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Last` (Modified -> STRING): Unrecognised SQL Server type 'Modified' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.