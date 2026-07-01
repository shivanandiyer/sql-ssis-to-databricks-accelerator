# Review Required: DW:Fact.Order

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Fact/Tables/Order.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `Order` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
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
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Order_City_Key_Dimension_City] FOREIGN KEY ([City Key]) REFERENCES [Dimension].[City] ([City Key])
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Order_Customer_Key_Dimension_Customer] FOREIGN KEY ([Customer Key]) REFERENCES [Dimension].[Customer
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Order_Order_Date_Key_Dimension_Date] FOREIGN KEY ([Order Date Key]) REFERENCES [Dimension].[Date] ([
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Order_Picked_Date_Key_Dimension_Date] FOREIGN KEY ([Picked Date Key]) REFERENCES [Dimension].[Date] 
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Order_Picker_Key_Dimension_Employee] FOREIGN KEY ([Picker Key]) REFERENCES [Dimension].[Employee] ([
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Order_Salesperson_Key_Dimension_Employee] FOREIGN KEY ([Salesperson Key]) REFERENCES [Dimension].[Em
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Order_Stock_Item_Key_Dimension_Stock Item] FOREIGN KEY ([Stock Item Key]) REFERENCES [Dimension].[St

## Source DDL (for reference)

```sql
CREATE TABLE [Fact].[Order] (
    [Order Key]           BIGINT          IDENTITY (1, 1) NOT NULL,
    [City Key]            INT             NOT NULL,
    [Customer Key]        INT             NOT NULL,
    [Stock Item Key]      INT             NOT NULL,
    [Order Date Key]      DATE            NOT NULL,
    [Picked Date Key]     DATE            NULL,
    [Salesperson Key]     INT             NOT NULL,
    [Picker Key]          INT             NULL,
    [WWI Order ID]        INT             NOT NULL,
    [WWI Backorder ID]    INT             NULL,
    [Description]         NVARCHAR (100)  NOT NULL,
    [Package]             NVARCHAR (50)   NOT NULL,
    [Quantity]            INT             NOT NULL,
    [Unit Price]          DECIMAL (18, 2) NOT NULL,
    [Tax Rate]            DECIMAL (18, 3) NOT NULL,
    [Total Excluding Tax] DECIMAL (18, 2) NOT NULL,
    [Tax Amount]          DECIMAL (18, 2) NOT NULL,
    [Total Including Tax] DECIMAL (18, 2) NOT NULL,
    [Lineage Key]         INT             NOT NULL,
    CONSTRAINT [PK_Fact_Order] PRIMARY KEY NONCLUSTERED ([Order Key] ASC, [Order Date Key] ASC) ON [PS_Date] ([Order Date Key]),
    CONSTRAINT [FK_Fact_Order_City_Key_Dimension_City] FOREIGN KEY ([City Key]) REFERENCES [Dimension].[City] ([City Key]),
    CONSTRAINT [FK_Fact_Order_Customer_Key_Dimension_Customer] FOREIGN KEY ([Customer Key]) REFERENCES [Dimension].[Customer] ([Customer Key]),
    CONSTRAINT [FK_Fact_Order_Order_Date_Key_Dimension_Date] FOREIGN KEY ([Order Date Key]) REFERENCES [Dimension].[Date] ([Date]),
    CONSTRAINT [FK_Fact_Order_Picked_Date_Key_Dimension_Date] FOREIGN KEY ([Picked Date Key]) REFERENCES [Dimension].[Date] ([Date]),
    CONSTRAINT [FK_Fact_Order_Picker_Key_Dimension_Employee] FOREIGN KEY ([Picker Key]) REFERENCES [Dimension].[Employee] ([Employee Key]),
    CONSTRAINT [FK_Fact_Order_Salesperson_Key_Dimension_Employee] FOREIGN KEY ([Salesperson Key]) REFERENCES [Dimension].[Employee] ([Employee Key]),
    CONSTRAINT [FK_Fact_Order_Stock_Item_Key_Dimension_Stock Item] FOREIGN KEY ([Stock Item Key]) REFERENCES [Dimension].[Stock Item] ([Stock Item Key])
);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Order_City_Key]
    ON [Fact].[Order]([City Key] ASC)
    ON [PS_Date] ([Order Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Order_Customer_Key]
    ON [Fact].[Order]([Customer Key] ASC)
    ON [PS_Date] ([Order Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Order_Order_Date_Key]
    ON [Fact].[Order]([Order Date Key] ASC)
    ON [PS_Date] ([Order Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Order_Picked_Date_Key]
    ON [Fact].[Order]([Picked Date Key] ASC)
    ON [PS_Date] ([Order Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Order_Picker_Key]
    ON [Fact].[Order]([Picker Key] ASC)
    ON [PS_Date] ([Order Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Order_Salesperson_Key]
    ON [Fact].[Order]([Salesperson Key] ASC)
    ON [PS_Date] ([Order Date Key]);


GO
CREATE NONCLUSTERED INDEX 
```