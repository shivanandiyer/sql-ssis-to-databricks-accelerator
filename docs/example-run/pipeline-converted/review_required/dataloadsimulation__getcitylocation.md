# Review Required: OLTP:DataLoadSimulation.GetCityLocation

- **Object type:** SCALAR_FUNCTION
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Functions/GetCityLocation.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UDF equivalent — converted to a PySpark UDF stub requiring manual implementation of the equivalent access-control or looping logic using Unity Catalog row/column-level security or PySpark control flow.
- Original function is called inline from T-SQL SELECT statements — registered via spark.udf.register('GetCityLocation', ...) so it remains SQL-callable after conversion, rather than only usable from PySpark DataFrame code.

## Source DDL (for reference)

```sql
CREATE FUNCTION [DataLoadSimulation].[GetCityLocation]
(@CityID INT)
RETURNS GEOGRAPHY
AS
BEGIN
/*
Notes:
  Returns the location for the passed in city id

Usage:
  DECLARE @myLoc GEOGRAPHY = [DataLoadSimulation].[GetCityLocation] (1)
  SELECT @myLoc

*/

  DECLARE @Loc AS GEOGRAPHY

  SELECT TOP 1 @Loc = [Location]
    FROM [Application].Cities
   WHERE CityID = @CityID

  RETURN @Loc

END
```