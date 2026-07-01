# Review Required: DW:Integration.Customer_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Customer_Staging.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Column `Customer` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Customer` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Bill` (To -> STRING): Unrecognised SQL Server type 'To' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Buying` (Group] -> STRING): Unrecognised SQL Server type 'Group]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Primary` (Contact] -> STRING): Unrecognised SQL Server type 'Contact]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Postal` (Code] -> STRING): Unrecognised SQL Server type 'Code]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[Customer_Staging] (
    [Customer Staging Key] INT            IDENTITY (1, 1) NOT NULL,
    [WWI Customer ID]      INT            NOT NULL,
    [Customer]             NVARCHAR (100) NOT NULL,
    [Bill To Customer]     NVARCHAR (100) NOT NULL,
    [Category]             NVARCHAR (50)  NOT NULL,
    [Buying Group]         NVARCHAR (50)  NOT NULL,
    [Primary Contact]      NVARCHAR (50)  NOT NULL,
    [Postal Code]          NVARCHAR (10)  NOT NULL,
    [Valid From]           DATETIME2 (7)  NOT NULL,
    [Valid To]             DATETIME2 (7)  NOT NULL,
    CONSTRAINT [PK_Integration_Customer_Staging] PRIMARY KEY NONCLUSTERED ([Customer Staging Key] ASC)
)
WITH (DURABILITY = SCHEMA_ONLY, MEMORY_OPTIMIZED = ON);
```