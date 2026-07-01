-- Source: OLTP:WebApi.SpecialDeals  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Views/SpecialDeals.sql)
-- Converted: VIEW -> Databricks SQL view. Body translated with best-effort syntax
-- rewrites (bracket identifiers, ISNULL->COALESCE, GETDATE()->current_timestamp(),
-- TOP(n)->LIMIT n).

CREATE OR REPLACE VIEW wwi_<env>.silver.webapi__specialdeals AS
SELECT	deal.SpecialDealID, deal.DealDescription, deal.StartDate, deal.EndDate, deal.DiscountAmount, deal.DiscountPercentage, deal.UnitPrice,
		si.StockItemName, si.Brand, si.Size, c.CustomerName, bg.BuyingGroupName, cat.CustomerCategoryName,
		deal.StockItemID, deal.CustomerID, deal.BuyingGroupID, deal.CustomerCategoryID, deal.StockGroupID
FROM Sales.SpecialDeals AS deal
	LEFT OUTER JOIN Warehouse.StockItems AS si ON deal.StockItemID = si.StockItemID
	LEFT OUTER JOIN Sales.Customers AS c ON deal.CustomerID = c.CustomerID
	LEFT OUTER JOIN Sales.CustomerCategories AS cat ON deal.CustomerCategoryID = cat.CustomerCategoryID
	LEFT OUTER JOIN Sales.BuyingGroups AS bg ON deal.BuyingGroupID = bg.BuyingGroupID
;