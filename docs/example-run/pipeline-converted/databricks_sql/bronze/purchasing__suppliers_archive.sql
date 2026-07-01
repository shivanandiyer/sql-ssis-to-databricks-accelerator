-- Source: OLTP:Purchasing.Suppliers_Archive  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Purchasing/Tables/Suppliers_Archive.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.purchasing__suppliers_archive (
    SupplierID INT NOT NULL,
    SupplierName STRING NOT NULL,
    SupplierCategoryID INT NOT NULL,
    PrimaryContactPersonID INT NOT NULL,
    AlternateContactPersonID INT NOT NULL,
    DeliveryMethodID INT,
    DeliveryCityID INT NOT NULL,
    PostalCityID INT NOT NULL,
    SupplierReference STRING,
    BankAccountName STRING,
    BankAccountBranch STRING,
    BankAccountCode STRING,
    BankAccountNumber STRING,
    BankInternationalCode STRING,
    PaymentDays INT NOT NULL,
    InternalComments STRING,
    PhoneNumber STRING NOT NULL,
    FaxNumber STRING NOT NULL,
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
COMMENT 'Converted from OLTP:Purchasing.Suppliers_Archive'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `DeliveryLocation` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake.
-- Recommend storing as WKT STRING and adding an H3 index column, or adopting a geospatial library
-- (Databricks Mosaic / Apache Sedona) for spatial predicates. MANUAL REVIEW REQUIRED.