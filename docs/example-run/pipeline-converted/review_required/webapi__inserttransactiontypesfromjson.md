# Review Required: OLTP:WebApi.InsertTransactionTypesFromJson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/InsertTransactionTypesFromJson.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[InsertTransactionTypesFromJson](@TransactionTypes NVARCHAR(MAX), @UserID int)
WITH EXECUTE AS OWNER
AS BEGIN
	INSERT INTO Application.TransactionTypes(TransactionTypeName,LastEditedBy)
			OUTPUT  inserted.TransactionTypeID
			SELECT TransactionTypeName,@UserID
			FROM OPENJSON(@TransactionTypes)
				WITH (TransactionTypeName nvarchar(50))
END
```