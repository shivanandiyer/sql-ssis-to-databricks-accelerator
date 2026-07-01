# Review Required: DW:Dimension.City

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Dimension/Tables/City.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `City` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `City` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `WWI` (City -> STRING): Unrecognised SQL Server type 'City' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `State` (Province] -> STRING): Unrecognised SQL Server type 'Province]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Sales` (Territory] -> STRING): Unrecognised SQL Server type 'Territory]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Location` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend storing as WKT STRING and adding an H3 index column, or adopting a geospatial library (Databricks Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.
- Column `Latest` (Recorded -> STRING): Unrecognised SQL Server type 'Recorded' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Dimension].[City] (
    [City Key]                   INT               CONSTRAINT [DF_Dimension_City_City_Key] DEFAULT (NEXT VALUE FOR [Sequences].[CityKey]) NOT NULL,
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
    [Lineage Key]                INT               NOT NULL,
    CONSTRAINT [PK_Dimension_City] PRIMARY KEY CLUSTERED ([City Key] ASC)
);


GO
CREATE NONCLUSTERED INDEX [IX_Dimension_City_WWICityID]
    ON [Dimension].[City]([WWI City ID] ASC, [Valid From] ASC, [Valid To] ASC);


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Allows quickly locating by WWI ID', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'City', @level2type = N'INDEX', @level2name = N'IX_Dimension_City_WWICityID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'City dimension', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'City';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'DW key for the city dimension', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'City', @level2type = N'COLUMN', @level2name = N'City Key';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Numeric ID used for reference to a city within the WWI database', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'City', @level2type = N'COLUMN', @level2name = N'WWI City ID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Formal name of the city', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'City', @level2type = N'COLUMN', @level2name = N'City';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'State or province for this city', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'City', @level2type = N'COLUMN', @level2name = N'State Province';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Country name', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'City', @level2type = N'COLUMN', @level2name = N'Country';


GO
EXECUTE sp_addextendedproperty @name = N'Description', 
```