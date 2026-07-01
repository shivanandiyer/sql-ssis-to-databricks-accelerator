-- Source: OLTP:Warehouse.StockItemStockGroups  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Warehouse/Tables/StockItemStockGroups.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.warehouse__stockitemstockgroups (
    StockItemStockGroupID INT NOT NULL,
    StockItemID INT NOT NULL,
    StockGroupID INT NOT NULL,
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Warehouse.StockItemStockGroups'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `StockItemStockGroupID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta
-- `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline
-- (see target_state_architecture.md, Unity Catalog section).
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItemStockGroups_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItemStockGroups_StockGroupID_Warehouse_StockGroups] FOREIGN KEY ([StockGroupID])
-- REFERENCE
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItemStockGroups_StockItemID_Warehouse_StockItems] FOREIGN KEY ([StockItemID])
-- REFERENCES [