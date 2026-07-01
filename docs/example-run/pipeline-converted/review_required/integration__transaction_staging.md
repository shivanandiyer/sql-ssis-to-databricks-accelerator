# Review Required: DW:Integration.Transaction_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Transaction_Staging.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Column `Transaction` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Transaction` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Bill` (To -> STRING): Unrecognised SQL Server type 'To' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Transaction` (Type -> STRING): Unrecognised SQL Server type 'Type' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Payment` (Method -> STRING): Unrecognised SQL Server type 'Method' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Supplier -> STRING): Unrecognised SQL Server type 'Supplier' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Purchase -> STRING): Unrecognised SQL Server type 'Purchase' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Supplier` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Total` (Excluding -> STRING): Unrecognised SQL Server type 'Excluding' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Tax` (Amount] -> STRING): Unrecognised SQL Server type 'Amount]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Total` (Including -> STRING): Unrecognised SQL Server type 'Including' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Outstanding` (Balance] -> STRING): Unrecognised SQL Server type 'Balance]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Is` (Finalized] -> STRING): Unrecognised SQL Server type 'Finalized]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Bill -> STRING): Unrecognised SQL Server type 'Bill' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Supplier -> STRING): Unrecognised SQL Server type 'Supplier' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Transaction -> STRING): Unrecognised SQL Server type 'Transaction' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Payment -> STRING): Unrecognised SQL Server type 'Payment' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Last` (Modified -> STRING): Unrecognised SQL Server type 'Modified' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[Transaction_Staging] (
    [Transaction Staging Key]     BIGINT          IDENTITY (1, 1) NOT NULL,
    [Date Key]                    DATE            NULL,
    [Customer Key]                INT             NULL,
    [Bill To Customer Key]        INT             NULL,
    [Supplier Key]                INT             NULL,
    [Transaction Type Key]        INT             NULL,
    [Payment Method Key]          INT             NULL,
    [WWI Customer Transaction ID] INT             NULL,
    [WWI Supplier Transaction ID] INT             NULL,
    [WWI Invoice ID]              INT             NULL,
    [WWI Purchase Order ID]       INT             NULL,
    [Supplier Invoice Number]     NVARCHAR (20)   NULL,
    [Total Excluding Tax]         DECIMAL (18, 2) NULL,
    [Tax Amount]                  DECIMAL (18, 2) NULL,
    [Total Including Tax]         DECIMAL (18, 2) NULL,
    [Outstanding Balance]         DECIMAL (18, 2) NULL,
    [Is Finalized]                BIT             NULL,
    [WWI Customer ID]             INT             NULL,
    [WWI Bill To Customer ID]     INT             NULL,
    [WWI Supplier ID]             INT             NULL,
    [WWI Transaction Type ID]     INT             NULL,
    [WWI Payment Method ID]       INT             NULL,
    [Last Modified When]          DATETIME2 (7)   NULL,
    CONSTRAINT [PK_Integration_Transaction_Staging] PRIMARY KEY NONCLUSTERED ([Transaction Staging Key] ASC)
)
WITH (DURABILITY = SCHEMA_ONLY, MEMORY_OPTIMIZED = ON);
```