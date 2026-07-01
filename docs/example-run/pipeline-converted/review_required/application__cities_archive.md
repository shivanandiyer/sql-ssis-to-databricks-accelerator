# Review Required: OLTP:Application.Cities_Archive

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/Cities_Archive.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `Location` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend storing as WKT STRING and adding an H3 index column, or adopting a geospatial library (Databricks Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Application].[Cities_Archive] (
    [CityID]                   INT               NOT NULL,
    [CityName]                 NVARCHAR (50)     NOT NULL,
    [StateProvinceID]          INT               NOT NULL,
    [Location]                 [sys].[geography] NULL,
    [LatestRecordedPopulation] BIGINT            NULL,
    [LastEditedBy]             INT               NOT NULL,
    [ValidFrom]                DATETIME2 (7)     NOT NULL,
    [ValidTo]                  DATETIME2 (7)     NOT NULL
);


GO
CREATE CLUSTERED INDEX [ix_Cities_Archive]
    ON [Application].[Cities_Archive]([ValidTo] ASC, [ValidFrom] ASC) WITH (DATA_COMPRESSION = PAGE);
```