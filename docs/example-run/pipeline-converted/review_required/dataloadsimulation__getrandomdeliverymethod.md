# Review Required: OLTP:DataLoadSimulation.GetRandomDeliveryMethod

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/GetRandomDeliveryMethod.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [DataLoadSimulation].[GetRandomDeliveryMethod]
@RandomDeliveryMethod INT OUTPUT
AS
BEGIN
/*
Notes:
  Selects a random delivery method.

  As with other similar procs, we have to use a proc as opposed
  to a function as random tools such as NEWID and RAND don't work
  in functions

Usage:
  DECLARE @DeliveryMethod INT
  EXEC [DataLoadSimulation].[GetRandomDeliveryMethod]
    @RandomDeliveryMethod = @DeliveryMethod OUTPUT
  SELECT @DeliveryMethod

*/
  SELECT TOP (1) @RandomDeliveryMethod = [DeliveryMethodID]
    FROM [Application].[DeliveryMethods]
   WHERE ValidTo = '99991231 23:59:59.9999999'
   ORDER BY NEWID()

  RETURN

END
```