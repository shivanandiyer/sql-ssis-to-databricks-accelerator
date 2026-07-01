# Review Required: OLTP:Warehouse.VehicleTemperatures

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Warehouse/Tables/VehicleTemperatures.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `VehicleTemperatureID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Source table was MEMORY_OPTIMIZED (SQL Server In-Memory OLTP) — no Delta Lake equivalent. Converted to a standard Delta table; if sub-millisecond OLTP-style access was relied upon, this workload may not be a good fit for Delta and should be redesigned (see manual_intervention_list.md).

## Source DDL (for reference)

```sql
CREATE TABLE [Warehouse].[VehicleTemperatures] (
    [VehicleTemperatureID] BIGINT          IDENTITY (1, 1) NOT NULL,
    [VehicleRegistration]  NVARCHAR (20)   COLLATE Latin1_General_CI_AS NOT NULL,
    [ChillerSensorNumber]  INT             NOT NULL,
    [RecordedWhen]         DATETIME2 (7)   NOT NULL,
    [Temperature]          DECIMAL (10, 2) NOT NULL,
    [FullSensorData]       NVARCHAR (1000) COLLATE Latin1_General_CI_AS NULL,
    [IsCompressed]         BIT             NOT NULL,
    [CompressedSensorData] VARBINARY (MAX) NULL,
    CONSTRAINT [PK_Warehouse_VehicleTemperatures] PRIMARY KEY NONCLUSTERED ([VehicleTemperatureID] ASC)
)
WITH (MEMORY_OPTIMIZED = ON);
```