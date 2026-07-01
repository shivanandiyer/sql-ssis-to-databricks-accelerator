# Review Required: OLTP:Purchasing.SupplierTransactions

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Purchasing/Tables/SupplierTransactions.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- Column `SupplierTransactionID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `IsFinalized` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Purchasing_SupplierTransactions_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application]
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Purchasing_SupplierTransactions_PaymentMethodID_Application_PaymentMethods] FOREIGN KEY ([PaymentMethodID
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Purchasing_SupplierTransactions_PurchaseOrderID_Purchasing_PurchaseOrders] FOREIGN KEY ([PurchaseOrderID]
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Purchasing_SupplierTransactions_SupplierID_Purchasing_Suppliers] FOREIGN KEY ([SupplierID]) REFERENCES [P
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Purchasing_SupplierTransactions_TransactionTypeID_Application_TransactionTypes] FOREIGN KEY ([Transaction

## Source DDL (for reference)

```sql
CREATE TABLE [Purchasing].[SupplierTransactions] (
    [SupplierTransactionID] INT             CONSTRAINT [DF_Purchasing_SupplierTransactions_SupplierTransactionID] DEFAULT (NEXT VALUE FOR [Sequences].[TransactionID]) NOT NULL,
    [SupplierID]            INT             NOT NULL,
    [TransactionTypeID]     INT             NOT NULL,
    [PurchaseOrderID]       INT             NULL,
    [PaymentMethodID]       INT             NULL,
    [SupplierInvoiceNumber] NVARCHAR (20)   NULL,
    [TransactionDate]       DATE            NOT NULL,
    [AmountExcludingTax]    DECIMAL (18, 2) NOT NULL,
    [TaxAmount]             DECIMAL (18, 2) NOT NULL,
    [TransactionAmount]     DECIMAL (18, 2) NOT NULL,
    [OutstandingBalance]    DECIMAL (18, 2) NOT NULL,
    [FinalizationDate]      DATE            NULL,
    [IsFinalized]           AS              (case when [FinalizationDate] IS NULL then CONVERT([bit],(0)) else CONVERT([bit],(1)) end) PERSISTED,
    [LastEditedBy]          INT             NOT NULL,
    [LastEditedWhen]        DATETIME2 (7)   CONSTRAINT [DF_Purchasing_SupplierTransactions_LastEditedWhen] DEFAULT (sysdatetime()) NOT NULL,
    CONSTRAINT [PK_Purchasing_SupplierTransactions] PRIMARY KEY NONCLUSTERED ([SupplierTransactionID] ASC),
    CONSTRAINT [FK_Purchasing_SupplierTransactions_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([PersonID]),
    CONSTRAINT [FK_Purchasing_SupplierTransactions_PaymentMethodID_Application_PaymentMethods] FOREIGN KEY ([PaymentMethodID]) REFERENCES [Application].[PaymentMethods] ([PaymentMethodID]),
    CONSTRAINT [FK_Purchasing_SupplierTransactions_PurchaseOrderID_Purchasing_PurchaseOrders] FOREIGN KEY ([PurchaseOrderID]) REFERENCES [Purchasing].[PurchaseOrders] ([PurchaseOrderID]),
    CONSTRAINT [FK_Purchasing_SupplierTransactions_SupplierID_Purchasing_Suppliers] FOREIGN KEY ([SupplierID]) REFERENCES [Purchasing].[Suppliers] ([SupplierID]),
    CONSTRAINT [FK_Purchasing_SupplierTransactions_TransactionTypeID_Application_TransactionTypes] FOREIGN KEY ([TransactionTypeID]) REFERENCES [Application].[TransactionTypes] ([TransactionTypeID])
);


GO
CREATE CLUSTERED INDEX [CX_Purchasing_SupplierTransactions]
    ON [Purchasing].[SupplierTransactions]([TransactionDate] ASC)
    ON [PS_TransactionDate] ([TransactionDate]);


GO
CREATE NONCLUSTERED INDEX [FK_Purchasing_SupplierTransactions_SupplierID]
    ON [Purchasing].[SupplierTransactions]([SupplierID] ASC)
    ON [PS_TransactionDate] ([TransactionDate]);


GO
CREATE NONCLUSTERED INDEX [FK_Purchasing_SupplierTransactions_TransactionTypeID]
    ON [Purchasing].[SupplierTransactions]([TransactionTypeID] ASC)
    ON [PS_TransactionDate] ([TransactionDate]);


GO
CREATE NONCLUSTERED INDEX [FK_Purchasing_SupplierTransactions_PurchaseOrderID]
    ON [Purchasing].[SupplierTransactions]([PurchaseOrderID] ASC)
    ON [PS_TransactionDate] ([TransactionDate]);


GO
CREATE NONCLUSTERED INDEX [FK_Purchasing_SupplierTransactions_PaymentMethodID]
```