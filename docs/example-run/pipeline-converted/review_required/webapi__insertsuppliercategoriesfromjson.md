# Review Required: OLTP:WebApi.InsertSupplierCategoriesFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/InsertSupplierCategoriesFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[InsertSupplierCategoriesFromJson](@SupplierCategories NVARCHAR(MAX), @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	INSERT INTO Purchasing.SupplierCategories(SupplierCategoryName,LastEditedBy)
			OUTPUT  inserted.SupplierCategoryID
			SELECT SupplierCategoryName,@UserID
			FROM OPENJSON(@SupplierCategories)
				WITH (SupplierCategoryName nvarchar(50))
END
```