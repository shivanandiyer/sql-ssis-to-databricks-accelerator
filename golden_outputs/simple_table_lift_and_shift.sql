-- Source: OLTP:DataLoadSimulation.FicticiousNamePool  (fixtures/sql/simple_table_lift_and_shift.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_dev.bronze.application__deliverymethods (
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
