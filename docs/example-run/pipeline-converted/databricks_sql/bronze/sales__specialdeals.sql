-- Source: OLTP:Sales.SpecialDeals  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Sales/Tables/SpecialDeals.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.sales__specialdeals (
    SpecialDealID INT NOT NULL,
    StockItemID INT,
    CustomerID INT,
    BuyingGroupID INT,
    CustomerCategoryID INT,
    StockGroupID INT,
    DealDescription STRING NOT NULL,
    StartDate DATE NOT NULL,
    EndDate DATE NOT NULL,
    DiscountAmount DECIMAL(18,2),
    DiscountPercentage DECIMAL(18,3),
    UnitPrice DECIMAL(18,2),
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Sales.SpecialDeals'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `SpecialDealID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_SpecialDeals_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[People] ([P
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_SpecialDeals_BuyingGroupID_Sales_BuyingGroups] FOREIGN KEY ([BuyingGroupID]) REFERENCES
-- [Sales].[Bu
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_SpecialDeals_CustomerCategoryID_Sales_CustomerCategories] FOREIGN KEY
-- ([CustomerCategoryID]) REFERE
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_SpecialDeals_CustomerID_Sales_Customers] FOREIGN KEY ([CustomerID]) REFERENCES
-- [Sales].[Customers]
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_SpecialDeals_StockGroupID_Warehouse_StockGroups] FOREIGN KEY ([StockGroupID]) REFERENCES
-- [Warehouse
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_SpecialDeals_StockItemID_Warehouse_StockItems] FOREIGN KEY ([StockItemID]) REFERENCES
-- [Warehouse].[