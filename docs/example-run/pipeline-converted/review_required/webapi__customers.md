# Review Required: OLTP:WebApi.Customers

- **Object type:** VIEW
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Views/Customers.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- FOR JSON has no direct Spark SQL equivalent — reimplement with to_json(struct(...)).

## Source DDL (for reference)

```sql
CREATE VIEW [WebApi].[Customers]
AS
SELECT c.CustomerID,
       c.CustomerName,
       sc.CustomerCategoryName,
       pp.FullName AS PrimaryContact,
       ap.FullName AS AlternateContact,
       c.PhoneNumber,
       c.FaxNumber,
       c.WebsiteURL,
	   c.PostalAddressLine1,
	   c.PostalAddressLine2,
	   c.PostalPostalCode,
	   c.PostalCityID,
	   PostalCity = pc.CityName,
	   c.AccountOpenedDate,
	   c.CreditLimit,
	   c.IsOnCreditHold,
	   c.IsStatementSent,
	   c.PaymentDays,
	   c.RunPosition,
	   c.StandardDiscountPercentage,
	   bg.BuyingGroupName,
       DeliveryLocation = JSON_QUERY((SELECT
				type = 'Feature',
				[geometry.type] = 'Point',
				[geometry.coordinates] = JSON_QUERY(CONCAT('[',c.DeliveryLocation.Long,',',c.DeliveryLocation.Lat ,']')),
				[properties.DeliveryMethod] = DeliveryMethodName,
				[properties.CityName] = pc.CityName,
				[properties.Province] = sp.StateProvinceName,
				[properties.Territory] = sp.SalesTerritory
		FOR JSON PATH, WITHOUT_ARRAY_WRAPPER)),
		c.PrimaryContactPersonID,
		c.AlternateContactPersonID,
		c.BillToCustomerID,
		c.BuyingGroupID,
		c.CustomerCategoryID
FROM Sales.Customers AS c
LEFT OUTER JOIN Sales.CustomerCategories AS sc
ON c.CustomerCategoryID = sc.CustomerCategoryID
LEFT OUTER JOIN [Application].People AS pp
ON c.PrimaryContactPersonID = pp.PersonID
LEFT OUTER JOIN [Application].People AS ap
ON c.AlternateContactPersonID = ap.PersonID
LEFT OUTER JOIN Sales.BuyingGroups AS bg
ON c.BuyingGroupID = bg.BuyingGroupID
LEFT OUTER JOIN [Application].DeliveryMethods AS dm
ON c.DeliveryMethodID = dm.DeliveryMethodID
LEFT OUTER JOIN [Application].Cities AS pc
ON c.PostalCityID = pc.CityID
LEFT OUTER JOIN [Application].StateProvinces AS sp
ON sp.StateProvinceID = pc.StateProvinceID
```