-- Source: DW:Dimension.Transaction  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Dimension/Tables/Transaction Type.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.silver.transaction (

)
USING DELTA
COMMENT 'Converted from DW:Dimension.Transaction'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
