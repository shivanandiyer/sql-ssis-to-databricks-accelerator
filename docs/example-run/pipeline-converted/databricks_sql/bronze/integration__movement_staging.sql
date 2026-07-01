-- Source: DW:Integration.Movement_Staging  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Movement_Staging.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.movement_staging (
    Movement STRING NOT NULL COMMENT 'source type: Staging',
    Date STRING COMMENT 'source type: Key]',
    Stock STRING COMMENT 'source type: Item',
    Customer STRING COMMENT 'source type: Key]',
    Supplier STRING COMMENT 'source type: Key]',
    Transaction STRING COMMENT 'source type: Type',
    WWI STRING COMMENT 'source type: Stock',
    WWI STRING COMMENT 'source type: Invoice',
    WWI STRING COMMENT 'source type: Purchase',
    Quantity INT,
    WWI STRING COMMENT 'source type: Stock',
    WWI STRING COMMENT 'source type: Customer',
    WWI STRING COMMENT 'source type: Supplier',
    WWI STRING COMMENT 'source type: Transaction',
    Last STRING COMMENT 'source type: Modifed'
)
USING DELTA
COMMENT 'Converted from DW:Integration.Movement_Staging'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Movement` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Movement` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Transaction` (Type -> STRING): Unrecognised SQL Server type 'Type' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Purchase -> STRING): Unrecognised SQL Server type 'Purchase' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Supplier -> STRING): Unrecognised SQL Server type 'Supplier' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Transaction -> STRING): Unrecognised SQL Server type 'Transaction' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Last` (Modifed -> STRING): Unrecognised SQL Server type 'Modifed' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.