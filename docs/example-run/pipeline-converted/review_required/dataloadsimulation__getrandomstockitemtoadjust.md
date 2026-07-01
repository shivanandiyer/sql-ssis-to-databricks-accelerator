# Review Required: OLTP:DataLoadSimulation.GetRandomStockItemToAdjust

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/GetRandomStockItemToAdjust.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [DataLoadSimulation].[GetRandomStockItemToAdjust]
  @QuantityToAdjust    INT
, @StockItemIDToAdjust INT OUTPUT
AS
BEGIN
/*
Notes:
  Selects stock item to adjust ID.

  As with other similar procs, we have to use a proc as opposed
  to a function as random tools such as NEWID and RAND don't work
  in functions

Usage:
  DECLARE @myStockItemIDToAdjust INT
  EXEC [DataLoadSimulation].[GetRandomStockItemToAdjust]
    10, @StockItemIDToAdjust = @myStockItemIDToAdjust OUTPUT
  SELECT @myStockItemIDToAdjust

*/

  SELECT TOP(1)
         @StockItemIDToAdjust = StockItemID
    FROM Warehouse.StockItemHoldings
   WHERE (QuantityOnHand + @QuantityToAdjust) >= 0
   ORDER BY NEWID()

  RETURN

END
```