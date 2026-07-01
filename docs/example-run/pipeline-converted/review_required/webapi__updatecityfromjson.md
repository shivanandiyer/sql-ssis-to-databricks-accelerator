# Review Required: OLTP:WebApi.UpdateCityFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateCityFromJson.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateCityFromJson](@City NVARCHAR(MAX), @CityID int,@UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	UPDATE Application.Cities SET
		CityName = json.CityName,
		StateProvinceID = json.StateProvinceID,
		LatestRecordedPopulation = json.LatestRecordedPopulation,
		LastEditedBy = @UserID
	FROM OPENJSON (@City)
		WITH (
			CityName nvarchar(50) N'strict $.CityName',
			StateProvinceID int N'strict $.StateProvinceID',
			LatestRecordedPopulation bigint) as json
	WHERE
		Application.Cities.CityID = @CityID

END
```