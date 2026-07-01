# Review Required: OLTP:WebApi.UpdatePaymentMethodFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/UpdatePaymentMethodFromJson.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[UpdatePaymentMethodFromJson](@PaymentMethod NVARCHAR(MAX), @PaymentMethodID int,@UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	UPDATE Application.PaymentMethods SET
		PaymentMethodName = json.PaymentMethodName,
		LastEditedBy = @UserID
	FROM OPENJSON (@PaymentMethod)
		WITH (PaymentMethodName nvarchar(50)) as json
	WHERE
		Application.PaymentMethods.PaymentMethodID = @PaymentMethodID

END
```