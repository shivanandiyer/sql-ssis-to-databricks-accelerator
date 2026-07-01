-- Source: OLTP:Warehouse.StockItemHoldings  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Warehouse/Tables/StockItemHoldings.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.warehouse__stockitemholdings (
    StockItemID INT NOT NULL,
    QuantityOnHand INT NOT NULL,
    BinLocation STRING NOT NULL,
    LastStocktakeQuantity INT NOT NULL,
    LastCostPrice DECIMAL(18,2) NOT NULL,
    ReorderLevel INT NOT NULL,
    TargetStockLevel INT NOT NULL,
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Warehouse.StockItemHoldings'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItemHoldings_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[Pe
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [PKFK_Warehouse_StockItemHoldings_StockItemID_Warehouse_StockItems] FOREIGN KEY ([StockItemID])
-- REFERENCES [W