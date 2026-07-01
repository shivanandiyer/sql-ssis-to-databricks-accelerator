-- Source: DW:Dimension.Payment  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Dimension/Tables/Payment Method.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.silver.payment (

)
USING DELTA
COMMENT 'Converted from DW:Dimension.Payment'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
