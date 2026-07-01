-- Source: OLTP:DataLoadSimulation.AreaCode  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Tables/AreaCode.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.dataloadsimulation__areacode (
    StateProvinceCode STRING,
    AreaCode STRING
)
USING DELTA
COMMENT 'Converted from OLTP:DataLoadSimulation.AreaCode'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
