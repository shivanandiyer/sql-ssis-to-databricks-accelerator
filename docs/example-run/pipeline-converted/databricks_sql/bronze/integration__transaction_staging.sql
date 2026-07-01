-- Source: DW:Integration.Transaction_Staging  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Transaction_Staging.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.transaction_staging (
    Transaction STRING NOT NULL COMMENT 'source type: Staging',
    Date STRING COMMENT 'source type: Key]',
    Customer STRING COMMENT 'source type: Key]',
    Bill STRING COMMENT 'source type: To',
    Supplier STRING COMMENT 'source type: Key]',
    Transaction STRING COMMENT 'source type: Type',
    Payment STRING COMMENT 'source type: Method',
    WWI STRING COMMENT 'source type: Customer',
    WWI STRING COMMENT 'source type: Supplier',
    WWI STRING COMMENT 'source type: Invoice',
    WWI STRING COMMENT 'source type: Purchase',
    Supplier STRING COMMENT 'source type: Invoice',
    Total STRING COMMENT 'source type: Excluding',
    Tax STRING COMMENT 'source type: Amount]',
    Total STRING COMMENT 'source type: Including',
    Outstanding STRING COMMENT 'source type: Balance]',
    Is STRING COMMENT 'source type: Finalized]',
    WWI STRING COMMENT 'source type: Customer',
    WWI STRING COMMENT 'source type: Bill',
    WWI STRING COMMENT 'source type: Supplier',
    WWI STRING COMMENT 'source type: Transaction',
    WWI STRING COMMENT 'source type: Payment',
    Last STRING COMMENT 'source type: Modified'
)
USING DELTA
COMMENT 'Converted from DW:Integration.Transaction_Staging'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Transaction` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Transaction` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Bill` (To -> STRING): Unrecognised SQL Server type 'To' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Transaction` (Type -> STRING): Unrecognised SQL Server type 'Type' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Payment` (Method -> STRING): Unrecognised SQL Server type 'Method' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Supplier -> STRING): Unrecognised SQL Server type 'Supplier' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Purchase -> STRING): Unrecognised SQL Server type 'Purchase' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Supplier` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Total` (Excluding -> STRING): Unrecognised SQL Server type 'Excluding' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Tax` (Amount] -> STRING): Unrecognised SQL Server type 'Amount]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Total` (Including -> STRING): Unrecognised SQL Server type 'Including' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Outstanding` (Balance] -> STRING): Unrecognised SQL Server type 'Balance]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Is` (Finalized] -> STRING): Unrecognised SQL Server type 'Finalized]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Bill -> STRING): Unrecognised SQL Server type 'Bill' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Supplier -> STRING): Unrecognised SQL Server type 'Supplier' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Transaction -> STRING): Unrecognised SQL Server type 'Transaction' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `WWI` (Payment -> STRING): Unrecognised SQL Server type 'Payment' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Last` (Modified -> STRING): Unrecognised SQL Server type 'Modified' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.