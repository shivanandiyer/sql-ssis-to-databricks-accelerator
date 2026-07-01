# Review Required: DW:Integration.Supplier_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Supplier_Staging.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Column `Supplier` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Supplier` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `WWI` (Supplier -> STRING): Unrecognised SQL Server type 'Supplier' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Primary` (Contact] -> STRING): Unrecognised SQL Server type 'Contact]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Supplier` (Reference] -> STRING): Unrecognised SQL Server type 'Reference]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Payment` (Days] -> STRING): Unrecognised SQL Server type 'Days]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Postal` (Code] -> STRING): Unrecognised SQL Server type 'Code]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[Supplier_Staging] (
    [Supplier Staging Key] INT            IDENTITY (1, 1) NOT NULL,
    [WWI Supplier ID]      INT            NOT NULL,
    [Supplier]             NVARCHAR (100) NOT NULL,
    [Category]             NVARCHAR (50)  NOT NULL,
    [Primary Contact]      NVARCHAR (50)  NOT NULL,
    [Supplier Reference]   NVARCHAR (20)  NULL,
    [Payment Days]         INT            NOT NULL,
    [Postal Code]          NVARCHAR (10)  NOT NULL,
    [Valid From]           DATETIME2 (7)  NOT NULL,
    [Valid To]             DATETIME2 (7)  NOT NULL,
    CONSTRAINT [PK_Integration_Supplier_Staging] PRIMARY KEY NONCLUSTERED ([Supplier Staging Key] ASC)
)
WITH (DURABILITY = SCHEMA_ONLY, MEMORY_OPTIMIZED = ON);
```