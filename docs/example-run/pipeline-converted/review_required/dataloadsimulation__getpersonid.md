# Review Required: OLTP:DataLoadSimulation.GetPersonID

- **Object type:** SCALAR_FUNCTION
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Functions/GetPersonID.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UDF equivalent — converted to a PySpark UDF stub requiring manual implementation of the equivalent access-control or looping logic using Unity Catalog row/column-level security or PySpark control flow.
- Original function is called inline from T-SQL SELECT statements — registered via spark.udf.register('GetPersonID', ...) so it remains SQL-callable after conversion, rather than only usable from PySpark DataFrame code.

## Source DDL (for reference)

```sql
CREATE FUNCTION [DataLoadSimulation].[GetPersonID]
( @FullName NVARCHAR(50) )
RETURNS INT
AS
BEGIN
/*
Notes:
  Returns the person id for the passed in full name

Usage:
  DECLARE @myPersonId INT = [DataLoadSimulation].[GetPersonID] ('Hubert Helms')
  SELECT @myPersonId

*/
  DECLARE @PerId INT

  SELECT TOP 1
         @PerId = PersonID
    FROM [Application].[People]
   WHERE FullName = @FullName
     AND ValidTo = '99991231 23:59:59.9999999'

  RETURN @PerId

END
```