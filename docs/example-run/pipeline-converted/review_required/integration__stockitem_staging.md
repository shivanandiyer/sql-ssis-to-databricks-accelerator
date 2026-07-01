# Review Required: DW:Integration.StockItem_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/StockItem_Staging.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Stock` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Stock` (Item] -> STRING): Unrecognised SQL Server type 'Item]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Selling` (Package] -> STRING): Unrecognised SQL Server type 'Package]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Buying` (Package] -> STRING): Unrecognised SQL Server type 'Package]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Lead` (Time -> STRING): No native TIME type in Spark SQL; stored as STRING (HH:MM:SS.fffffff). Consider STRING or cast to TIMESTAMP with a fixed date if arithmetic is required.
- Column `Quantity` (Per -> STRING): Unrecognised SQL Server type 'Per' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Is` (Chiller -> STRING): Unrecognised SQL Server type 'Chiller' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Tax` (Rate] -> STRING): Unrecognised SQL Server type 'Rate]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Unit` (Price] -> STRING): Unrecognised SQL Server type 'Price]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Recommended` (Retail -> STRING): Unrecognised SQL Server type 'Retail' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Typical` (Weight -> STRING): Unrecognised SQL Server type 'Weight' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[StockItem_Staging] (
    [Stock Item Staging Key]   INT             IDENTITY (1, 1) NOT NULL,
    [WWI Stock Item ID]        INT             NOT NULL,
    [Stock Item]               NVARCHAR (100)  NOT NULL,
    [Color]                    NVARCHAR (20)   NOT NULL,
    [Selling Package]          NVARCHAR (50)   NOT NULL,
    [Buying Package]           NVARCHAR (50)   NOT NULL,
    [Brand]                    NVARCHAR (50)   NOT NULL,
    [Size]                     NVARCHAR (20)   NOT NULL,
    [Lead Time Days]           INT             NOT NULL,
    [Quantity Per Outer]       INT             NOT NULL,
    [Is Chiller Stock]         BIT             NOT NULL,
    [Barcode]                  NVARCHAR (50)   NULL,
    [Tax Rate]                 DECIMAL (18, 3) NOT NULL,
    [Unit Price]               DECIMAL (18, 2) NOT NULL,
    [Recommended Retail Price] DECIMAL (18, 2) NULL,
    [Typical Weight Per Unit]  DECIMAL (18, 3) NOT NULL,
    [Photo]                    VARBINARY (MAX) NULL,
    [Valid From]               DATETIME2 (7)   NOT NULL,
    [Valid To]                 DATETIME2 (7)   NOT NULL,
    CONSTRAINT [PK_Integration_Stock_Item_Staging] PRIMARY KEY NONCLUSTERED ([Stock Item Staging Key] ASC)
)
WITH (DURABILITY = SCHEMA_ONLY, MEMORY_OPTIMIZED = ON);
```