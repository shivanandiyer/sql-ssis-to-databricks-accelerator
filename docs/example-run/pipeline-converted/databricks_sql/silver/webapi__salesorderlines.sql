-- Source: OLTP:WebApi.SalesOrderLines  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Views/SalesOrderLines.sql)
-- Converted: VIEW -> Databricks SQL view. Body translated with best-effort syntax
-- rewrites (bracket identifiers, ISNULL->COALESCE, GETDATE()->current_timestamp(),
-- TOP(n)->LIMIT n).

CREATE OR REPLACE VIEW wwi_<env>.silver.webapi__salesorderlines AS
SELECT	ol.OrderLineID, ol.OrderID, ol.Description, ol.Quantity, ol.UnitPrice, ol.TaxRate, ol.PickingCompletedWhen,
		ProductName = si.StockItemName, si.Brand, si.Size, c.ColorName, pt.PackageTypeName
FROM	Sales.OrderLines ol
		INNER JOIN Warehouse.StockItems si
			ON ol.StockItemID = si.StockItemID
			INNER JOIN Warehouse.Colors c
				ON c.ColorID = si.ColorID
		INNER JOIN Warehouse.PackageTypes pt
			ON ol.PackageTypeID = pt.PackageTypeID
;