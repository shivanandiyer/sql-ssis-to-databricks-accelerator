-- Source: DW:dbo.SampleVersion  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/dbo/Tables/SampleVersion.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.sampleversion (
    MajorSampleVersion INT NOT NULL,
    MinorSampleVersion INT NOT NULL,
    MinSQLServerBuild STRING NOT NULL,
    RowCount INT NOT NULL
)
USING DELTA
COMMENT 'Converted from DW:dbo.SampleVersion'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
