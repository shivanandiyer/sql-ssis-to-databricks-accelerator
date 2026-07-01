-- Source: OLTP:Sales.InvoiceLines  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Sales/Tables/InvoiceLines.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.sales__invoicelines (
    InvoiceLineID INT NOT NULL,
    InvoiceID INT NOT NULL,
    StockItemID INT NOT NULL,
    Description STRING NOT NULL,
    PackageTypeID INT NOT NULL,
    Quantity INT NOT NULL,
    UnitPrice DECIMAL(18,2),
    TaxRate DECIMAL(18,3) NOT NULL,
    TaxAmount DECIMAL(18,2) NOT NULL,
    LineProfit DECIMAL(18,2) NOT NULL,
    ExtendedPrice DECIMAL(18,2) NOT NULL,
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Sales.InvoiceLines'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `InvoiceLineID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_InvoiceLines_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[People] ([P
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_InvoiceLines_InvoiceID_Sales_Invoices] FOREIGN KEY ([InvoiceID]) REFERENCES
-- [Sales].[Invoices] ([In
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_InvoiceLines_PackageTypeID_Warehouse_PackageTypes] FOREIGN KEY ([PackageTypeID])
-- REFERENCES [Wareho
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_InvoiceLines_StockItemID_Warehouse_StockItems] FOREIGN KEY ([StockItemID]) REFERENCES
-- [Warehouse].[