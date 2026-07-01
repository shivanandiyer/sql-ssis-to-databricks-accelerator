# Review Required: OLTP:WebApi.UpdateSupplierCategoryFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateSupplierCategoryFromJson.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateSupplierCategoryFromJson](@SupplierCategory NVARCHAR(MAX), @SupplierCategoryID int, @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	UPDATE Purchasing.SupplierCategories SET
		SupplierCategoryName = json.SupplierCategoryName,
		LastEditedBy = @UserID
	FROM OPENJSON (@SupplierCategory)
		WITH (SupplierCategoryName nvarchar(50)) as json
	WHERE
		Purchasing.SupplierCategories.SupplierCategoryID = @SupplierCategoryID

END
```