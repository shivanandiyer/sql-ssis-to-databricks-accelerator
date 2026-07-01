# Review Required: DW:Integration.City_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/City_Staging.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `City` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `City` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `WWI` (City -> STRING): Unrecognised SQL Server type 'City' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `State` (Province] -> STRING): Unrecognised SQL Server type 'Province]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Sales` (Territory] -> STRING): Unrecognised SQL Server type 'Territory]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Location` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend storing as WKT STRING and adding an H3 index column, or adopting a geospatial library (Databricks Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.
- Column `Latest` (Recorded -> STRING): Unrecognised SQL Server type 'Recorded' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[City_Staging] (
    [City Staging Key]           INT               IDENTITY (1, 1) NOT NULL,
    [WWI City ID]                INT               NOT NULL,
    [City]                       NVARCHAR (50)     NOT NULL,
    [State Province]             NVARCHAR (50)     NOT NULL,
    [Country]                    NVARCHAR (60)     NOT NULL,
    [Continent]                  NVARCHAR (30)     NOT NULL,
    [Sales Territory]            NVARCHAR (50)     NOT NULL,
    [Region]                     NVARCHAR (30)     NOT NULL,
    [Subregion]                  NVARCHAR (30)     NOT NULL,
    [Location]                   [sys].[geography] NULL,
    [Latest Recorded Population] BIGINT            NOT NULL,
    [Valid From]                 DATETIME2 (7)     NOT NULL,
    [Valid To]                   DATETIME2 (7)     NOT NULL,
    CONSTRAINT [PK_Integration_City_Staging] PRIMARY KEY CLUSTERED ([City Staging Key] ASC)
);


GO
CREATE NONCLUSTERED INDEX [IX_Integration_City_Staging_WWI_City_ID]
    ON [Integration].[City_Staging]([WWI City ID] ASC);


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Allows quickly locating by WWI City Key', @level0type = N'SCHEMA', @level0name = N'Integration', @level1type = N'TABLE', @level1name = N'City_Staging', @level2type = N'INDEX', @level2name = N'IX_Integration_City_Staging_WWI_City_ID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'City staging table', @level0type = N'SCHEMA', @level0name = N'Integration', @level1type = N'TABLE', @level1name = N'City_Staging';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Row ID within the staging table', @level0type = N'SCHEMA', @level0name = N'Integration', @level1type = N'TABLE', @level1name = N'City_Staging', @level2type = N'COLUMN', @level2name = N'City Staging Key';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Numeric ID used for reference to a city within the WWI database', @level0type = N'SCHEMA', @level0name = N'Integration', @level1type = N'TABLE', @level1name = N'City_Staging', @level2type = N'COLUMN', @level2name = N'WWI City ID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Formal name of the city', @level0type = N'SCHEMA', @level0name = N'Integration', @level1type = N'TABLE', @level1name = N'City_Staging', @level2type = N'COLUMN', @level2name = N'City';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'State or province for this city', @level0type = N'SCHEMA', @level0name = N'Integration', @level1type = N'TABLE', @level1name = N'City_Staging', @level2type = N'COLUMN', @level2name = N'State Province';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Country name', @level0type = N'SCHEMA', @level0name = N'Integration', @level1type = N'TABLE', @level1name = N'City_Staging', @level2type = N'COLUMN', @level2name = N'Country';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Cont
```