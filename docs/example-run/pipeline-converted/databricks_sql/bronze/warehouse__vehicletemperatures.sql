-- Source: OLTP:Warehouse.VehicleTemperatures  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Warehouse/Tables/VehicleTemperatures.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.warehouse__vehicletemperatures (
    VehicleTemperatureID BIGINT NOT NULL,
    VehicleRegistration STRING NOT NULL,
    ChillerSensorNumber INT NOT NULL,
    RecordedWhen TIMESTAMP NOT NULL,
    Temperature DECIMAL(10,2) NOT NULL,
    FullSensorData STRING,
    IsCompressed BOOLEAN NOT NULL,
    CompressedSensorData BINARY
)
USING DELTA
COMMENT 'Converted from OLTP:Warehouse.VehicleTemperatures'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `VehicleTemperatureID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta
-- `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline
-- (see target_state_architecture.md, Unity Catalog section).
-- Source table was MEMORY_OPTIMIZED (SQL Server In-Memory OLTP) — no Delta Lake equivalent. Converted
-- to a standard Delta table; if sub-millisecond OLTP-style access was relied upon, this workload may
-- not be a good fit for Delta and should be redesigned (see manual_intervention_list.md).