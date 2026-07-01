# Review Required: OLTP:Application.StateProvinces_Archive

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/StateProvinces_Archive.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `Border` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend storing as WKT STRING and adding an H3 index column, or adopting a geospatial library (Databricks Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Application].[StateProvinces_Archive] (
    [StateProvinceID]          INT               NOT NULL,
    [StateProvinceCode]        NVARCHAR (5)      NOT NULL,
    [StateProvinceName]        NVARCHAR (50)     NOT NULL,
    [CountryID]                INT               NOT NULL,
    [SalesTerritory]           NVARCHAR (50)     NOT NULL,
    [Border]                   [sys].[geography] NULL,
    [LatestRecordedPopulation] BIGINT            NULL,
    [LastEditedBy]             INT               NOT NULL,
    [ValidFrom]                DATETIME2 (7)     NOT NULL,
    [ValidTo]                  DATETIME2 (7)     NOT NULL
);


GO
CREATE CLUSTERED INDEX [ix_StateProvinces_Archive]
    ON [Application].[StateProvinces_Archive]([ValidTo] ASC, [ValidFrom] ASC) WITH (DATA_COMPRESSION = PAGE);
```