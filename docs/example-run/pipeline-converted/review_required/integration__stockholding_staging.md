# Review Required: DW:Integration.StockHolding_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/StockHolding_Staging.sql
- **Classification:** LIFT_AND_SHIFT

## Why this needs manual review

- Column `Stock` (Holding -> STRING): Unrecognised SQL Server type 'Holding' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Stock` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Quantity` (On -> STRING): Unrecognised SQL Server type 'On' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Bin` (Location] -> STRING): Unrecognised SQL Server type 'Location]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Last` (Stocktake -> STRING): Unrecognised SQL Server type 'Stocktake' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Last` (Cost -> STRING): Unrecognised SQL Server type 'Cost' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Reorder` (Level] -> STRING): Unrecognised SQL Server type 'Level]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Target` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[StockHolding_Staging] (
    [Stock Holding Staging Key] BIGINT          IDENTITY (1, 1) NOT NULL,
    [Stock Item Key]            INT             NULL,
    [Quantity On Hand]          INT             NULL,
    [Bin Location]              NVARCHAR (20)   NULL,
    [Last Stocktake Quantity]   INT             NULL,
    [Last Cost Price]           DECIMAL (18, 2) NULL,
    [Reorder Level]             INT             NULL,
    [Target Stock Level]        INT             NULL,
    [WWI Stock Item ID]         INT             NULL,
    CONSTRAINT [PK_Integration_Stock_Holding_Staging] PRIMARY KEY NONCLUSTERED ([Stock Holding Staging Key] ASC)
)
WITH (DURABILITY = SCHEMA_ONLY, MEMORY_OPTIMIZED = ON);
```