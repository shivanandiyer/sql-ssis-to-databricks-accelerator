-- Source: OLTP:Sales.CustomerTransactions  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Sales/Tables/CustomerTransactions.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.sales__customertransactions (
    CustomerTransactionID INT NOT NULL,
    CustomerID INT NOT NULL,
    TransactionTypeID INT NOT NULL,
    InvoiceID INT,
    PaymentMethodID INT,
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
COMMENT 'Converted from OLTP:Sales.CustomerTransactions'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `CustomerTransactionID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta
-- `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline
-- (see target_state_architecture.md, Unity Catalog section).
-- Column `IsFinalized` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_CustomerTransactions_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[Peo
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_CustomerTransactions_CustomerID_Sales_Customers] FOREIGN KEY ([CustomerID]) REFERENCES
-- [Sales].[Cus
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_CustomerTransactions_InvoiceID_Sales_Invoices] FOREIGN KEY ([InvoiceID]) REFERENCES
-- [Sales].[Invoic
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_CustomerTransactions_PaymentMethodID_Application_PaymentMethods] FOREIGN KEY
-- ([PaymentMethodID]) RE
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_CustomerTransactions_TransactionTypeID_Application_TransactionTypes] FOREIGN KEY
-- ([TransactionTypeI