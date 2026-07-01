-- Source: OLTP:WebApi.CustomerTransactions  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Views/CustomerTransactions.sql)
-- Converted: VIEW -> Databricks SQL view. Body translated with best-effort syntax
-- rewrites (bracket identifiers, ISNULL->COALESCE, GETDATE()->current_timestamp(),
-- TOP(n)->LIMIT n).

CREATE OR REPLACE VIEW wwi_<env>.silver.webapi__customertransactions AS
SELECT ct.CustomerTransactionID, ct.TransactionDate, ct.AmountExcludingTax, ct.TaxAmount, ct.TransactionAmount, ct.OutstandingBalance, ct.FinalizationDate, ct.IsFinalized,
		c.CustomerName, tt.TransactionTypeName, i.InvoiceDate, i.CustomerPurchaseOrderNumber, pm.PaymentMethodName,
		ct.CustomerID, ct.TransactionTypeID, ct.InvoiceID, ct.PaymentMethodID
FROM Sales.CustomerTransactions AS ct
		JOIN Sales.Customers AS c ON ct.CustomerID = c.CustomerID
		JOIN Sales.Invoices AS i ON ct.InvoiceID = i.InvoiceID
		LEFT OUTER JOIN Application.TransactionTypes AS tt ON ct.TransactionTypeID = tt.TransactionTypeID
		LEFT OUTER JOIN Application.PaymentMethods AS pm ON ct.PaymentMethodID = pm.PaymentMethodID
;