-- Source: OLTP:Warehouse.StockItems_Archive  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Warehouse/Tables/StockItems_Archive.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.warehouse__stockitems_archive (
    StockItemID INT NOT NULL,
    StockItemName STRING NOT NULL,
    SupplierID INT NOT NULL,
    ColorID INT,
    UnitPackageID INT NOT NULL,
    OuterPackageID INT NOT NULL,
    Brand STRING,
    Size STRING,
    LeadTimeDays INT NOT NULL,
    QuantityPerOuter INT NOT NULL,
    IsChillerStock BOOLEAN NOT NULL,
    Barcode STRING,
    TaxRate DECIMAL(18,3) NOT NULL,
    UnitPrice DECIMAL(18,2) NOT NULL,
    RecommendedRetailPrice DECIMAL(18,2),
    TypicalWeightPerUnit DECIMAL(18,3) NOT NULL,
    MarketingComments STRING,
    InternalComments STRING,
    Photo BINARY,
    CustomFields STRING,
    Tags STRING,
    SearchDetails STRING NOT NULL,
    LastEditedBy INT NOT NULL,
    ValidFrom TIMESTAMP NOT NULL,
    ValidTo TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Warehouse.StockItems_Archive'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
