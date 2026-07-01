-- Source: OLTP:WebApi.SalesOrders  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Views/SalesOrders.sql)
-- Converted: VIEW -> Databricks SQL view. Body translated with best-effort syntax
-- rewrites (bracket identifiers, ISNULL->COALESCE, GETDATE()->current_timestamp(),
-- TOP(n)->LIMIT n).

CREATE OR REPLACE VIEW wwi_<env>.silver.webapi__salesorders AS
SELECT	o.OrderID, o.OrderDate, o.CustomerPurchaseOrderNumber,
		o.ExpectedDeliveryDate, o.PickingCompletedWhen,
		o.CustomerID, c.CustomerName, c.PhoneNumber, c.FaxNumber, c.WebsiteURL,
		DeliveryLocation = JSON_QUERY((SELECT
				`type` = 'Feature',
				[geometry.type] = 'Point',
				[geometry.coordinates] = JSON_QUERY(CONCAT('[',c.DeliveryLocation.Long,',',c.DeliveryLocation.Lat ,']')),
				[properties.DeliveryMethod] = dm.DeliveryMethodName,
				[properties.AddressLine1] = c.DeliveryAddressLine1,
				[properties.AddressLine2] = c.DeliveryAddressLine2,
				[properties.PostalCode] = c.DeliveryPostalCode,
				[properties.Instructions] = o.DeliveryInstructions
			FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)),
		SalesPerson = sp.FullName, SalesPersonPhone = sp.PhoneNumber, SalesPersonEmail = sp.EmailAddress
FROM	Sales.Orders o
		INNER JOIN Sales.Customers c
			ON o.CustomerID = c.CustomerID
			LEFT OUTER JOIN `Application`.DeliveryMethods AS dm
				ON c.DeliveryMethodID = dm.DeliveryMethodID
		INNER JOIN Application.People sp
			ON o.SalespersonPersonID = sp.PersonID
;

-- UNRESOLVED — manual rewrite required:
-- FOR JSON has no direct Spark SQL equivalent — reimplement with to_json(struct(...)).