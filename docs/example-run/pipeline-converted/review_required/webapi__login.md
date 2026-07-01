# Review Required: OLTP:WebApi.Login

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Stored Procedures/Login.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [WebApi].[Login](@LogonName nvarchar(256), @Password nvarchar(256))
WITH EXECUTE AS OWNER
AS BEGIN
	select  PersonID, PreferredName, IsSalesperson, IsEmployee,
        Territory = JSON_VALUE(CustomFields,'$.PrimarySalesTerritory')
	from Application.People
	where IsPermittedToLogon = 1
	and LogonName = @LogonName
	--and HashedPassword = HASHBYTES(N'SHA2_256', @Password)",
END
```