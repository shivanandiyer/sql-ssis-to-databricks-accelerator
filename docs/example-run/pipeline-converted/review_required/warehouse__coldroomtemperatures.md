# Review Required: OLTP:Warehouse.ColdRoomTemperatures

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Warehouse/Tables/ColdRoomTemperatures.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `ColdRoomTemperatureID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `ValidFrom` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Column `ValidTo` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Column `INDEX` ([IX_Warehouse_ColdRoomTemperatures_ColdRoomSensorNumber] -> STRING): Unrecognised SQL Server type '[IX_Warehouse_ColdRoomTemperatures_ColdRoomSensorNumber]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Source table was MEMORY_OPTIMIZED (SQL Server In-Memory OLTP) — no Delta Lake equivalent. Converted to a standard Delta table; if sub-millisecond OLTP-style access was relied upon, this workload may not be a good fit for Delta and should be redesigned (see manual_intervention_list.md).
- Source table used SQL Server temporal tables (FOR SYSTEM_TIME / paired _Archive table). Recommended replacement: enable `delta.enableChangeDataFeed` and query history via `TIMESTAMP AS OF` / `VERSION AS OF`, or `table_changes()`. The paired _Archive table is converted separately and should be reconciled with this table's Delta history rather than kept as a second physical table long-term.

## Source DDL (for reference)

```sql
CREATE TABLE [Warehouse].[ColdRoomTemperatures] (
    [ColdRoomTemperatureID] BIGINT                                      IDENTITY (1, 1) NOT NULL,
    [ColdRoomSensorNumber]  INT                                         NOT NULL,
    [RecordedWhen]          DATETIME2 (7)                               NOT NULL,
    [Temperature]           DECIMAL (10, 2)                             NOT NULL,
    [ValidFrom]             DATETIME2 (7) GENERATED ALWAYS AS ROW START NOT NULL,
    [ValidTo]               DATETIME2 (7) GENERATED ALWAYS AS ROW END   NOT NULL,
    CONSTRAINT [PK_Warehouse_ColdRoomTemperatures] PRIMARY KEY NONCLUSTERED ([ColdRoomTemperatureID] ASC),
    INDEX [IX_Warehouse_ColdRoomTemperatures_ColdRoomSensorNumber] NONCLUSTERED ([ColdRoomSensorNumber]),
    PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
)
WITH (MEMORY_OPTIMIZED = ON, SYSTEM_VERSIONING = ON (HISTORY_TABLE=[Warehouse].[ColdRoomTemperatures_Archive], DATA_CONSISTENCY_CHECK=ON));
```