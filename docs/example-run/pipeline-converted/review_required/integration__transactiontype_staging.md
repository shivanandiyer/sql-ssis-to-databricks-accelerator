# Review Required: DW:Integration.TransactionType_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/TransactionType_Staging.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Column `Transaction` (Type -> STRING): Unrecognised SQL Server type 'Type' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Transaction` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `WWI` (Transaction -> STRING): Unrecognised SQL Server type 'Transaction' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Transaction` (Type] -> STRING): Unrecognised SQL Server type 'Type]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[TransactionType_Staging] (
    [Transaction Type Staging Key] INT           IDENTITY (1, 1) NOT NULL,
    [WWI Transaction Type ID]      INT           NOT NULL,
    [Transaction Type]             NVARCHAR (50) NOT NULL,
    [Valid From]                   DATETIME2 (7) NOT NULL,
    [Valid To]                     DATETIME2 (7) NOT NULL,
    CONSTRAINT [PK_Integration_Transaction_Type_Staging] PRIMARY KEY NONCLUSTERED ([Transaction Type Staging Key] ASC)
)
WITH (DURABILITY = SCHEMA_ONLY, MEMORY_OPTIMIZED = ON);
```