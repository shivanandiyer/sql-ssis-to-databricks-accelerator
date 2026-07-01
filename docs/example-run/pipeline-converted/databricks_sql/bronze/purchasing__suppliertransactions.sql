-- Source: OLTP:Purchasing.SupplierTransactions  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Purchasing/Tables/SupplierTransactions.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.purchasing__suppliertransactions (
    SupplierTransactionID INT NOT NULL,
    SupplierID INT NOT NULL,
    TransactionTypeID INT NOT NULL,
    PurchaseOrderID INT,
    PaymentMethodID INT,
    SupplierInvoiceNumber STRING,
    TransactionDate DATE NOT NULL,
    AmountExcludingTax DECIMAL(18,2) NOT NULL,
    TaxAmount DECIMAL(18,2) NOT NULL,
    TransactionAmount DECIMAL(18,2) NOT NULL,
    OutstandingBalance DECIMAL(18,2) NOT NULL,
    FinalizationDate DATE,
    IsFinalized STRING COMMENT 'source type: AS',
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
-- TODO: confirm partition column from source PARTITION SCHEME before enabling:
-- PARTITIONED BY (<date_or_period_column>)
COMMENT 'Converted from OLTP:Purchasing.SupplierTransactions'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `SupplierTransactionID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta
-- `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline
-- (see target_state_architecture.md, Unity Catalog section).
-- Column `IsFinalized` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_SupplierTransactions_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application]
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_SupplierTransactions_PaymentMethodID_Application_PaymentMethods] FOREIGN KEY
-- ([PaymentMethodID
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_SupplierTransactions_PurchaseOrderID_Purchasing_PurchaseOrders] FOREIGN KEY
-- ([PurchaseOrderID]
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_SupplierTransactions_SupplierID_Purchasing_Suppliers] FOREIGN KEY ([SupplierID])
-- REFERENCES [P
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Purchasing_SupplierTransactions_TransactionTypeID_Application_TransactionTypes] FOREIGN KEY
-- ([Transaction