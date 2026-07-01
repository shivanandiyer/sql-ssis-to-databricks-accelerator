# Review Required: OLTP:Application.Countries

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/Countries.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `CountryID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `Border` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend storing as WKT STRING and adding an H3 index column, or adopting a geospatial library (Databricks Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.
- Column `ValidFrom` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Column `ValidTo` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Application_Countries_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] 
- Source table used SQL Server temporal tables (FOR SYSTEM_TIME / paired _Archive table). Recommended replacement: enable `delta.enableChangeDataFeed` and query history via `TIMESTAMP AS OF` / `VERSION AS OF`, or `table_changes()`. The paired _Archive table is converted separately and should be reconciled with this table's Delta history rather than kept as a second physical table long-term.

## Source DDL (for reference)

```sql
CREATE TABLE [Application].[Countries] (
    [CountryID]                INT                                         CONSTRAINT [DF_Application_Countries_CountryID] DEFAULT (NEXT VALUE FOR [Sequences].[CountryID]) NOT NULL,
    [CountryName]              NVARCHAR (60)                               NOT NULL,
    [FormalName]               NVARCHAR (60)                               NOT NULL,
    [IsoAlpha3Code]            NVARCHAR (3)                                NULL,
    [IsoNumericCode]           INT                                         NULL,
    [CountryType]              NVARCHAR (20)                               NULL,
    [LatestRecordedPopulation] BIGINT                                      NULL,
    [Continent]                NVARCHAR (30)                               NOT NULL,
    [Region]                   NVARCHAR (30)                               NOT NULL,
    [Subregion]                NVARCHAR (30)                               NOT NULL,
    [Border]                   [sys].[geography]                           NULL,
    [LastEditedBy]             INT                                         NOT NULL,
    [ValidFrom]                DATETIME2 (7) GENERATED ALWAYS AS ROW START NOT NULL,
    [ValidTo]                  DATETIME2 (7) GENERATED ALWAYS AS ROW END   NOT NULL,
    CONSTRAINT [PK_Application_Countries] PRIMARY KEY CLUSTERED ([CountryID] ASC),
    CONSTRAINT [FK_Application_Countries_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([PersonID]),
    CONSTRAINT [UQ_Application_Countries_CountryName] UNIQUE NONCLUSTERED ([CountryName] ASC),
    CONSTRAINT [UQ_Application_Countries_FormalName] UNIQUE NONCLUSTERED ([FormalName] ASC),
    PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE=[Application].[Countries_Archive], DATA_CONSISTENCY_CHECK=ON));


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'Countries that contain the states or provinces (including geographic boundaries)', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'Countries';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Numeric ID used for reference to a country within the database', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'Countries', @level2type = N'COLUMN', @level2name = N'CountryID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Name of the country', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'Countries', @level2type = N'COLUMN', @level2name = N'CountryName';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Full formal name of the country as agreed by United Nations', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'Countries', @level2type = N'COLUMN', @level2name = N'FormalName';


GO
EXECUTE sp_ad
```