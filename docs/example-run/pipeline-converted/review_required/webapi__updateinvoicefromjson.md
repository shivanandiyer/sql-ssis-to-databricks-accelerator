# Review Required: OLTP:WebApi.UpdateInvoiceFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateInvoiceFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].UpdateInvoiceFromJson(@Invoice NVARCHAR(MAX), @InvoiceID int, @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN	UPDATE Sales.Invoices SET
				CustomerID = ISNULL(json.CustomerID, Sales.Invoices.CustomerID),
				BillToCustomerID = ISNULL(json.BillToCustomerID, Sales.Invoices.BillToCustomerID),
				DeliveryMethodID = ISNULL(json.DeliveryMethodID, Sales.Invoices.DeliveryMethodID),
				ContactPersonID = ISNULL(json.ContactPersonID, Sales.Invoices.ContactPersonID),
				AccountsPersonID = ISNULL(json.AccountsPersonID, Sales.Invoices.AccountsPersonID),
				SalespersonPersonID = ISNULL(json.SalespersonPersonID, Sales.Invoices.SalespersonPersonID),
				PackedByPersonID = ISNULL(json.PackedByPersonID, Sales.Invoices.PackedByPersonID),
				InvoiceDate = ISNULL(json.InvoiceDate, Sales.Invoices.InvoiceDate),
				CustomerPurchaseOrderNumber = json.CustomerPurchaseOrderNumber,
				IsCreditNote = ISNULL(json.IsCreditNote, Sales.Invoices.IsCreditNote),
				TotalDryItems = ISNULL(json.TotalDryItems, Sales.Invoices.TotalDryItems),
				TotalChillerItems = ISNULL(json.TotalChillerItems, Sales.Invoices.TotalChillerItems),
				DeliveryRun = json.DeliveryRun,
				RunPosition = json.RunPosition,
				LastEditedBy = @UserID
			FROM OPENJSON(@Invoice)
				WITH (
					CustomerID int,
					BillToCustomerID int,
					OrderID int,
					DeliveryMethodID int,
					ContactPersonID int,
					AccountsPersonID int,
					SalespersonPersonID int,
					PackedByPersonID int,
					InvoiceDate date,
					CustomerPurchaseOrderNumber nvarchar(20),
					IsCreditNote bit,
					TotalDryItems int,
					TotalChillerItems int,
					DeliveryRun nvarchar(5),
					RunPosition nvarchar(5)) as json
			WHERE
				Sales.Invoices.InvoiceID = @InvoiceID

END
```