-- Source: OLTP:Sales.Customers  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Sales/Tables/Customers.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.sales__customers (
    CustomerID INT NOT NULL,
    CustomerName STRING NOT NULL,
    BillToCustomerID INT NOT NULL,
    CustomerCategoryID INT NOT NULL,
    BuyingGroupID INT,
    PrimaryContactPersonID INT NOT NULL,
    AlternateContactPersonID INT,
    DeliveryMethodID INT NOT NULL,
    DeliveryCityID INT NOT NULL,
    PostalCityID INT NOT NULL,
    CreditLimit DECIMAL(18,2),
    AccountOpenedDate DATE NOT NULL,
    StandardDiscountPercentage DECIMAL(18,3) NOT NULL,
    IsStatementSent BOOLEAN NOT NULL,
    IsOnCreditHold BOOLEAN NOT NULL,
    PaymentDays INT NOT NULL,
    PhoneNumber STRING NOT NULL,
    FaxNumber STRING NOT NULL,
    DeliveryRun STRING,
    RunPosition STRING,
    WebsiteURL STRING NOT NULL,
    DeliveryAddressLine1 STRING NOT NULL,
    DeliveryAddressLine2 STRING,
    DeliveryPostalCode STRING NOT NULL,
    DeliveryLocation STRING COMMENT 'source type: [sys].[geography]',
    PostalAddressLine1 STRING NOT NULL,
    PostalAddressLine2 STRING,
    PostalPostalCode STRING NOT NULL,
    LastEditedBy INT NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Sales.Customers'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `CustomerID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `DeliveryLocation` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake.
-- Recommend storing as WKT STRING and adding an H3 index column, or adopting a geospatial library
-- (Databricks Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.
-- Column `ValidFrom` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW
-- START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT
-- equivalent to this column's semantics — Time Travel returns the whole table's state at a commit,
-- while this column tracks each row's own validity window independent of write/commit history. Any
-- query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter
-- (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present
-- ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
-- Column `ValidTo` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END)
-- — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to
-- this column's semantics — Time Travel returns the whole table's state at a commit, while this column
-- tracks each row's own validity window independent of write/commit history. Any query that did `...
-- FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from
-- <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo
-- columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Customers_AlternateContactPersonID_Application_People] FOREIGN KEY
-- ([AlternateContactPersonID]) REF
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Customers_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[People] ([Pers
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Customers_BillToCustomerID_Sales_Customers] FOREIGN KEY ([BillToCustomerID]) REFERENCES
-- [Sales].[Cu
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Customers_BuyingGroupID_Sales_BuyingGroups] FOREIGN KEY ([BuyingGroupID]) REFERENCES
-- [Sales].[Buyin
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Customers_CustomerCategoryID_Sales_CustomerCategories] FOREIGN KEY ([CustomerCategoryID])
-- REFERENCE
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Customers_DeliveryCityID_Application_Cities] FOREIGN KEY ([DeliveryCityID]) REFERENCES
-- [Application
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Customers_DeliveryMethodID_Application_DeliveryMethods] FOREIGN KEY ([DeliveryMethodID])
-- REFERENCES
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Customers_PostalCityID_Application_Cities] FOREIGN KEY ([PostalCityID]) REFERENCES
-- [Application].[C
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Customers_PrimaryContactPersonID_Application_People] FOREIGN KEY
-- ([PrimaryContactPersonID]) REFEREN
-- Source table used SQL Server temporal tables (FOR SYSTEM_TIME / paired _Archive table). Recommended
-- replacement: enable `delta.enableChangeDataFeed` and query history via `TIMESTAMP AS OF` / `VERSION
-- AS OF`, or `table_changes()`. The paired _Archive table is converted separately and should be
-- reconciled with this table's Delta history rather than kept as a second physical table long-term.