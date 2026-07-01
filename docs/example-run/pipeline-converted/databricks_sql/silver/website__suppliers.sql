-- Source: OLTP:Website.Suppliers  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Website/Views/Suppliers.sql)
-- Converted: VIEW -> Databricks SQL view. Body translated with best-effort syntax
-- rewrites (bracket identifiers, ISNULL->COALESCE, GETDATE()->current_timestamp(),
-- TOP(n)->LIMIT n).

CREATE OR REPLACE VIEW wwi_<env>.silver.website__suppliers AS
SELECT s.SupplierID,
       s.SupplierName,
       sc.SupplierCategoryName,
       pp.FullName AS PrimaryContact,
       ap.FullName AS AlternateContact,
       s.PhoneNumber,
       s.FaxNumber,
       s.WebsiteURL,
       dm.DeliveryMethodName AS DeliveryMethod,
       c.CityName AS CityName,
       s.DeliveryLocation AS DeliveryLocation,
       s.SupplierReference
FROM Purchasing.Suppliers AS s
LEFT OUTER JOIN Purchasing.SupplierCategories AS sc
ON s.SupplierCategoryID = sc.SupplierCategoryID
LEFT OUTER JOIN `Application`.People AS pp
ON s.PrimaryContactPersonID = pp.PersonID
LEFT OUTER JOIN `Application`.People AS ap
ON s.AlternateContactPersonID = ap.PersonID
LEFT OUTER JOIN `Application`.DeliveryMethods AS dm
ON s.DeliveryMethodID = dm.DeliveryMethodID
LEFT OUTER JOIN `Application`.Cities AS c
ON s.DeliveryCityID = c.CityID
GO
;