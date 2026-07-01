# Review Required: DW:Integration.PaymentMethod_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/PaymentMethod_Staging.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Column `Payment` (Method -> STRING): Unrecognised SQL Server type 'Method' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Payment` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `WWI` (Payment -> STRING): Unrecognised SQL Server type 'Payment' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Payment` (Method] -> STRING): Unrecognised SQL Server type 'Method]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[PaymentMethod_Staging] (
    [Payment Method Staging Key] INT           IDENTITY (1, 1) NOT NULL,
    [WWI Payment Method ID]      INT           NOT NULL,
    [Payment Method]             NVARCHAR (50) NOT NULL,
    [Valid From]                 DATETIME2 (7) NOT NULL,
    [Valid To]                   DATETIME2 (7) NOT NULL,
    CONSTRAINT [PK_Integration_Payment_Method_Staging] PRIMARY KEY NONCLUSTERED ([Payment Method Staging Key] ASC)
)
WITH (DURABILITY = SCHEMA_ONLY, MEMORY_OPTIMIZED = ON);
```