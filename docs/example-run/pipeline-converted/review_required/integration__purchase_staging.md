# Review Required: DW:Integration.Purchase_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Purchase_Staging.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Column `Purchase` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Purchase` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Purchase -> STRING): Unrecognised SQL Server type 'Purchase' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Ordered` (Outers] -> STRING): Unrecognised SQL Server type 'Outers]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Ordered` (Quantity] -> STRING): Unrecognised SQL Server type 'Quantity]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Received` (Outers] -> STRING): Unrecognised SQL Server type 'Outers]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Is` (Order -> STRING): Unrecognised SQL Server type 'Order' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Supplier -> STRING): Unrecognised SQL Server type 'Supplier' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Last` (Modified -> STRING): Unrecognised SQL Server type 'Modified' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[Purchase_Staging] (
    [Purchase Staging Key]  BIGINT        IDENTITY (1, 1) NOT NULL,
    [Date Key]              DATE          NULL,
    [Supplier Key]          INT           NULL,
    [Stock Item Key]        INT           NULL,
    [WWI Purchase Order ID] INT           NULL,
    [Ordered Outers]        INT           NULL,
    [Ordered Quantity]      INT           NULL,
    [Received Outers]       INT           NULL,
    [Package]               NVARCHAR (50) NULL,
    [Is Order Finalized]    BIT           NULL,
    [WWI Supplier ID]       INT           NULL,
    [WWI Stock Item ID]     INT           NULL,
    [Last Modified When]    DATETIME2 (7) NULL,
    CONSTRAINT [PK_Integration_Purchase_Staging] PRIMARY KEY NONCLUSTERED ([Purchase Staging Key] ASC)
)
WITH (DURABILITY = SCHEMA_ONLY, MEMORY_OPTIMIZED = ON);
```