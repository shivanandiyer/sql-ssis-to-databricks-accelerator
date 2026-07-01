-- Source: OLTP:Purchasing.PurchaseOrderLines  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Purchasing/Tables/PurchaseOrderLines.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.purchasing__purchaseorderlines (
    PurchaseOrderLineID INT NOT NULL,
    PurchaseOrderID INT NOT NULL,
    StockItemID INT NOT NULL,
    OrderedOuters INT NOT NULL,
    Description STRING NOT NULL,
    ReceivedOuters INT NOT NULL,
    PackageTypeID INT NOT NULL,
    ExpectedUnitPricePerOuter DECIMAL(18,2),
    LastReceiptDate DATE,
    IsOrderLineFinalized BOOLEAN NOT NULL,
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Purchasing.PurchaseOrderLines'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `PurchaseOrderLineID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta
-- `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline
-- (see target_state_architecture.md, Unity Catalog section).
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_PurchaseOrderLines_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_PurchaseOrderLines_PackageTypeID_Warehouse_PackageTypes] FOREIGN KEY
-- ([PackageTypeID]) REFEREN
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_PurchaseOrderLines_PurchaseOrderID_Purchasing_PurchaseOrders] FOREIGN KEY
-- ([PurchaseOrderID])
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_PurchaseOrderLines_StockItemID_Warehouse_StockItems] FOREIGN KEY ([StockItemID])
-- REFERENCES [W