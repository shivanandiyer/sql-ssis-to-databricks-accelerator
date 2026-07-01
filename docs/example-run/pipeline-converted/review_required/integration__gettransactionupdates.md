# Review Required: OLTP:Integration.GetTransactionUpdates

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Integration/Stored Procedures/GetTransactionUpdates.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE Integration.GetTransactionUpdates
@LastCutoff datetime2(7),
@NewCutoff datetime2(7)
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    SELECT CAST(ct.TransactionDate AS date) AS [Date Key],
           ct.CustomerTransactionID AS [WWI Customer Transaction ID],
           CAST(NULL AS int) AS [WWI Supplier Transaction ID],
           ct.InvoiceID AS [WWI Invoice ID],
           CAST(NULL AS int) AS [WWI Purchase Order ID],
           CAST(NULL AS nvarchar(20)) AS [Supplier Invoice Number],
           ct.AmountExcludingTax AS [Total Excluding Tax],
           ct.TaxAmount AS [Tax Amount],
           ct.TransactionAmount AS [Total Including Tax],
           ct.OutstandingBalance AS [Outstanding Balance],
           ct.IsFinalized AS [Is Finalized],
           COALESCE(i.CustomerID, ct.CustomerID) AS [WWI Customer ID],
           ct.CustomerID AS [WWI Bill To Customer ID],
           CAST(NULL AS int) AS [WWI Supplier ID],
           ct.TransactionTypeID AS [WWI Transaction Type ID],
           ct.PaymentMethodID AS [WWI Payment Method ID],
           ct.LastEditedWhen AS [Last Modified When]
    FROM Sales.CustomerTransactions AS ct
    LEFT OUTER JOIN Sales.Invoices AS i
    ON ct.InvoiceID = i.InvoiceID
    WHERE ct.LastEditedWhen > @LastCutoff
    AND ct.LastEditedWhen <= @NewCutoff

    UNION ALL

    SELECT CAST(st.TransactionDate AS date) AS [Date Key],
           CAST(NULL AS int) AS [WWI Customer Transaction ID],
           st.SupplierTransactionID AS [WWI Supplier Transaction ID],
           CAST(NULL AS int) AS [WWI Invoice ID],
           st.PurchaseOrderID AS [WWI Purchase Order ID],
           st.SupplierInvoiceNumber AS [Supplier Invoice Number],
           st.AmountExcludingTax AS [Total Excluding Tax],
           st.TaxAmount AS [Tax Amount],
           st.TransactionAmount AS [Total Including Tax],
           st.OutstandingBalance AS [Outstanding Balance],
           st.IsFinalized AS [Is Finalized],
           CAST(NULL AS int) AS [WWI Customer ID],
           CAST(NULL AS int) AS [WWI Bill To Customer ID],
           st.SupplierID AS [WWI Supplier ID],
           st.TransactionTypeID AS [WWI Transaction Type ID],
           st.PaymentMethodID AS [WWI Payment Method ID],
           st.LastEditedWhen AS [Last Modified When]
    FROM Purchasing.SupplierTransactions AS st
    WHERE st.LastEditedWhen > @LastCutoff
    AND st.LastEditedWhen <= @NewCutoff;

    RETURN 0;
END;
```