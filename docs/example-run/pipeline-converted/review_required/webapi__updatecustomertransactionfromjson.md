# Review Required: OLTP:WebApi.UpdateCustomerTransactionFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateCustomerTransactionFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateCustomerTransactionFromJson](@CustomerTransaction NVARCHAR(MAX), @CustomerTransactionID int, @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	UPDATE Sales.CustomerTransactions SET
			TransactionTypeID = ISNULL(json.TransactionTypeID, Sales.CustomerTransactions.TransactionTypeID),
			PaymentMethodID = json.PaymentMethodID,
			TransactionDate = ISNULL(json.TransactionDate, Sales.CustomerTransactions.TransactionDate),
			AmountExcludingTax = ISNULL(json.AmountExcludingTax, Sales.CustomerTransactions.AmountExcludingTax),
			TaxAmount = ISNULL(json.TaxAmount, Sales.CustomerTransactions.TaxAmount),
			TransactionAmount = ISNULL(json.TransactionAmount, Sales.CustomerTransactions.TransactionAmount),
			OutstandingBalance = ISNULL(json.OutstandingBalance, Sales.CustomerTransactions.OutstandingBalance),
			FinalizationDate = json.FinalizationDate,
			LastEditedBy = @UserID
		FROM OPENJSON(@CustomerTransaction)
			WITH (
				TransactionTypeID int,
				PaymentMethodID int,
				TransactionDate date,
				FinalizationDate date,
				AmountExcludingTax decimal(18,2),
				TaxAmount decimal(18,2),
				TransactionAmount decimal(18,2),
				OutstandingBalance decimal(18,2)
				) as json
		WHERE
			Sales.CustomerTransactions.CustomerTransactionID = @CustomerTransactionID

END
```