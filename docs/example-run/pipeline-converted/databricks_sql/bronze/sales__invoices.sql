-- Source: OLTP:Sales.Invoices  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Sales/Tables/Invoices.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.sales__invoices (
    InvoiceID INT NOT NULL,
    CustomerID INT NOT NULL,
    BillToCustomerID INT NOT NULL,
    OrderID INT,
    DeliveryMethodID INT NOT NULL,
    ContactPersonID INT NOT NULL,
    AccountsPersonID INT NOT NULL,
    SalespersonPersonID INT NOT NULL,
    PackedByPersonID INT NOT NULL,
    InvoiceDate DATE NOT NULL,
    CustomerPurchaseOrderNumber STRING,
    IsCreditNote BOOLEAN NOT NULL,
    CreditNoteReason STRING,
    Comments STRING,
    DeliveryInstructions STRING,
    InternalComments STRING,
    TotalDryItems INT NOT NULL,
    TotalChillerItems INT NOT NULL,
    DeliveryRun STRING,
    RunPosition STRING,
    ReturnedDeliveryData STRING,
    ConfirmedDeliveryTime STRING COMMENT 'source type: AS',
    ConfirmedReceivedBy STRING COMMENT 'source type: AS',
    LastEditedBy INT NOT NULL,
    LastEditedWhen TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Sales.Invoices'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `InvoiceID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `ConfirmedDeliveryTime` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `ConfirmedReceivedBy` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Invoices_AccountsPersonID_Application_People] FOREIGN KEY ([AccountsPersonID]) REFERENCES
-- [Applicat
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Invoices_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[People] ([Perso
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Invoices_BillToCustomerID_Sales_Customers] FOREIGN KEY ([BillToCustomerID]) REFERENCES
-- [Sales].[Cus
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Invoices_ContactPersonID_Application_People] FOREIGN KEY ([ContactPersonID]) REFERENCES
-- [Applicatio
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Invoices_CustomerID_Sales_Customers] FOREIGN KEY ([CustomerID]) REFERENCES
-- [Sales].[Customers] ([Cu
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Invoices_DeliveryMethodID_Application_DeliveryMethods] FOREIGN KEY ([DeliveryMethodID])
-- REFERENCES
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Invoices_OrderID_Sales_Orders] FOREIGN KEY ([OrderID]) REFERENCES [Sales].[Orders]
-- ([OrderID])
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Invoices_PackedByPersonID_Application_People] FOREIGN KEY ([PackedByPersonID]) REFERENCES
-- [Applicat
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Sales_Invoices_SalespersonPersonID_Application_People] FOREIGN KEY ([SalespersonPersonID])
-- REFERENCES [Ap