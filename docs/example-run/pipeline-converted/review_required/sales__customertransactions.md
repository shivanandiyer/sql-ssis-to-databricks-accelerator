# Review Required: OLTP:Sales.CustomerTransactions

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Sales/Tables/CustomerTransactions.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `CustomerTransactionID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `IsFinalized` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_CustomerTransactions_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[Peo
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_CustomerTransactions_CustomerID_Sales_Customers] FOREIGN KEY ([CustomerID]) REFERENCES [Sales].[Cus
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_CustomerTransactions_InvoiceID_Sales_Invoices] FOREIGN KEY ([InvoiceID]) REFERENCES [Sales].[Invoic
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_CustomerTransactions_PaymentMethodID_Application_PaymentMethods] FOREIGN KEY ([PaymentMethodID]) RE
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_CustomerTransactions_TransactionTypeID_Application_TransactionTypes] FOREIGN KEY ([TransactionTypeI

## Source DDL (for reference)

```sql
CREATE TABLE [Sales].[CustomerTransactions] (
    [CustomerTransactionID] INT             CONSTRAINT [DF_Sales_CustomerTransactions_CustomerTransactionID] DEFAULT (NEXT VALUE FOR [Sequences].[TransactionID]) NOT NULL,
    [CustomerID]            INT             NOT NULL,
    [TransactionTypeID]     INT             NOT NULL,
    [InvoiceID]             INT             NULL,
    [PaymentMethodID]       INT             NULL,
    [TransactionDate]       DATE            NOT NULL,
    [AmountExcludingTax]    DECIMAL (18, 2) NOT NULL,
    [TaxAmount]             DECIMAL (18, 2) NOT NULL,
    [TransactionAmount]     DECIMAL (18, 2) NOT NULL,
    [OutstandingBalance]    DECIMAL (18, 2) NOT NULL,
    [FinalizationDate]      DATE            NULL,
    [IsFinalized]           AS              (case when [FinalizationDate] IS NULL then CONVERT([bit],(0)) else CONVERT([bit],(1)) end) PERSISTED,
    [LastEditedBy]          INT             NOT NULL,
    [LastEditedWhen]        DATETIME2 (7)   CONSTRAINT [DF_Sales_CustomerTransactions_LastEditedWhen] DEFAULT (sysdatetime()) NOT NULL,
    CONSTRAINT [PK_Sales_CustomerTransactions] PRIMARY KEY NONCLUSTERED ([CustomerTransactionID] ASC),
    CONSTRAINT [FK_Sales_CustomerTransactions_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([PersonID]),
    CONSTRAINT [FK_Sales_CustomerTransactions_CustomerID_Sales_Customers] FOREIGN KEY ([CustomerID]) REFERENCES [Sales].[Customers] ([CustomerID]),
    CONSTRAINT [FK_Sales_CustomerTransactions_InvoiceID_Sales_Invoices] FOREIGN KEY ([InvoiceID]) REFERENCES [Sales].[Invoices] ([InvoiceID]),
    CONSTRAINT [FK_Sales_CustomerTransactions_PaymentMethodID_Application_PaymentMethods] FOREIGN KEY ([PaymentMethodID]) REFERENCES [Application].[PaymentMethods] ([PaymentMethodID]),
    CONSTRAINT [FK_Sales_CustomerTransactions_TransactionTypeID_Application_TransactionTypes] FOREIGN KEY ([TransactionTypeID]) REFERENCES [Application].[TransactionTypes] ([TransactionTypeID])
);


GO
CREATE CLUSTERED INDEX [CX_Sales_CustomerTransactions]
    ON [Sales].[CustomerTransactions]([TransactionDate] ASC)
    ON [PS_TransactionDate] ([TransactionDate]);


GO
CREATE NONCLUSTERED INDEX [FK_Sales_CustomerTransactions_CustomerID]
    ON [Sales].[CustomerTransactions]([CustomerID] ASC)
    ON [PS_TransactionDate] ([TransactionDate]);


GO
CREATE NONCLUSTERED INDEX [FK_Sales_CustomerTransactions_TransactionTypeID]
    ON [Sales].[CustomerTransactions]([TransactionTypeID] ASC)
    ON [PS_TransactionDate] ([TransactionDate]);


GO
CREATE NONCLUSTERED INDEX [FK_Sales_CustomerTransactions_InvoiceID]
    ON [Sales].[CustomerTransactions]([InvoiceID] ASC)
    ON [PS_TransactionDate] ([TransactionDate]);


GO
CREATE NONCLUSTERED INDEX [FK_Sales_CustomerTransactions_PaymentMethodID]
    ON [Sales].[CustomerTransactions]([PaymentMethodID] ASC)
    ON [PS_TransactionDate] ([TransactionDate]);


GO
CREATE NONCLUSTERED INDEX [IX_Sales_CustomerTransactions_IsFinalized]
    ON [Sales].[
```