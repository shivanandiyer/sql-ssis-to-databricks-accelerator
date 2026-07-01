-- Source: OLTP:Warehouse.ColdRoomTemperatures_Archive  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Warehouse/Tables/ColdRoomTemperatures_Archive.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.warehouse__coldroomtemperatures_archive (
    ColdRoomTemperatureID BIGINT NOT NULL,
    ColdRoomSensorNumber INT NOT NULL,
    RecordedWhen TIMESTAMP NOT NULL,
    Temperature DECIMAL(10,2) NOT NULL,
    ValidFrom TIMESTAMP NOT NULL,
    ValidTo TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Warehouse.ColdRoomTemperatures_Archive'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
