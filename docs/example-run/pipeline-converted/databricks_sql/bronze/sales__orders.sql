-- Source: OLTP:Sales.Orders  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Sales/Tables/Orders.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.sales__orders (
    OrderID INT NOT NULL,
    CustomerID INT NOT NULL,
    SalespersonPersonID INT NOT NULL,
    PickedByPersonID INT,
    ContactPersonID INT NOT NULL,
    BackorderOrderID INT,
    OrderDate DATE NOT NULL,
    ExpectedDeliveryDate DATE NOT NULL,
    CustomerPurchaseOrderNumber STRING,
    IsUndersupplyBackordered BOOLEAN NOT NULL,
    Comments STRING,
    DeliveryInstructions STRING,
    InternalComments STRING,
    PickingCompletedWhen TIMESTAMP,
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Sales.Orders'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `OrderID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS
-- AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Orders_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People]
-- ([PersonI
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Orders_BackorderOrderID_Sales_Orders] FOREIGN KEY ([BackorderOrderID]) REFERENCES
-- [Sales].[Orders]
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Orders_ContactPersonID_Application_People] FOREIGN KEY ([ContactPersonID]) REFERENCES
-- [Application]
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Orders_CustomerID_Sales_Customers] FOREIGN KEY ([CustomerID]) REFERENCES
-- [Sales].[Customers] ([Cust
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Orders_PickedByPersonID_Application_People] FOREIGN KEY ([PickedByPersonID]) REFERENCES
-- [Applicatio
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Orders_SalespersonPersonID_Application_People] FOREIGN KEY ([SalespersonPersonID])
-- REFERENCES [Appl