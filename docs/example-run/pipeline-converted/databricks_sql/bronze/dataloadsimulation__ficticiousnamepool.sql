-- Source: OLTP:DataLoadSimulation.FicticiousNamePool  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Tables/FicticiousNamePool.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.dataloadsimulation__ficticiousnamepool (
    FullName STRING,
    PreferredName STRING,
    LastName STRING,
    ToEmail STRING
)
USING DELTA
COMMENT 'Converted from OLTP:DataLoadSimulation.FicticiousNamePool'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
