# Review Required: OLTP:WebApi.UpdateSupplierTransactionFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateSupplierTransactionFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateSupplierTransactionFromJson](@SupplierTransaction NVARCHAR(MAX), @SupplierTransactionID int, @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	UPDATE Purchasing.SupplierTransactions SET
			SupplierID = ISNULL(json.SupplierID,Purchasing.SupplierTransactions.SupplierID),
			TransactionTypeID = ISNULL(json.TransactionTypeID,Purchasing.SupplierTransactions.TransactionTypeID),
			PurchaseOrderID = json.PurchaseOrderID,
			PaymentMethodID = json.PaymentMethodID,
			SupplierInvoiceNumber = ISNULL(json.SupplierInvoiceNumber,Purchasing.SupplierTransactions.SupplierInvoiceNumber),
			TransactionDate = ISNULL(json.TransactionDate,Purchasing.SupplierTransactions.TransactionDate),
			AmountExcludingTax = ISNULL(json.AmountExcludingTax,Purchasing.SupplierTransactions.AmountExcludingTax),
			TaxAmount = ISNULL(json.TaxAmount,Purchasing.SupplierTransactions.TaxAmount),
			TransactionAmount = ISNULL(json.TransactionAmount,Purchasing.SupplierTransactions.TransactionAmount),
			OutstandingBalance = ISNULL(json.OutstandingBalance,Purchasing.SupplierTransactions.OutstandingBalance),
			FinalizationDate = ISNULL(json.FinalizationDate,Purchasing.SupplierTransactions.FinalizationDate),
			LastEditedBy = @UserID
		FROM OPENJSON(@SupplierTransaction)
			WITH (
				SupplierID int,
				TransactionTypeID int,
				PurchaseOrderID int,
				PaymentMethodID int,
				SupplierInvoiceNumber nvarchar(20),
				TransactionDate date,
				AmountExcludingTax decimal(18,2),
				TaxAmount decimal(18,2),
				TransactionAmount decimal(18,2),
				OutstandingBalance decimal(18,2),
				FinalizationDate date) as json
		WHERE
			Purchasing.SupplierTransactions.SupplierTransactionID = @SupplierTransactionID

END
```