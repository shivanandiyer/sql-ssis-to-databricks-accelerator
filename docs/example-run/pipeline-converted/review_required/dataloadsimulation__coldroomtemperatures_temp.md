# Review Required: OLTP:DataLoadSimulation.ColdRoomTemperatures_temp

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Tables/ColdRoomTemperatures_temp.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `INDEX` ([IX_DataSimulation_ColdRoomTemperatures_ColdRoomSensorNumber] -> STRING): Unrecognised SQL Server type '[IX_DataSimulation_ColdRoomTemperatures_ColdRoomSensorNumber]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `since` (this -> STRING): Unrecognised SQL Server type 'this' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Source table was MEMORY_OPTIMIZED (SQL Server In-Memory OLTP) — no Delta Lake equivalent. Converted to a standard Delta table; if sub-millisecond OLTP-style access was relied upon, this workload may not be a good fit for Delta and should be redesigned (see manual_intervention_list.md).

## Source DDL (for reference)

```sql
CREATE TABLE DataLoadSimulation.[ColdRoomTemperatures_temp] (
    [ColdRoomTemperatureID] BIGINT                                      NOT NULL,
    [ColdRoomSensorNumber]  INT                                         NOT NULL,
    [RecordedWhen]          DATETIME2 (7)                               NOT NULL,
    [Temperature]           DECIMAL (10, 2)                             NOT NULL,
    [ValidFrom]             DATETIME2 (7)								NOT NULL,
    [ValidTo]               DATETIME2 (7)								NOT NULL,
    INDEX [IX_DataSimulation_ColdRoomTemperatures_ColdRoomSensorNumber]
		NONCLUSTERED HASH ([ColdRoomSensorNumber]) WITH (BUCKET_COUNT=100000)
		-- 100K was chosen as bucket_count, since this number is always a good starting point, and
		--   number of sensors is not expected to exceed 1 million. (if it were to exceed 1 million,
		--   a performance degradation would be expected)
)
WITH (MEMORY_OPTIMIZED = ON, DURABILITY=SCHEMA_ONLY);
```