-- Source: OLTP:Application.Logs  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/Logs.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.application__logs (
    Message STRING NOT NULL,
    Level STRING NOT NULL,
    EventTime TIMESTAMP NOT NULL,
    LogEvent STRING,
    INDEX STRING COMMENT 'source type: CCX_Application_Logs'
)
USING DELTA
COMMENT 'Converted from OLTP:Application.Logs'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `INDEX` (CCX_Application_Logs -> STRING): Unrecognised SQL Server type 'CCX_Application_Logs'
-- — defaulted to STRING. MANUAL REVIEW REQUIRED.