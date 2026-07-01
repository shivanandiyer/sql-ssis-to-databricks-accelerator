# Review Required: OLTP:Sales.Invoices

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Sales/Tables/Invoices.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `InvoiceID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `ConfirmedDeliveryTime` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `ConfirmedReceivedBy` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_Invoices_AccountsPersonID_Application_People] FOREIGN KEY ([AccountsPersonID]) REFERENCES [Applicat
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_Invoices_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([Perso
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_Invoices_BillToCustomerID_Sales_Customers] FOREIGN KEY ([BillToCustomerID]) REFERENCES [Sales].[Cus
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_Invoices_ContactPersonID_Application_People] FOREIGN KEY ([ContactPersonID]) REFERENCES [Applicatio
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_Invoices_CustomerID_Sales_Customers] FOREIGN KEY ([CustomerID]) REFERENCES [Sales].[Customers] ([Cu
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_Invoices_DeliveryMethodID_Application_DeliveryMethods] FOREIGN KEY ([DeliveryMethodID]) REFERENCES 
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_Invoices_OrderID_Sales_Orders] FOREIGN KEY ([OrderID]) REFERENCES [Sales].[Orders] ([OrderID])
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_Invoices_PackedByPersonID_Application_People] FOREIGN KEY ([PackedByPersonID]) REFERENCES [Applicat
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_Invoices_SalespersonPersonID_Application_People] FOREIGN KEY ([SalespersonPersonID]) REFERENCES [Ap

## Source DDL (for reference)

```sql
CREATE TABLE [Sales].[Invoices] (
    [InvoiceID]                   INT            CONSTRAINT [DF_Sales_Invoices_InvoiceID] DEFAULT (NEXT VALUE FOR [Sequences].[InvoiceID]) NOT NULL,
    [CustomerID]                  INT            NOT NULL,
    [BillToCustomerID]            INT            NOT NULL,
    [OrderID]                     INT            NULL,
    [DeliveryMethodID]            INT            NOT NULL,
    [ContactPersonID]             INT            NOT NULL,
    [AccountsPersonID]            INT            NOT NULL,
    [SalespersonPersonID]         INT            NOT NULL,
    [PackedByPersonID]            INT            NOT NULL,
    [InvoiceDate]                 DATE           NOT NULL,
    [CustomerPurchaseOrderNumber] NVARCHAR (20)  NULL,
    [IsCreditNote]                BIT            NOT NULL,
    [CreditNoteReason]            NVARCHAR (MAX) NULL,
    [Comments]                    NVARCHAR (MAX) NULL,
    [DeliveryInstructions]        NVARCHAR (MAX) NULL,
    [InternalComments]            NVARCHAR (MAX) NULL,
    [TotalDryItems]               INT            NOT NULL,
    [TotalChillerItems]           INT            NOT NULL,
    [DeliveryRun]                 NVARCHAR (5)   NULL,
    [RunPosition]                 NVARCHAR (5)   NULL,
    [ReturnedDeliveryData]        NVARCHAR (MAX) NULL,
    [ConfirmedDeliveryTime]       AS             (TRY_CONVERT([datetime2](7),json_value([ReturnedDeliveryData],N'$.DeliveredWhen'),(126))),
    [ConfirmedReceivedBy]         AS             (json_value([ReturnedDeliveryData],N'$.ReceivedBy')),
    [LastEditedBy]                INT            NOT NULL,
    [LastEditedWhen]              DATETIME2 (7)  CONSTRAINT [DF_Sales_Invoices_LastEditedWhen] DEFAULT (sysdatetime()) NOT NULL,
    CONSTRAINT [PK_Sales_Invoices] PRIMARY KEY CLUSTERED ([InvoiceID] ASC),
    CONSTRAINT [CK_Sales_Invoices_ReturnedDeliveryData_Must_Be_Valid_JSON] CHECK ([ReturnedDeliveryData] IS NULL OR isjson([ReturnedDeliveryData])<>(0)),
    CONSTRAINT [FK_Sales_Invoices_AccountsPersonID_Application_People] FOREIGN KEY ([AccountsPersonID]) REFERENCES [Application].[People] ([PersonID]),
    CONSTRAINT [FK_Sales_Invoices_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([PersonID]),
    CONSTRAINT [FK_Sales_Invoices_BillToCustomerID_Sales_Customers] FOREIGN KEY ([BillToCustomerID]) REFERENCES [Sales].[Customers] ([CustomerID]),
    CONSTRAINT [FK_Sales_Invoices_ContactPersonID_Application_People] FOREIGN KEY ([ContactPersonID]) REFERENCES [Application].[People] ([PersonID]),
    CONSTRAINT [FK_Sales_Invoices_CustomerID_Sales_Customers] FOREIGN KEY ([CustomerID]) REFERENCES [Sales].[Customers] ([CustomerID]),
    CONSTRAINT [FK_Sales_Invoices_DeliveryMethodID_Application_DeliveryMethods] FOREIGN KEY ([DeliveryMethodID]) REFERENCES [Application].[DeliveryMethods] ([DeliveryMethodID]),
    CONSTRAINT [FK_Sales_Invoices_OrderID_Sales_Orders] FOREIGN KEY ([OrderID]) REFERENCES [Sales].[Orders] ([OrderID
```