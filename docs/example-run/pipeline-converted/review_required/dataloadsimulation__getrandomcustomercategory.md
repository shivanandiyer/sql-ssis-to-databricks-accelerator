# Review Required: OLTP:DataLoadSimulation.GetRandomCustomerCategory

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/GetRandomCustomerCategory.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [DataLoadSimulation].[GetRandomCustomerCategory]
@RandomCustomerCategoryID INT OUTPUT
AS
BEGIN
/*
Notes:
  Selects a random category ID from the customer category table
  for categories other than corporate (we only want the Head Office
  stores to be of type corporate, and that is set in another
  routine).

  As with other similar procs, we have to use a proc as opposed
  to a function as random tools such as NEWID and RAND don't work
  in functions

Usage:
  DECLARE @myCustomerCategoryID AS INT
  EXEC [DataLoadSimulation].[GetRandomCustomerCategory]
    @RandomCustomerCategoryID = @myCustomerCategoryID OUTPUT
  SELECT @myCustomerCategoryID

*/

  SELECT TOP 1
         @RandomCustomerCategoryID = CustomerCategoryID
    FROM [Sales].[CustomerCategories]
   WHERE CustomerCategoryID > 0
     AND CustomerCategoryName <> 'Corporate'
   ORDER BY NEWID()

  RETURN

END
```