# Review Required: OLTP:DataLoadSimulation.GetRandomStreetSuffix

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/GetRandomStreetSuffix.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. years), a Python for-loop generating one MERGE per iteration.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [DataLoadSimulation].[GetRandomStreetSuffix]
@randomStreetSuffix NVARCHAR(20) OUTPUT
AS
BEGIN
/*
Notes:
  This procedure will randomly select a street suffix from the table
  variable loaded herein.

  While it would be preferable to have implemented this as a function,
  the NEWID mechanism needed to make this work are not allowed within
  a function hence the requirement to implement in a stored procedure.

Usage:
  DECLARE @r AS NVARCHAR(20)
  EXEC [DataLoadSimulation].[GetRandomStreetSuffix] @randomStreetSuffix = @r OUTPUT;
  SELECT @r
*/

  DECLARE @streetSuffix TABLE (street NVARCHAR(20))

  INSERT INTO @streetSuffix
  VALUES ('Street')
       , ('Road')
       , ('Avenue')
       , ('Lane')
       , ('Drive')
       , ('Boulevard')
       , ('Court')
       , ('Circle')
       , ('Place')
       , ('Trail')
       , ('Path')
       , ('Loop')
       , ('Way')
       , ('Highway')
       , ('Alley')
       ;

  SELECT TOP 1 @randomStreetSuffix = street FROM @streetSuffix ORDER BY NEWID()
  RETURN

END;
```