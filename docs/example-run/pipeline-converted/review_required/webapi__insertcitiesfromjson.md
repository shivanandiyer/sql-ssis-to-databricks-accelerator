# Review Required: OLTP:WebApi.InsertCitiesFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/InsertCitiesFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[InsertCitiesFromJson](@Cities NVARCHAR(MAX), @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	INSERT INTO Application.Cities(CityName,StateProvinceID,LatestRecordedPopulation,LastEditedBy)
			OUTPUT  inserted.CityID
			SELECT CityName,StateProvinceID,LatestRecordedPopulation,@UserID
			FROM OPENJSON(@Cities)
				WITH (
					CityName nvarchar(50) N'strict $.CityName',
					StateProvinceID int N'strict $.StateProvinceID',
					LatestRecordedPopulation bigint)
END
```