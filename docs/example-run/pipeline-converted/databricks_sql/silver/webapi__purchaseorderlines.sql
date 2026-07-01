-- Source: OLTP:WebApi.PurchaseOrderLines  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Views/PurchaseOrderLines.sql)
-- Converted: VIEW -> Databricks SQL view. Body translated with best-effort syntax
-- rewrites (bracket identifiers, ISNULL->COALESCE, GETDATE()->current_timestamp(),
-- TOP(n)->LIMIT n).

CREATE OR REPLACE VIEW wwi_<env>.silver.webapi__purchaseorderlines AS
SELECT	ol.PurchaseOrderLineID, ol.PurchaseOrderID, ol.Description, ol.IsOrderLineFinalized,
		ProductName = si.StockItemName, si.Brand, si.Size, c.ColorName, pt.PackageTypeName,
		ol.ReceivedOuters, ol.OrderedOuters, ol.ExpectedUnitPricePerOuter
FROM	Purchasing.PurchaseOrderLines ol
		INNER JOIN Warehouse.StockItems si
			ON ol.StockItemID = si.StockItemID
			INNER JOIN Warehouse.Colors c
				ON c.ColorID = si.ColorID
		INNER JOIN Warehouse.PackageTypes pt
			ON ol.PackageTypeID = pt.PackageTypeID
;