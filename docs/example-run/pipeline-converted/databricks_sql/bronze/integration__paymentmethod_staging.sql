-- Source: DW:Integration.PaymentMethod_Staging  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/PaymentMethod_Staging.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.paymentmethod_staging (
    Payment STRING NOT NULL COMMENT 'source type: Method',
    WWI STRING NOT NULL COMMENT 'source type: Payment',
    Payment STRING NOT NULL COMMENT 'source type: Method]',
    Valid STRING NOT NULL COMMENT 'source type: From]',
    Valid STRING NOT NULL COMMENT 'source type: To]'
)
USING DELTA
COMMENT 'Converted from DW:Integration.PaymentMethod_Staging'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Payment` (Method -> STRING): Unrecognised SQL Server type 'Method' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Payment` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS
-- AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `WWI` (Payment -> STRING): Unrecognised SQL Server type 'Payment' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Payment` (Method] -> STRING): Unrecognised SQL Server type 'Method]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.