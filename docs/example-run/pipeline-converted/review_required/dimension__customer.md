# Review Required: DW:Dimension.Customer

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Dimension/Tables/Customer.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Customer` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Bill` (To -> STRING): Unrecognised SQL Server type 'To' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Buying` (Group] -> STRING): Unrecognised SQL Server type 'Group]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Primary` (Contact] -> STRING): Unrecognised SQL Server type 'Contact]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Postal` (Code] -> STRING): Unrecognised SQL Server type 'Code]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (From] -> STRING): Unrecognised SQL Server type 'From]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Valid` (To] -> STRING): Unrecognised SQL Server type 'To]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.

## Source DDL (for reference)

```sql
CREATE TABLE [Dimension].[Customer] (
    [Customer Key]     INT            CONSTRAINT [DF_Dimension_Customer_Customer_Key] DEFAULT (NEXT VALUE FOR [Sequences].[CustomerKey]) NOT NULL,
    [WWI Customer ID]  INT            NOT NULL,
    [Customer]         NVARCHAR (100) NOT NULL,
    [Bill To Customer] NVARCHAR (100) NOT NULL,
    [Category]         NVARCHAR (50)  NOT NULL,
    [Buying Group]     NVARCHAR (50)  NOT NULL,
    [Primary Contact]  NVARCHAR (50)  NOT NULL,
    [Postal Code]      NVARCHAR (10)  NOT NULL,
    [Valid From]       DATETIME2 (7)  NOT NULL,
    [Valid To]         DATETIME2 (7)  NOT NULL,
    [Lineage Key]      INT            NOT NULL,
    CONSTRAINT [PK_Dimension_Customer] PRIMARY KEY CLUSTERED ([Customer Key] ASC)
);


GO
CREATE NONCLUSTERED INDEX [IX_Dimension_Customer_WWICustomerID]
    ON [Dimension].[Customer]([WWI Customer ID] ASC, [Valid From] ASC, [Valid To] ASC);


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Allows quickly locating by WWI ID', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'Customer', @level2type = N'INDEX', @level2name = N'IX_Dimension_Customer_WWICustomerID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'Customer dimension', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'Customer';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'DW key for the customer dimension', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'Customer', @level2type = N'COLUMN', @level2name = N'Customer Key';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Numeric ID used for reference to a customer within the WWI database', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'Customer', @level2type = N'COLUMN', @level2name = N'WWI Customer ID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Customer''s full name (usually a trading name)', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'Customer', @level2type = N'COLUMN', @level2name = N'Customer';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Bill to customer''s full name', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'Customer', @level2type = N'COLUMN', @level2name = N'Bill To Customer';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Customer''s category', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'Customer', @level2type = N'COLUMN', @level2name = N'Category';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Customer''s buying group', @level0type = N'SCHEMA', @level0name = N'Dimension', @level1type = N'TABLE', @level1name = N'Customer', @level2type = N'COLUMN', @level2name = N'Buying G
```