# Review Required: OLTP:WebApi.UpdateDeliveryMethodFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdateDeliveryMethodFromJson.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdateDeliveryMethodFromJson](@DeliveryMethod NVARCHAR(MAX), @DeliveryMethodID int,@UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	UPDATE Application.DeliveryMethods SET
		DeliveryMethodName = json.DeliveryMethodName,
		LastEditedBy = @UserID
	FROM OPENJSON (@DeliveryMethod)
		WITH (DeliveryMethodName nvarchar(50)) as json
	WHERE
		Application.DeliveryMethods.DeliveryMethodID = @DeliveryMethodID

END
```