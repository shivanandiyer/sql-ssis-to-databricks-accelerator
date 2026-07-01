# Review Required: OLTP:WebApi.InsertPaymentMethodsFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/InsertPaymentMethodsFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[InsertPaymentMethodsFromJson](@PaymentMethods NVARCHAR(MAX), @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	INSERT INTO Application.PaymentMethods(PaymentMethodName,LastEditedBy)
			OUTPUT  inserted.PaymentMethodID
			SELECT PaymentMethodName,@UserID
			FROM OPENJSON(@PaymentMethods)
				WITH (PaymentMethodName nvarchar(50))
END
```