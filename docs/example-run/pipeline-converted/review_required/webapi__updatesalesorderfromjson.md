# Review Required: OLTP:WebApi.UpdateSalesOrderFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateSalesOrderFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateSalesOrderFromJson](@SalesOrder NVARCHAR(MAX), @SalesOrderID int, @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN	UPDATE Sales.Orders SET
				SalespersonPersonID = ISNULL(json.SalespersonPersonID,Sales.Orders.SalespersonPersonID),
				PickedByPersonID = ISNULL(json.PickedByPersonID,Sales.Orders.PickedByPersonID),
				ContactPersonID = ISNULL(json.ContactPersonID,Sales.Orders.ContactPersonID),
				BackorderOrderID = ISNULL(json.BackorderOrderID,Sales.Orders.BackorderOrderID),
				OrderDate = ISNULL(json.OrderDate,Sales.Orders.OrderDate),
				ExpectedDeliveryDate = ISNULL(json.ExpectedDeliveryDate,Sales.Orders.ExpectedDeliveryDate),
				CustomerPurchaseOrderNumber = ISNULL(json.CustomerPurchaseOrderNumber,Sales.Orders.CustomerPurchaseOrderNumber),
				IsUndersupplyBackordered = ISNULL(json.IsUndersupplyBackordered,Sales.Orders.IsUndersupplyBackordered),
				PickingCompletedWhen = ISNULL(json.PickingCompletedWhen,Sales.Orders.PickingCompletedWhen),
				LastEditedBy = @UserID
			FROM OPENJSON(@SalesOrder)
				WITH (
					SalespersonPersonID int,
					PickedByPersonID int,
					ContactPersonID int,
					BackorderOrderID int,
					OrderDate date,
					ExpectedDeliveryDate date,
					CustomerPurchaseOrderNumber nvarchar(20),
					IsUndersupplyBackordered bit,
					PickingCompletedWhen date) as json
			WHERE
				Sales.Orders.OrderID = @SalesOrderID

END
```