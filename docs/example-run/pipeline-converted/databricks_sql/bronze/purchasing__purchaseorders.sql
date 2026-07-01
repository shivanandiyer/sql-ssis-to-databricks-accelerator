-- Source: OLTP:Purchasing.PurchaseOrders  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Purchasing/Tables/PurchaseOrders.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.purchasing__purchaseorders (
    PurchaseOrderID INT NOT NULL,
    SupplierID INT NOT NULL,
    OrderDate DATE NOT NULL,
    DeliveryMethodID INT NOT NULL,
    ContactPersonID INT NOT NULL,
    ExpectedDeliveryDate DATE,
    SupplierReference STRING,
    IsOrderFinalized BOOLEAN NOT NULL,
    Comments STRING,
    InternalComments STRING,
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Purchasing.PurchaseOrders'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `PurchaseOrderID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta
-- `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline
-- (see target_state_architecture.md, Unity Catalog section).
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_PurchaseOrders_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[Peop
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_PurchaseOrders_ContactPersonID_Application_People] FOREIGN KEY ([ContactPersonID])
-- REFERENCES
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_PurchaseOrders_DeliveryMethodID_Application_DeliveryMethods] FOREIGN KEY
-- ([DeliveryMethodID])
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_PurchaseOrders_SupplierID_Purchasing_Suppliers] FOREIGN KEY ([SupplierID]) REFERENCES
-- [Purchas