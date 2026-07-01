-- Source: OLTP:DataLoadSimulation.PaySuppliers  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/PaySuppliers.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

INSERT @TransactionsToPay
        (SupplierTransactionID, SupplierID, PurchaseOrderID, SupplierInvoiceNumber, OutstandingBalance)
    SELECT SupplierTransactionID, SupplierID, PurchaseOrderID, SupplierInvoiceNumber, OutstandingBalance
    FROM Purchasing.SupplierTransactions
    WHERE IsFinalized = 0;

UPDATE Purchasing.SupplierTransactions
    SET OutstandingBalance = 0,
        FinalizationDate = @StartingWhen,
        LastEditedBy = @StaffMemberPersonID,
        LastEditedWhen = @StartingWhen
    WHERE SupplierTransactionID IN (SELECT SupplierTransactionID FROM @TransactionsToPay);

INSERT Purchasing.SupplierTransactions
        (SupplierID, TransactionTypeID, PurchaseOrderID, PaymentMethodID,
         SupplierInvoiceNumber, TransactionDate, AmountExcludingTax, TaxAmount, TransactionAmount,
         OutstandingBalance, FinalizationDate, LastEditedBy, LastEditedWhen)
    SELECT ttp.SupplierID, `DataLoadSimulation`.`GetTransactionTypeID` (N'Supplier Payment Issued'),
           NULL, `DataLoadSimulation`.`GetPaymentMethodID` (N'EFT'),
           NULL, CAST(@StartingWhen AS date), 0, 0, 0 - SUM(ttp.OutstandingBalance),
           0, CAST(@StartingWhen AS date), @StaffMemberPersonID, @StartingWhen
    FROM @TransactionsToPay AS ttp
    GROUP BY ttp.SupplierID;