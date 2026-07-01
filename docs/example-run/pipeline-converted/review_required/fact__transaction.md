# Review Required: DW:Fact.Transaction

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Fact/Tables/Transaction.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `Transaction` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
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
- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Transaction_Bill_To_Customer_Key_Dimension_Customer] FOREIGN KEY ([Bill To Customer Key]) REFERENCES
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Transaction_Customer_Key_Dimension_Customer] FOREIGN KEY ([Customer Key]) REFERENCES [Dimension].[Cu
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Transaction_Date_Key_Dimension_Date] FOREIGN KEY ([Date Key]) REFERENCES [Dimension].[Date] ([Date])
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Transaction_Payment_Method_Key_Dimension_Payment Method] FOREIGN KEY ([Payment Method Key]) REFERENC
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Transaction_Supplier_Key_Dimension_Supplier] FOREIGN KEY ([Supplier Key]) REFERENCES [Dimension].[Su
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Transaction_Transaction_Type_Key_Dimension_Transaction Type] FOREIGN KEY ([Transaction Type Key]) RE

## Source DDL (for reference)

```sql
CREATE TABLE [Fact].[Transaction] (
    [Transaction Key]             BIGINT          IDENTITY (1, 1) NOT NULL,
    [Date Key]                    DATE            NOT NULL,
    [Customer Key]                INT             NULL,
    [Bill To Customer Key]        INT             NULL,
    [Supplier Key]                INT             NULL,
    [Transaction Type Key]        INT             NOT NULL,
    [Payment Method Key]          INT             NULL,
    [WWI Customer Transaction ID] INT             NULL,
    [WWI Supplier Transaction ID] INT             NULL,
    [WWI Invoice ID]              INT             NULL,
    [WWI Purchase Order ID]       INT             NULL,
    [Supplier Invoice Number]     NVARCHAR (20)   NULL,
    [Total Excluding Tax]         DECIMAL (18, 2) NOT NULL,
    [Tax Amount]                  DECIMAL (18, 2) NOT NULL,
    [Total Including Tax]         DECIMAL (18, 2) NOT NULL,
    [Outstanding Balance]         DECIMAL (18, 2) NOT NULL,
    [Is Finalized]                BIT             NOT NULL,
    [Lineage Key]                 INT             NOT NULL,
    CONSTRAINT [PK_Fact_Transaction] PRIMARY KEY NONCLUSTERED ([Transaction Key] ASC, [Date Key] ASC) ON [PS_Date] ([Date Key]),
    CONSTRAINT [FK_Fact_Transaction_Bill_To_Customer_Key_Dimension_Customer] FOREIGN KEY ([Bill To Customer Key]) REFERENCES [Dimension].[Customer] ([Customer Key]),
    CONSTRAINT [FK_Fact_Transaction_Customer_Key_Dimension_Customer] FOREIGN KEY ([Customer Key]) REFERENCES [Dimension].[Customer] ([Customer Key]),
    CONSTRAINT [FK_Fact_Transaction_Date_Key_Dimension_Date] FOREIGN KEY ([Date Key]) REFERENCES [Dimension].[Date] ([Date]),
    CONSTRAINT [FK_Fact_Transaction_Payment_Method_Key_Dimension_Payment Method] FOREIGN KEY ([Payment Method Key]) REFERENCES [Dimension].[Payment Method] ([Payment Method Key]),
    CONSTRAINT [FK_Fact_Transaction_Supplier_Key_Dimension_Supplier] FOREIGN KEY ([Supplier Key]) REFERENCES [Dimension].[Supplier] ([Supplier Key]),
    CONSTRAINT [FK_Fact_Transaction_Transaction_Type_Key_Dimension_Transaction Type] FOREIGN KEY ([Transaction Type Key]) REFERENCES [Dimension].[Transaction Type] ([Transaction Type Key])
);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Transaction_Bill_To_Customer_Key]
    ON [Fact].[Transaction]([Bill To Customer Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Transaction_Customer_Key]
    ON [Fact].[Transaction]([Customer Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Transaction_Date_Key]
    ON [Fact].[Transaction]([Date Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Transaction_Payment_Method_Key]
    ON [Fact].[Transaction]([Payment Method Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Transaction_Supplier_Key]
    ON [Fact].[Transaction]([Supplier Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Transaction_Transaction_Ty
```