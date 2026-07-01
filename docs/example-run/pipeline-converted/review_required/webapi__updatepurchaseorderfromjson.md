# Review Required: OLTP:WebApi.UpdatePurchaseOrderFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdatePurchaseOrderFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdatePurchaseOrderFromJson](@PurchaseOrder NVARCHAR(MAX), @PurchaseOrderID int, @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN	UPDATE Purchasing.PurchaseOrders SET
				SupplierID = ISNULL(json.SupplierID, Purchasing.PurchaseOrders.SupplierID),
				OrderDate = ISNULL(json.OrderDate,Purchasing.PurchaseOrders.OrderDate),
				DeliveryMethodID = ISNULL(json.DeliveryMethodID,Purchasing.PurchaseOrders.DeliveryMethodID),
				ContactPersonID = ISNULL(json.ContactPersonID,Purchasing.PurchaseOrders.ContactPersonID),
				ExpectedDeliveryDate = json.ExpectedDeliveryDate,
				SupplierReference = json.SupplierReference,
				IsOrderFinalized = ISNULL(json.IsOrderFinalized,Purchasing.PurchaseOrders.IsOrderFinalized)
			FROM OPENJSON(@PurchaseOrder)
				WITH (
					SupplierID int,
					OrderDate date,
					DeliveryMethodID int,
					ContactPersonID int,
					ExpectedDeliveryDate date,
					SupplierReference nvarchar(20),
					IsOrderFinalized bit) as json
			WHERE
				Purchasing.PurchaseOrders.PurchaseOrderID = @PurchaseOrderID

END
```