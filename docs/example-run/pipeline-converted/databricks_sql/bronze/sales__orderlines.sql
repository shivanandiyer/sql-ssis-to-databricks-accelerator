-- Source: OLTP:Sales.OrderLines  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Sales/Tables/OrderLines.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.sales__orderlines (
    OrderLineID INT NOT NULL,
    OrderID INT NOT NULL,
    StockItemID INT NOT NULL,
    Description STRING NOT NULL,
    PackageTypeID INT NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(18,2),
    TaxRate DECIMAL(18,3) NOT NULL,
    PickedQuantity INT NOT NULL,
    PickingCompletedWhen TIMESTAMP,
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Sales.OrderLines'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `OrderLineID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_OrderLines_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[People] ([Per
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_OrderLines_OrderID_Sales_Orders] FOREIGN KEY ([OrderID]) REFERENCES [Sales].[Orders]
-- ([OrderID])
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_OrderLines_PackageTypeID_Warehouse_PackageTypes] FOREIGN KEY ([PackageTypeID]) REFERENCES
-- [Warehous
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_OrderLines_StockItemID_Warehouse_StockItems] FOREIGN KEY ([StockItemID]) REFERENCES
-- [Warehouse].[St