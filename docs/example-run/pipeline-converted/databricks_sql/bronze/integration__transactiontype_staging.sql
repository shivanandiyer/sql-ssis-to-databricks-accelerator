-- Source: DW:Integration.TransactionType_Staging  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/TransactionType_Staging.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.transactiontype_staging (
    Transaction STRING NOT NULL COMMENT 'source type: Type',
    WWI STRING NOT NULL COMMENT 'source type: Transaction',
    Transaction STRING NOT NULL COMMENT 'source type: Type]',
    Valid STRING NOT NULL COMMENT 'source type: From]',
    Valid STRING NOT NULL COMMENT 'source type: To]'
)
USING DELTA
COMMENT 'Converted from DW:Integration.TransactionType_Staging'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Transaction` (Type -> STRING): Unrecognised SQL Server type 'Type' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Transaction` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `WWI` (Transaction -> STRING): Unrecognised SQL Server type 'Transaction' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Transaction` (Type] -> STRING): Unrecognised SQL Server type 'Type]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.