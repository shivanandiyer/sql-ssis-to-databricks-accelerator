# Review Required: DW:Integration.Order_Staging

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Tables/Order_Staging.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Column `Order` (Staging -> STRING): Unrecognised SQL Server type 'Staging' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Order` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `City` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Salesperson` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Picker` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Order -> STRING): Unrecognised SQL Server type 'Order' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Backorder -> STRING): Unrecognised SQL Server type 'Backorder' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Unit` (Price] -> STRING): Unrecognised SQL Server type 'Price]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Tax` (Rate] -> STRING): Unrecognised SQL Server type 'Rate]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Total` (Excluding -> STRING): Unrecognised SQL Server type 'Excluding' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Tax` (Amount] -> STRING): Unrecognised SQL Server type 'Amount]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Total` (Including -> STRING): Unrecognised SQL Server type 'Including' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (City -> STRING): Unrecognised SQL Server type 'City' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Salesperson -> STRING): Unrecognised SQL Server type 'Salesperson' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Picker -> STRING): Unrecognised SQL Server type 'Picker' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Last` (Modified -> STRING): Unrecognised SQL Server type 'Modified' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Integration].[Order_Staging] (
    [Order Staging Key]   BIGINT          IDENTITY (1, 1) NOT NULL,
    [City Key]            INT             NULL,
    [Customer Key]        INT             NULL,
    [Stock Item Key]      INT             NULL,
    [Order Date Key]      DATE            NULL,
    [Picked Date Key]     DATE            NULL,
    [Salesperson Key]     INT             NULL,
    [Picker Key]          INT             NULL,
    [WWI Order ID]        INT             NULL,
    [WWI Backorder ID]    INT             NULL,
    [Description]         NVARCHAR (100)  NULL,
    [Package]             NVARCHAR (50)   NULL,
    [Quantity]            INT             NULL,
    [Unit Price]          DECIMAL (18, 2) NULL,
    [Tax Rate]            DECIMAL (18, 3) NULL,
    [Total Excluding Tax] DECIMAL (18, 2) NULL,
    [Tax Amount]          DECIMAL (18, 2) NULL,
    [Total Including Tax] DECIMAL (18, 2) NULL,
    [Lineage Key]         INT             NULL,
    [WWI City ID]         INT             NULL,
    [WWI Customer ID]     INT             NULL,
    [WWI Stock Item ID]   INT             NULL,
    [WWI Salesperson ID]  INT             NULL,
    [WWI Picker ID]       INT             NULL,
    [Last Modified When]  DATETIME2 (7)   NULL,
    CONSTRAINT [PK_Integration_Order_Staging] PRIMARY KEY NONCLUSTERED ([Order Staging Key] ASC)
)
WITH (DURABILITY = SCHEMA_ONLY, MEMORY_OPTIMIZED = ON);
```