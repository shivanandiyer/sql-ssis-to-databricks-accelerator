-- Source: DW:Integration.Lineage  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Lineage.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.lineage (
    Lineage STRING NOT NULL COMMENT 'source type: Key]',
    Data STRING NOT NULL COMMENT 'source type: Load',
    Table STRING NOT NULL COMMENT 'source type: Name]',
    Data STRING COMMENT 'source type: Load',
    Was STRING NOT NULL COMMENT 'source type: Successful]',
    Source STRING NOT NULL COMMENT 'source type: System'
)
USING DELTA
COMMENT 'Converted from DW:Integration.Lineage'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Lineage` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS
-- AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `Data` (Load -> STRING): Unrecognised SQL Server type 'Load' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Table` (Name] -> STRING): Unrecognised SQL Server type 'Name]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Data` (Load -> STRING): Unrecognised SQL Server type 'Load' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Was` (Successful] -> STRING): Unrecognised SQL Server type 'Successful]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Source` (System -> STRING): Unrecognised SQL Server type 'System' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.