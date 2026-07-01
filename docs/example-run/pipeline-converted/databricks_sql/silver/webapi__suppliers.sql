-- Source: OLTP:WebApi.Suppliers  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Views/Suppliers.sql)
-- Converted: VIEW -> Databricks SQL view. Body translated with best-effort syntax
-- rewrites (bracket identifiers, ISNULL->COALESCE, GETDATE()->current_timestamp(),
-- TOP(n)->LIMIT n).

CREATE OR REPLACE VIEW wwi_<env>.silver.webapi__suppliers AS
SELECT s.SupplierID,
       s.SupplierName,
       sc.SupplierCategoryName,
       pp.FullName AS PrimaryContact,
       ap.FullName AS AlternateContact,
       s.PhoneNumber,
       s.FaxNumber,
       s.WebsiteURL,
       s.SupplierReference,
	   s.BankAccountName,
	   s.BankAccountBranch,
		s.BankAccountCode,
		s.BankAccountNumber,
		s.BankInternationalCode,
		s.PostalAddressLine1,
		s.PostalAddressLine2,
		s.PostalPostalCode,
		s.PaymentDays,
		s.SupplierCategoryID,
	   DeliveryLocation = JSON_QUERY((SELECT
				`type` = 'Feature',
				[geometry.type] = 'Point',
				[geometry.coordinates] = JSON_QUERY(CONCAT('[',s.DeliveryLocation.Long,',',s.DeliveryLocation.Lat ,']')),
				[properties.DeliveryMethod] = dm.DeliveryMethodName,
				[properties.DeliveryMethodID] = s.DeliveryMethodID,
				[properties.City] = c.CityName,
				[properties.Province] = sp.StateProvinceName,
				[properties.Territory] = sp.SalesTerritory
			FOR JSON PATH, WITHOUT_ARRAY_WRAPPER))
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
		LEFT OUTER JOIN `Application`.StateProvinces AS sp
			ON sp.StateProvinceID = c.StateProvinceID
;

-- UNRESOLVED — manual rewrite required:
-- FOR JSON has no direct Spark SQL equivalent — reimplement with to_json(struct(...)).