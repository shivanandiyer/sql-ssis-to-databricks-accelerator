-- Source: OLTP:WebApi.Cities  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Views/Cities.sql)
-- Converted: VIEW -> Databricks SQL view. Body translated with best-effort syntax
-- rewrites (bracket identifiers, ISNULL->COALESCE, GETDATE()->current_timestamp(),
-- TOP(n)->LIMIT n).

CREATE OR REPLACE VIEW wwi_<env>.silver.webapi__cities AS
SELECT c.CityID, c.CityName, c.LatestRecordedPopulation, c.StateProvinceID, sp.StateProvinceName,
	Location = JSON_QUERY((SELECT
				type = 'Feature',
				[geometry.type] = 'Point',
				[geometry.coordinates] = JSON_QUERY(CONCAT('[',c.Location.Long,',',c.Location.Lat ,']'))
			FOR JSON PATH, WITHOUT_ARRAY_WRAPPER))
FROM Application.Cities c
	INNER JOIN Application.StateProvinces sp
		ON c.StateProvinceID = sp.StateProvinceID
;

-- UNRESOLVED — manual rewrite required:
-- FOR JSON has no direct Spark SQL equivalent — reimplement with to_json(struct(...)).