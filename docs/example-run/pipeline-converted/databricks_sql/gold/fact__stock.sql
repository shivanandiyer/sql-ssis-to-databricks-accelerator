-- Source: DW:Fact.Stock  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Fact/Tables/Stock Holding.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.gold.stock (

)
USING DELTA
COMMENT 'Converted from DW:Fact.Stock'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
