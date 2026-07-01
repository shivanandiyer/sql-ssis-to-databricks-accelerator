# Review Required: DW:Fact.Sale

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Fact/Tables/Sale.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `Sale` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Sale` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `City` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Bill` (To -> STRING): Unrecognised SQL Server type 'To' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Salesperson` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Unit` (Price] -> STRING): Unrecognised SQL Server type 'Price]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Tax` (Rate] -> STRING): Unrecognised SQL Server type 'Rate]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Total` (Excluding -> STRING): Unrecognised SQL Server type 'Excluding' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Tax` (Amount] -> STRING): Unrecognised SQL Server type 'Amount]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Total` (Including -> STRING): Unrecognised SQL Server type 'Including' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Total` (Dry -> STRING): Unrecognised SQL Server type 'Dry' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Total` (Chiller -> STRING): Unrecognised SQL Server type 'Chiller' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Sale_Bill_To_Customer_Key_Dimension_Customer] FOREIGN KEY ([Bill To Customer Key]) REFERENCES [Dimen
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Sale_City_Key_Dimension_City] FOREIGN KEY ([City Key]) REFERENCES [Dimension].[City] ([City Key])
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Sale_Customer_Key_Dimension_Customer] FOREIGN KEY ([Customer Key]) REFERENCES [Dimension].[Customer]
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Sale_Delivery_Date_Key_Dimension_Date] FOREIGN KEY ([Delivery Date Key]) REFERENCES [Dimension].[Dat
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Sale_Invoice_Date_Key_Dimension_Date] FOREIGN KEY ([Invoice Date Key]) REFERENCES [Dimension].[Date]
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Sale_Salesperson_Key_Dimension_Employee] FOREIGN KEY ([Salesperson Key]) REFERENCES [Dimension].[Emp
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Sale_Stock_Item_Key_Dimension_Stock Item] FOREIGN KEY ([Stock Item Key]) REFERENCES [Dimension].[Sto

## Source DDL (for reference)

```sql
CREATE TABLE [Fact].[Sale] (
    [Sale Key]             BIGINT          IDENTITY (1, 1) NOT NULL,
    [City Key]             INT             NOT NULL,
    [Customer Key]         INT             NOT NULL,
    [Bill To Customer Key] INT             NOT NULL,
    [Stock Item Key]       INT             NOT NULL,
    [Invoice Date Key]     DATE            NOT NULL,
    [Delivery Date Key]    DATE            NULL,
    [Salesperson Key]      INT             NOT NULL,
    [WWI Invoice ID]       INT             NOT NULL,
    [Description]          NVARCHAR (100)  NOT NULL,
    [Package]              NVARCHAR (50)   NOT NULL,
    [Quantity]             INT             NOT NULL,
    [Unit Price]           DECIMAL (18, 2) NOT NULL,
    [Tax Rate]             DECIMAL (18, 3) NOT NULL,
    [Total Excluding Tax]  DECIMAL (18, 2) NOT NULL,
    [Tax Amount]           DECIMAL (18, 2) NOT NULL,
    [Profit]               DECIMAL (18, 2) NOT NULL,
    [Total Including Tax]  DECIMAL (18, 2) NOT NULL,
    [Total Dry Items]      INT             NOT NULL,
    [Total Chiller Items]  INT             NOT NULL,
    [Lineage Key]          INT             NOT NULL,
    CONSTRAINT [PK_Fact_Sale] PRIMARY KEY NONCLUSTERED ([Sale Key] ASC, [Invoice Date Key] ASC) ON [PS_Date] ([Invoice Date Key]),
    CONSTRAINT [FK_Fact_Sale_Bill_To_Customer_Key_Dimension_Customer] FOREIGN KEY ([Bill To Customer Key]) REFERENCES [Dimension].[Customer] ([Customer Key]),
    CONSTRAINT [FK_Fact_Sale_City_Key_Dimension_City] FOREIGN KEY ([City Key]) REFERENCES [Dimension].[City] ([City Key]),
    CONSTRAINT [FK_Fact_Sale_Customer_Key_Dimension_Customer] FOREIGN KEY ([Customer Key]) REFERENCES [Dimension].[Customer] ([Customer Key]),
    CONSTRAINT [FK_Fact_Sale_Delivery_Date_Key_Dimension_Date] FOREIGN KEY ([Delivery Date Key]) REFERENCES [Dimension].[Date] ([Date]),
    CONSTRAINT [FK_Fact_Sale_Invoice_Date_Key_Dimension_Date] FOREIGN KEY ([Invoice Date Key]) REFERENCES [Dimension].[Date] ([Date]),
    CONSTRAINT [FK_Fact_Sale_Salesperson_Key_Dimension_Employee] FOREIGN KEY ([Salesperson Key]) REFERENCES [Dimension].[Employee] ([Employee Key]),
    CONSTRAINT [FK_Fact_Sale_Stock_Item_Key_Dimension_Stock Item] FOREIGN KEY ([Stock Item Key]) REFERENCES [Dimension].[Stock Item] ([Stock Item Key])
);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Sale_Bill_To_Customer_Key]
    ON [Fact].[Sale]([Bill To Customer Key] ASC)
    ON [PS_Date] ([Invoice Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Sale_City_Key]
    ON [Fact].[Sale]([City Key] ASC)
    ON [PS_Date] ([Invoice Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Sale_Customer_Key]
    ON [Fact].[Sale]([Customer Key] ASC)
    ON [PS_Date] ([Invoice Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Sale_Delivery_Date_Key]
    ON [Fact].[Sale]([Delivery Date Key] ASC)
    ON [PS_Date] ([Invoice Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Sale_Invoice_Date_Key]
    ON [Fact].[Sale]([Invoice Date Key] ASC)
    ON [PS_Date] ([Invoice Date 
```