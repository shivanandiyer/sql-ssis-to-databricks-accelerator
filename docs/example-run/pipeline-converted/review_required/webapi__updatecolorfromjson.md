# Review Required: OLTP:WebApi.UpdateColorFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateColorFromJson.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateColorFromJson](@Color NVARCHAR(MAX), @ColorID int, @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	UPDATE Warehouse.Colors SET
		ColorName = json.ColorName,
		LastEditedBy = @UserID
	FROM OPENJSON (@Color)
		WITH (ColorName nvarchar(50)) as json
	WHERE
		Warehouse.Colors.ColorID = @ColorID

END
```