-- Source: OLTP:DataLoadSimulation.ColdRoomTemperatures_temp  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Tables/ColdRoomTemperatures_temp.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.dataloadsimulation__coldroomtemperatures_temp (
    ColdRoomTemperatureID BIGINT NOT NULL,
    ColdRoomSensorNumber INT NOT NULL,
    RecordedWhen TIMESTAMP NOT NULL,
    Temperature DECIMAL(10,2) NOT NULL,
    ValidFrom TIMESTAMP NOT NULL,
    ValidTo TIMESTAMP NOT NULL,
    INDEX STRING COMMENT 'source type: [IX_DataSimulation_ColdRoomTemperatures_ColdRoomSensorNumber]',
    since STRING COMMENT 'source type: this'
)
USING DELTA
COMMENT 'Converted from OLTP:DataLoadSimulation.ColdRoomTemperatures_temp'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `INDEX` ([IX_DataSimulation_ColdRoomTemperatures_ColdRoomSensorNumber] -> STRING):
-- Unrecognised SQL Server type '[IX_DataSimulation_ColdRoomTemperatures_ColdRoomSensorNumber]' —
-- defaulted to STRING. MANUAL REVIEW REQUIRED.
-- Column `since` (this -> STRING): Unrecognised SQL Server type 'this' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Source table was MEMORY_OPTIMIZED (SQL Server In-Memory OLTP) — no Delta Lake equivalent. Converted
-- to a standard Delta table; if sub-millisecond OLTP-style access was relied upon, this workload may
-- not be a good fit for Delta and should be redesigned (see manual_intervention_list.md).