# Review Required: OLTP:WebApi.UpdateBuyingGroupFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateBuyingGroupFromJson.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateBuyingGroupFromJson](@BuyingGroup NVARCHAR(MAX), @BuyingGroupID int,@UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	UPDATE Sales.BuyingGroups SET
		BuyingGroupName = json.BuyingGroupName,
		LastEditedBy = @UserID
	FROM OPENJSON (@BuyingGroup)
		WITH (BuyingGroupName nvarchar(50)) as json
	WHERE
		Sales.BuyingGroups.BuyingGroupID = @BuyingGroupID
END
```