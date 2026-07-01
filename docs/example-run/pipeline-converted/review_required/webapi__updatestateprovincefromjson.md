# Review Required: OLTP:WebApi.UpdateStateProvinceFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateStateProvinceFromJson.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateStateProvinceFromJson](@StateProvince NVARCHAR(MAX), @StateProvinceID int, @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	UPDATE	Application.StateProvinces SET
			StateProvinceCode = json.StateProvinceCode,
			StateProvinceName = json.StateProvinceName,
			CountryID = json.CountryID,
			SalesTerritory = json.SalesTerritory,
			LatestRecordedPopulation = json.LatestRecordedPopulation,
			LastEditedBy = @UserID
		FROM OPENJSON (@StateProvince)
			WITH (
				StateProvinceCode nvarchar(5) N'strict $.StateProvinceCode',
				StateProvinceName nvarchar(50) N'strict $.StateProvinceName',
				CountryID int N'strict $.CountryID',
				SalesTerritory nvarchar(50) N'strict $.SalesTerritory',
				LatestRecordedPopulation bigint) as json
		WHERE
			Application.StateProvinces.StateProvinceID = @StateProvinceID

END
```