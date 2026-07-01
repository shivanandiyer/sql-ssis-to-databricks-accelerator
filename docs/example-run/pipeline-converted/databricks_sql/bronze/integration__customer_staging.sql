-- Source: DW:Integration.Customer_Staging  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Customer_Staging.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.customer_staging (
    Customer STRING NOT NULL COMMENT 'source type: Staging',
    WWI STRING NOT NULL COMMENT 'source type: Customer',
    Customer STRING NOT NULL,
    Bill STRING NOT NULL COMMENT 'source type: To',
    Category STRING NOT NULL,
    Buying STRING NOT NULL COMMENT 'source type: Group]',
    Primary STRING NOT NULL COMMENT 'source type: Contact]',
    Postal STRING NOT NULL COMMENT 'source type: Code]',
    Valid STRING NOT NULL COMMENT 'source type: From]',
    Valid STRING NOT NULL COMMENT 'source type: To]'
)
USING DELTA
COMMENT 'Converted from DW:Integration.Customer_Staging'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Customer` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Customer` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Bill` (To -> STRING): Unrecognised SQL Server type 'To' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `Buying` (Group] -> STRING): Unrecognised SQL Server type 'Group]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Primary` (Contact] -> STRING): Unrecognised SQL Server type 'Contact]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Postal` (Code] -> STRING): Unrecognised SQL Server type 'Code]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.