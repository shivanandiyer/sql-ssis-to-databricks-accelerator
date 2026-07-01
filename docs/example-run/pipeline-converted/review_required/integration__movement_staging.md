# Review Required: DW:Integration.Movement_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Movement_Staging.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Column `Movement` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Movement` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Transaction` (Type -> STRING): Unrecognised SQL Server type 'Type' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Purchase -> STRING): Unrecognised SQL Server type 'Purchase' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Supplier -> STRING): Unrecognised SQL Server type 'Supplier' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Transaction -> STRING): Unrecognised SQL Server type 'Transaction' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Last` (Modifed -> STRING): Unrecognised SQL Server type 'Modifed' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[Movement_Staging] (
    [Movement Staging Key]          BIGINT        IDENTITY (1, 1) NOT NULL,
    [Date Key]                      DATE          NULL,
    [Stock Item Key]                INT           NULL,
    [Customer Key]                  INT           NULL,
    [Supplier Key]                  INT           NULL,
    [Transaction Type Key]          INT           NULL,
    [WWI Stock Item Transaction ID] INT           NULL,
    [WWI Invoice ID]                INT           NULL,
    [WWI Purchase Order ID]         INT           NULL,
    [Quantity]                      INT           NULL,
    [WWI Stock Item ID]             INT           NULL,
    [WWI Customer ID]               INT           NULL,
    [WWI Supplier ID]               INT           NULL,
    [WWI Transaction Type ID]       INT           NULL,
    [Last Modifed When]             DATETIME2 (7) NULL,
    CONSTRAINT [PK_Integration_Movement_Staging] PRIMARY KEY NONCLUSTERED ([Movement Staging Key] ASC)
)
WITH (DURABILITY = SCHEMA_ONLY, MEMORY_OPTIMIZED = ON);
```