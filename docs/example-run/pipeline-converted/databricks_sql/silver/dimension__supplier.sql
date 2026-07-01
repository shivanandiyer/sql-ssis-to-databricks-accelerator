-- Source: DW:Dimension.Supplier  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Dimension/Tables/Supplier.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.silver.supplier (
    Supplier STRING NOT NULL COMMENT 'source type: Key]',
    WWI STRING NOT NULL COMMENT 'source type: Supplier',
    Supplier STRING NOT NULL,
    Category STRING NOT NULL,
    Primary STRING NOT NULL COMMENT 'source type: Contact]',
    Supplier STRING COMMENT 'source type: Reference]',
    Payment STRING NOT NULL COMMENT 'source type: Days]',
    Postal STRING NOT NULL COMMENT 'source type: Code]',
    Valid STRING NOT NULL COMMENT 'source type: From]',
    Valid STRING NOT NULL COMMENT 'source type: To]',
    Lineage STRING NOT NULL COMMENT 'source type: Key]'
)
USING DELTA
COMMENT 'Converted from DW:Dimension.Supplier'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Supplier` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `WWI` (Supplier -> STRING): Unrecognised SQL Server type 'Supplier' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Primary` (Contact] -> STRING): Unrecognised SQL Server type 'Contact]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Supplier` (Reference] -> STRING): Unrecognised SQL Server type 'Reference]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Payment` (Days] -> STRING): Unrecognised SQL Server type 'Days]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Postal` (Code] -> STRING): Unrecognised SQL Server type 'Code]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.