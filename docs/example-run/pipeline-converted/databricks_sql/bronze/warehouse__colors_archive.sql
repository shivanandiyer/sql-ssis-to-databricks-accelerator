-- Source: OLTP:Warehouse.Colors_Archive  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Warehouse/Tables/Colors_Archive.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.warehouse__colors_archive (
    ColorID INT NOT NULL,
    ColorName STRING NOT NULL,
    LastEditedBy INT NOT NULL,
    ValidFrom TIMESTAMP NOT NULL,
    ValidTo TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Warehouse.Colors_Archive'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
