-- Source: OLTP:WebApi.PurchaseOrders  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Views/PurchaseOrders.sql)
-- Converted: VIEW -> Databricks SQL view. Body translated with best-effort syntax
-- rewrites (bracket identifiers, ISNULL->COALESCE, GETDATE()->current_timestamp(),
-- TOP(n)->LIMIT n).

CREATE OR REPLACE VIEW wwi_<env>.silver.webapi__purchaseorders AS
SELECT	o.PurchaseOrderID, o.OrderDate, o.ExpectedDeliveryDate, o.SupplierReference, o.IsOrderFinalized,
		dm.DeliveryMethodName, o.DeliveryMethodID, o.SupplierID,
		ContactName = c.FullName, ContactPhone = c.PhoneNumber, ContactFax = c.FaxNumber, ContactEmail = c.EmailAddress
FROM	Purchasing.PurchaseOrders o
		INNER JOIN Application.People c
			ON o.ContactPersonID = c.PersonID
		INNER JOIN Application.DeliveryMethods dm
			ON o.DeliveryMethodID = dm.DeliveryMethodID
;