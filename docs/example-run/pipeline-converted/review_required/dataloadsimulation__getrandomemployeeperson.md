# Review Required: OLTP:DataLoadSimulation.GetRandomEmployeePerson

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/GetRandomEmployeePerson.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review


## Source DDL (for reference)

```sql
CREATE PROCEDURE [DataLoadSimulation].[GetRandomEmployeePerson]
  @EmployeePersonID INT OUTPUT
AS
BEGIN
/*
Notes:
  Selects a random person ID.

  As with other similar procs, we have to use a proc as opposed
  to a function as random tools such as NEWID and RAND don't work
  in functions

Usage:
  DECLARE @myEmployeePersonID INT
  EXEC [DataLoadSimulation].[GetRandomEmployeePerson]
      @EmployeePersonID = @myEmployeePersonID OUTPUT
  SELECT @myEmployeePersonID

*/

  SELECT TOP(1)
         @EmployeePersonID = PersonID
    FROM [Application].People
   WHERE IsEmployee <> 0
     AND ValidTo = '99991231 23:59:59.9999999'
   ORDER BY NEWID()

  RETURN

END
```