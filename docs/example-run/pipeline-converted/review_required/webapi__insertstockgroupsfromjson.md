# Review Required: OLTP:WebApi.InsertStockGroupsFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/InsertStockGroupsFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[InsertStockGroupsFromJson](@StockGroups NVARCHAR(MAX), @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	INSERT INTO Warehouse.StockGroups(StockGroupName,LastEditedBy)
			OUTPUT  inserted.StockGroupID
			SELECT StockGroupName,@UserID
			FROM OPENJSON(@StockGroups)
				WITH (StockGroupName nvarchar(50))
END
```