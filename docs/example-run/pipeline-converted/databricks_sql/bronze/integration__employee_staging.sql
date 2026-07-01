-- Source: DW:Integration.Employee_Staging  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Employee_Staging.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.employee_staging (
    Employee STRING NOT NULL COMMENT 'source type: Staging',
    WWI STRING NOT NULL COMMENT 'source type: Employee',
    Employee STRING NOT NULL,
    Preferred STRING NOT NULL COMMENT 'source type: Name]',
    Is STRING NOT NULL COMMENT 'source type: Salesperson]',
    Photo BINARY,
    Valid STRING NOT NULL COMMENT 'source type: From]',
    Valid STRING NOT NULL COMMENT 'source type: To]'
)
USING DELTA
COMMENT 'Converted from DW:Integration.Employee_Staging'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Employee` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Employee` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `WWI` (Employee -> STRING): Unrecognised SQL Server type 'Employee' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Preferred` (Name] -> STRING): Unrecognised SQL Server type 'Name]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Is` (Salesperson] -> STRING): Unrecognised SQL Server type 'Salesperson]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.