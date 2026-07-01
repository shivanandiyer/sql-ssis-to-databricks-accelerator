# Review Required: OLTP:DataLoadSimulation.GetRandomSalesPersonID

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/GetRandomSalesPersonID.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [DataLoadSimulation].[GetRandomSalesPersonID]
@RandomSalesPersonID INT OUTPUT
AS
BEGIN
/*
Notes:
  Selects a random sales person ID.

  As with other similar procs, we have to use a proc as opposed
  to a function as random tools such as NEWID and RAND don't work
  in functions

Usage:
  DECLARE @SalesPersonID INT
  EXEC [DataLoadSimulation].[GetRandomSalesPersonID]
    @RandomSalesPersonID = @SalesPersonID OUTPUT
  SELECT @SalesPersonID

*/

  SELECT TOP 1
         @RandomSalesPersonID = PersonID
    FROM [Application].[People]
   WHERE IsSalesperson <> 0
     AND ValidTo = '99991231 23:59:59.9999999'
   ORDER BY NEWID()

  RETURN

END
```