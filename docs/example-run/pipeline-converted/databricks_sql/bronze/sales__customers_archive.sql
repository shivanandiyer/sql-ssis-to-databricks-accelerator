-- Source: OLTP:Sales.Customers_Archive  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Sales/Tables/Customers_Archive.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.sales__customers_archive (
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
    LastEditedBy INT NOT NULL,
    ValidFrom TIMESTAMP NOT NULL,
    ValidTo TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Sales.Customers_Archive'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `DeliveryLocation` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake.
-- Recommend storing as WKT STRING and adding an H3 index column, or adopting a geospatial library
-- (Databricks Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.