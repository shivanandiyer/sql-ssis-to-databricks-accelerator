# Review Required: OLTP:WebApi.Cities

- **Object type:** VIEW
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Views/Cities.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- FOR JSON has no direct Spark SQL equivalent — reimplement with to_json(struct(...)).

## Source DDL (for reference)

```sql
CREATE VIEW [WebApi].[Cities]
AS
SELECT c.CityID, c.CityName, c.LatestRecordedPopulation, c.StateProvinceID, sp.StateProvinceName,
	Location = JSON_QUERY((SELECT
				type = 'Feature',
				[geometry.type] = 'Point',
				[geometry.coordinates] = JSON_QUERY(CONCAT('[',c.Location.Long,',',c.Location.Lat ,']'))
			FOR JSON PATH, WITHOUT_ARRAY_WRAPPER))
FROM Application.Cities c
	INNER JOIN Application.StateProvinces sp
		ON c.StateProvinceID = sp.StateProvinceID
```