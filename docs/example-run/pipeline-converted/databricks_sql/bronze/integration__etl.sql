-- Source: DW:Integration.ETL  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/ETL Cutoff.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.etl (

)
USING DELTA
COMMENT 'Converted from DW:Integration.ETL'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
