# Review Required: OLTP:WebApi.InsertBuyingGroupsFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/InsertBuyingGroupsFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[InsertBuyingGroupsFromJson](@BuyingGroups NVARCHAR(MAX), @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	INSERT INTO Sales.BuyingGroups(BuyingGroupName,LastEditedBy)
			OUTPUT  inserted.BuyingGroupID
			SELECT BuyingGroupName,@UserID
			FROM OPENJSON(@BuyingGroups)
				WITH (BuyingGroupName nvarchar(50))
END
```