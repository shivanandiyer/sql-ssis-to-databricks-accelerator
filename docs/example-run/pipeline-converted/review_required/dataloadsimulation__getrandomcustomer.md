# Review Required: OLTP:DataLoadSimulation.GetRandomCustomer

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/GetRandomCustomer.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [DataLoadSimulation].[GetRandomCustomer]
  @RandomCustomerID INT OUTPUT
, @CustomerPrimaryContactPersonID INT OUTPUT
AS
BEGIN
/*
Notes:
  Selects a random sales person ID.

  As with other similar procs, we have to use a proc as opposed
  to a function as random tools such as NEWID and RAND don't work
  in functions

Usage:
  DECLARE @myCustomerID INT
  DECLARE @myCustomerPrimaryContactPersonID INT
  EXEC [DataLoadSimulation].[GetRandomCustomer]
      @RandomCustomerID = @myCustomerID OUTPUT
    , @CustomerPrimaryContactPersonID = @myCustomerPrimaryContactPersonID OUTPUT
  SELECT @myCustomerID, @myCustomerPrimaryContactPersonID

*/

  SELECT TOP(1)
         @RandomCustomerID = c.CustomerID
       , @CustomerPrimaryContactPersonID = c.PrimaryContactPersonID
    FROM Sales.Customers AS c
   WHERE c.IsOnCreditHold = 0
     AND ValidTo = '99991231 23:59:59.9999999'
   ORDER BY NEWID()

  RETURN

END
```