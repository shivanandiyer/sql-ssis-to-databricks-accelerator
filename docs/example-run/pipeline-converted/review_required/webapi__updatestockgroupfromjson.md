# Review Required: OLTP:WebApi.UpdateStockGroupFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateStockGroupFromJson.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateStockGroupFromJson](@StockGroup NVARCHAR(MAX), @StockGroupID int,@UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	UPDATE Warehouse.StockGroups SET
		StockGroupName = json.StockGroupName,
		LastEditedBy = @UserID
	FROM OPENJSON (@StockGroup)
		WITH (StockGroupName nvarchar(50)) as json
	WHERE
		Warehouse.StockGroups.StockGroupID = @StockGroupID

END
```