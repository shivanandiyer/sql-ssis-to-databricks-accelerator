# Review Required: OLTP:Application.StateProvinces

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/StateProvinces.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `StateProvinceID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `Border` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend storing as WKT STRING and adding an H3 index column, or adopting a geospatial library (Databricks Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.
- Column `ValidFrom` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Column `ValidTo` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Application_StateProvinces_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[Peo
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Application_StateProvinces_CountryID_Application_Countries] FOREIGN KEY ([CountryID]) REFERENCES [Applica
- Source table used SQL Server temporal tables (FOR SYSTEM_TIME / paired _Archive table). Recommended replacement: enable `delta.enableChangeDataFeed` and query history via `TIMESTAMP AS OF` / `VERSION AS OF`, or `table_changes()`. The paired _Archive table is converted separately and should be reconciled with this table's Delta history rather than kept as a second physical table long-term.

## Source DDL (for reference)

```sql
CREATE TABLE [Application].[StateProvinces] (
    [StateProvinceID]          INT                                         CONSTRAINT [DF_Application_StateProvinces_StateProvinceID] DEFAULT (NEXT VALUE FOR [Sequences].[StateProvinceID]) NOT NULL,
    [StateProvinceCode]        NVARCHAR (5)                                NOT NULL,
    [StateProvinceName]        NVARCHAR (50)                               NOT NULL,
    [CountryID]                INT                                         NOT NULL,
    [SalesTerritory]           NVARCHAR (50)                               NOT NULL,
    [Border]                   [sys].[geography]                           NULL,
    [LatestRecordedPopulation] BIGINT                                      NULL,
    [LastEditedBy]             INT                                         NOT NULL,
    [ValidFrom]                DATETIME2 (7) GENERATED ALWAYS AS ROW START NOT NULL,
    [ValidTo]                  DATETIME2 (7) GENERATED ALWAYS AS ROW END   NOT NULL,
    CONSTRAINT [PK_Application_StateProvinces] PRIMARY KEY CLUSTERED ([StateProvinceID] ASC),
    CONSTRAINT [FK_Application_StateProvinces_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([PersonID]),
    CONSTRAINT [FK_Application_StateProvinces_CountryID_Application_Countries] FOREIGN KEY ([CountryID]) REFERENCES [Application].[Countries] ([CountryID]),
    CONSTRAINT [UQ_Application_StateProvinces_StateProvinceName] UNIQUE NONCLUSTERED ([StateProvinceName] ASC),
    PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE=[Application].[StateProvinces_Archive], DATA_CONSISTENCY_CHECK=ON));


GO
CREATE NONCLUSTERED INDEX [FK_Application_StateProvinces_CountryID]
    ON [Application].[StateProvinces]([CountryID] ASC);


GO
CREATE NONCLUSTERED INDEX [IX_Application_StateProvinces_SalesTerritory]
    ON [Application].[StateProvinces]([SalesTerritory] ASC);


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Auto-created to support a foreign key', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'StateProvinces', @level2type = N'INDEX', @level2name = N'FK_Application_StateProvinces_CountryID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Index used to quickly locate sales territories', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'StateProvinces', @level2type = N'INDEX', @level2name = N'IX_Application_StateProvinces_SalesTerritory';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'States or provinces that contain cities (including geographic location)', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'StateProvinces';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Numeric ID used for reference to a state or province within the database', @level0type = N'SCHEMA', @level0n
```