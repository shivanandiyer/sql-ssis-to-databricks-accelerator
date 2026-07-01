# Review Required: OLTP:WebApi.InsertPackageTypesFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/InsertPackageTypesFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[InsertPackageTypesFromJson](@PackageTypes NVARCHAR(MAX), @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	INSERT INTO Warehouse.PackageTypes(PackageTypeName,LastEditedBy)
			OUTPUT  inserted.PackageTypeID
			SELECT PackageTypeName,@UserID
			FROM OPENJSON(@PackageTypes)
				WITH (PackageTypeName nvarchar(50))
END
```