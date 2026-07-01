# Review Required: DW:Integration.Employee_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Employee_Staging.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Column `Employee` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Employee` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `WWI` (Employee -> STRING): Unrecognised SQL Server type 'Employee' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Preferred` (Name] -> STRING): Unrecognised SQL Server type 'Name]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Is` (Salesperson] -> STRING): Unrecognised SQL Server type 'Salesperson]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[Employee_Staging] (
    [Employee Staging Key] INT             IDENTITY (1, 1) NOT NULL,
    [WWI Employee ID]      INT             NOT NULL,
    [Employee]             NVARCHAR (50)   NOT NULL,
    [Preferred Name]       NVARCHAR (50)   NOT NULL,
    [Is Salesperson]       BIT             NOT NULL,
    [Photo]                VARBINARY (MAX) NULL,
    [Valid From]           DATETIME2 (7)   NOT NULL,
    [Valid To]             DATETIME2 (7)   NOT NULL,
    CONSTRAINT [PK_Integration_Employee_Staging] PRIMARY KEY NONCLUSTERED ([Employee Staging Key] ASC)
)
WITH (DURABILITY = SCHEMA_ONLY, MEMORY_OPTIMIZED = ON);
```