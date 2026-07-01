# Review Required: OLTP:WebApi.UpdateCountryFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateCountryFromJson.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateCountryFromJson](@Country NVARCHAR(MAX), @CountryID int, @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN	UPDATE Application.Countries SET
				CountryName = json.CountryName,
				FormalName = json.FormalName,
				IsoAlpha3Code = json.IsoAlpha3Code,
				IsoNumericCode = json.IsoNumericCode,
				CountryType = json.CountryType,
				LatestRecordedPopulation = json.LatestRecordedPopulation,
				Continent = json.Continent,
				Region = json.Region,
				Subregion = json.Subregion,
				LastEditedBy = @UserID
			FROM OPENJSON (@Country)
				WITH (
					CountryName nvarchar(60) N'strict $.CountryName',
					FormalName nvarchar(60) N'strict $.FormalName',
					IsoAlpha3Code nvarchar(3),
					IsoNumericCode int,
					CountryType nvarchar(20),
					LatestRecordedPopulation bigint,
					Continent nvarchar(30) N'strict $.Continent',
					Region nvarchar(30) N'strict $.Region',
					Subregion nvarchar(30) N'strict $.Subregion') as json
			WHERE
				Application.Countries.CountryID = @CountryID
END
```