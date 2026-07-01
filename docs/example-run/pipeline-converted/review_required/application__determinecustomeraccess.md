# Review Required: OLTP:Application.DetermineCustomerAccess

- **Object type:** TVF_INLINE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Functions/DetermineCustomerAccess.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UDF equivalent — converted to a PySpark UDF stub requiring manual implementation of the equivalent access-control or looping logic using Unity Catalog row/column-level security or PySpark control flow.
- Original function is called inline from T-SQL SELECT statements — registered via spark.udf.register('DetermineCustomerAccess', ...) so it remains SQL-callable after conversion, rather than only usable from PySpark DataFrame code.

## Source DDL (for reference)

```sql
CREATE FUNCTION [Application].DetermineCustomerAccess(@CityID int)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN (SELECT 1 AS AccessResult
        WHERE IS_ROLEMEMBER(N'db_owner') <> 0
        OR IS_ROLEMEMBER((SELECT sp.SalesTerritory
                          FROM [Application].Cities AS c
                          INNER JOIN [Application].StateProvinces AS sp
                          ON c.StateProvinceID = sp.StateProvinceID
                          WHERE c.CityID = @CityID) + N' Sales') <> 0
	    OR ((ORIGINAL_LOGIN() = N'Website' OR ORIGINAL_LOGIN() = N'WebApi')
		    AND EXISTS (SELECT 1
		                FROM [Application].Cities AS c
				        INNER JOIN [Application].StateProvinces AS sp
				        ON c.StateProvinceID = sp.StateProvinceID
				        WHERE c.CityID = @CityID
				        AND sp.SalesTerritory = SESSION_CONTEXT(N'SalesTerritory'))));
```