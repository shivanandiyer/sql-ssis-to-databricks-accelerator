# Review Required: OLTP:WebApi.UpdateCustomerCategoryFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateCustomerCategoryFromJson.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateCustomerCategoryFromJson](@CustomerCategory NVARCHAR(MAX), @CustomerCategoryID int, @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	UPDATE Sales.CustomerCategories SET
		CustomerCategoryName = json.CustomerCategoryName,
		LastEditedBy = @UserID
	FROM OPENJSON (@CustomerCategory)
		WITH (CustomerCategoryName nvarchar(50)) as json
	WHERE
		Sales.CustomerCategories.CustomerCategoryID = @CustomerCategoryID
END
```