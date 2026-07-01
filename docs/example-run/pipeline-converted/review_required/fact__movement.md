# Review Required: DW:Fact.Movement

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Fact/Tables/Movement.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `Movement` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Movement` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Transaction` (Type -> STRING): Unrecognised SQL Server type 'Type' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Purchase -> STRING): Unrecognised SQL Server type 'Purchase' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Movement_Customer_Key_Dimension_Customer] FOREIGN KEY ([Customer Key]) REFERENCES [Dimension].[Custo
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Movement_Date_Key_Dimension_Date] FOREIGN KEY ([Date Key]) REFERENCES [Dimension].[Date] ([Date])
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Movement_Stock_Item_Key_Dimension_Stock Item] FOREIGN KEY ([Stock Item Key]) REFERENCES [Dimension].
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Movement_Supplier_Key_Dimension_Supplier] FOREIGN KEY ([Supplier Key]) REFERENCES [Dimension].[Suppl
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Movement_Transaction_Type_Key_Dimension_Transaction Type] FOREIGN KEY ([Transaction Type Key]) REFER

## Source DDL (for reference)

```sql
CREATE TABLE [Fact].[Movement] (
    [Movement Key]                  BIGINT IDENTITY (1, 1) NOT NULL,
    [Date Key]                      DATE   NOT NULL,
    [Stock Item Key]                INT    NOT NULL,
    [Customer Key]                  INT    NULL,
    [Supplier Key]                  INT    NULL,
    [Transaction Type Key]          INT    NOT NULL,
    [WWI Stock Item Transaction ID] INT    NOT NULL,
    [WWI Invoice ID]                INT    NULL,
    [WWI Purchase Order ID]         INT    NULL,
    [Quantity]                      INT    NOT NULL,
    [Lineage Key]                   INT    NOT NULL,
    CONSTRAINT [PK_Fact_Movement] PRIMARY KEY NONCLUSTERED ([Movement Key] ASC, [Date Key] ASC) ON [PS_Date] ([Date Key]),
    CONSTRAINT [FK_Fact_Movement_Customer_Key_Dimension_Customer] FOREIGN KEY ([Customer Key]) REFERENCES [Dimension].[Customer] ([Customer Key]),
    CONSTRAINT [FK_Fact_Movement_Date_Key_Dimension_Date] FOREIGN KEY ([Date Key]) REFERENCES [Dimension].[Date] ([Date]),
    CONSTRAINT [FK_Fact_Movement_Stock_Item_Key_Dimension_Stock Item] FOREIGN KEY ([Stock Item Key]) REFERENCES [Dimension].[Stock Item] ([Stock Item Key]),
    CONSTRAINT [FK_Fact_Movement_Supplier_Key_Dimension_Supplier] FOREIGN KEY ([Supplier Key]) REFERENCES [Dimension].[Supplier] ([Supplier Key]),
    CONSTRAINT [FK_Fact_Movement_Transaction_Type_Key_Dimension_Transaction Type] FOREIGN KEY ([Transaction Type Key]) REFERENCES [Dimension].[Transaction Type] ([Transaction Type Key])
);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Movement_Customer_Key]
    ON [Fact].[Movement]([Customer Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Movement_Date_Key]
    ON [Fact].[Movement]([Date Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Movement_Stock_Item_Key]
    ON [Fact].[Movement]([Stock Item Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Movement_Supplier_Key]
    ON [Fact].[Movement]([Supplier Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Movement_Transaction_Type_Key]
    ON [Fact].[Movement]([Transaction Type Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [IX_Integration_Movement_WWI_Stock_Item_Transaction_ID]
    ON [Fact].[Movement]([WWI Stock Item Transaction ID] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE CLUSTERED COLUMNSTORE INDEX [CCX_Fact_Movement]
    ON [Fact].[Movement]
    ON [PS_Date] ([Date Key]);


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'Movement fact table (movements of stock items)', @level0type = N'SCHEMA', @level0name = N'Fact', @level1type = N'TABLE', @level1name = N'Movement';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'DW key for a row in the Movement fact', @level0type = N'SCHEMA', @level0name = N'Fact', @level1type = N'TABLE', @level1name = N'Movement', @level2type = N'COLUMN', @level2name = N'Movement Key';


GO
EXECUT
```