# Review Required: OLTP:WebApi.InsertStateProvincesFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/InsertStateProvincesFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[InsertStateProvincesFromJson](@StateProvinces NVARCHAR(MAX), @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	INSERT INTO Application.StateProvinces(StateProvinceCode,StateProvinceName,CountryID,SalesTerritory,LatestRecordedPopulation,LastEditedBy)
	OUTPUT  inserted.StateProvinceID
	SELECT StateProvinceCode,StateProvinceName,CountryID,SalesTerritory,LatestRecordedPopulation,@UserID
	FROM OPENJSON(@StateProvinces)
		WITH (
			StateProvinceCode nvarchar(5) N'strict $.StateProvinceCode',
			StateProvinceName nvarchar(50) N'strict $.StateProvinceName',
			CountryID int N'strict $.CountryID',
			SalesTerritory nvarchar(50) N'strict $.SalesTerritory',
			LatestRecordedPopulation bigint)
END
```