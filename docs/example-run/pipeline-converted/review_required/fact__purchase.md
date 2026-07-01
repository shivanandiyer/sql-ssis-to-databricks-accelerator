# Review Required: DW:Fact.Purchase

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Fact/Tables/Purchase.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `Purchase` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Purchase` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `WWI` (Purchase -> STRING): Unrecognised SQL Server type 'Purchase' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Ordered` (Outers] -> STRING): Unrecognised SQL Server type 'Outers]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Ordered` (Quantity] -> STRING): Unrecognised SQL Server type 'Quantity]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Received` (Outers] -> STRING): Unrecognised SQL Server type 'Outers]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Is` (Order -> STRING): Unrecognised SQL Server type 'Order' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Purchase_Date_Key_Dimension_Date] FOREIGN KEY ([Date Key]) REFERENCES [Dimension].[Date] ([Date])
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Purchase_Stock_Item_Key_Dimension_Stock Item] FOREIGN KEY ([Stock Item Key]) REFERENCES [Dimension].
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Fact_Purchase_Supplier_Key_Dimension_Supplier] FOREIGN KEY ([Supplier Key]) REFERENCES [Dimension].[Suppl

## Source DDL (for reference)

```sql
CREATE TABLE [Fact].[Purchase] (
    [Purchase Key]          BIGINT        IDENTITY (1, 1) NOT NULL,
    [Date Key]              DATE          NOT NULL,
    [Supplier Key]          INT           NOT NULL,
    [Stock Item Key]        INT           NOT NULL,
    [WWI Purchase Order ID] INT           NULL,
    [Ordered Outers]        INT           NOT NULL,
    [Ordered Quantity]      INT           NOT NULL,
    [Received Outers]       INT           NOT NULL,
    [Package]               NVARCHAR (50) NOT NULL,
    [Is Order Finalized]    BIT           NOT NULL,
    [Lineage Key]           INT           NOT NULL,
    CONSTRAINT [PK_Fact_Purchase] PRIMARY KEY NONCLUSTERED ([Purchase Key] ASC, [Date Key] ASC) ON [PS_Date] ([Date Key]),
    CONSTRAINT [FK_Fact_Purchase_Date_Key_Dimension_Date] FOREIGN KEY ([Date Key]) REFERENCES [Dimension].[Date] ([Date]),
    CONSTRAINT [FK_Fact_Purchase_Stock_Item_Key_Dimension_Stock Item] FOREIGN KEY ([Stock Item Key]) REFERENCES [Dimension].[Stock Item] ([Stock Item Key]),
    CONSTRAINT [FK_Fact_Purchase_Supplier_Key_Dimension_Supplier] FOREIGN KEY ([Supplier Key]) REFERENCES [Dimension].[Supplier] ([Supplier Key])
);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Purchase_Date_Key]
    ON [Fact].[Purchase]([Date Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Purchase_Stock_Item_Key]
    ON [Fact].[Purchase]([Stock Item Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE NONCLUSTERED INDEX [FK_Fact_Purchase_Supplier_Key]
    ON [Fact].[Purchase]([Supplier Key] ASC)
    ON [PS_Date] ([Date Key]);


GO
CREATE CLUSTERED COLUMNSTORE INDEX [CCX_Fact_Purchase]
    ON [Fact].[Purchase]
    ON [PS_Date] ([Date Key]);


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'Purchase fact table (stock purchases from suppliers)', @level0type = N'SCHEMA', @level0name = N'Fact', @level1type = N'TABLE', @level1name = N'Purchase';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'DW key for a row in the Purchase fact', @level0type = N'SCHEMA', @level0name = N'Fact', @level1type = N'TABLE', @level1name = N'Purchase', @level2type = N'COLUMN', @level2name = N'Purchase Key';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Purchase order date', @level0type = N'SCHEMA', @level0name = N'Fact', @level1type = N'TABLE', @level1name = N'Purchase', @level2type = N'COLUMN', @level2name = N'Date Key';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Supplier for this purchase order', @level0type = N'SCHEMA', @level0name = N'Fact', @level1type = N'TABLE', @level1name = N'Purchase', @level2type = N'COLUMN', @level2name = N'Supplier Key';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Stock item for this purchase order', @level0type = N'SCHEMA', @level0name = N'Fact', @level1type = N'TABLE', @level1name = N'Purchase', @level2type = N'COLUMN', @level2name = N'Stock Item Key';


GO
EXECUTE sp_addextendedproperty @name = N
```