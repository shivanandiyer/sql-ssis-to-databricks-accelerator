-- Source: OLTP:Warehouse.StockItemTransactions  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Warehouse/Tables/StockItemTransactions.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.warehouse__stockitemtransactions (
    StockItemTransactionID INT NOT NULL,
    StockItemID INT NOT NULL,
    TransactionTypeID INT NOT NULL,
    CustomerID INT,
    InvoiceID INT,
    SupplierID INT,
    PurchaseOrderID INT,
    TransactionOccurredWhen TIMESTAMP NOT NULL,
    Quantity DECIMAL(18,3) NOT NULL,
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Warehouse.StockItemTransactions'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `StockItemTransactionID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta
-- `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline
-- (see target_state_architecture.md, Unity Catalog section).
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItemTransactions_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application]
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItemTransactions_CustomerID_Sales_Customers] FOREIGN KEY ([CustomerID])
-- REFERENCES [Sales]
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItemTransactions_InvoiceID_Sales_Invoices] FOREIGN KEY ([InvoiceID]) REFERENCES
-- [Sales].[I
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItemTransactions_PurchaseOrderID_Purchasing_PurchaseOrders] FOREIGN KEY
-- ([PurchaseOrderID]
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItemTransactions_StockItemID_Warehouse_StockItems] FOREIGN KEY ([StockItemID])
-- REFERENCES
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItemTransactions_SupplierID_Purchasing_Suppliers] FOREIGN KEY ([SupplierID])
-- REFERENCES [P
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItemTransactions_TransactionTypeID_Application_TransactionTypes] FOREIGN KEY
-- ([Transaction