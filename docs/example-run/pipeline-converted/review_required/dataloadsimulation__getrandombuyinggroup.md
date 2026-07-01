# Review Required: OLTP:DataLoadSimulation.GetRandomBuyingGroup

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/GetRandomBuyingGroup.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [DataLoadSimulation].[GetRandomBuyingGroup]
  @BuyingGroupID   INT          OUTPUT
, @BuyingGroupName NVARCHAR(50) OUTPUT
AS
BEGIN
/*
Notes:
  Retrieves a random buying group.
  1 is reserved for individual buyers, so we want to
  get an ID above that.

Usage:
  DECLARE @BuyingGroupID INT
  DECLARE @BuyingGroupName NVARCHAR(50)
  EXEC [DataLoadSimulation].[GetRandomBuyingGroup]
      @BuyingGroupID   = @BuyingGroupID   OUTPUT
    , @BuyingGroupName = @BuyingGroupName OUTPUT
  SELECT @BuyingGroupID, @BuyingGroupName
*/

  SELECT TOP 1
         @BuyingGroupID = [BuyingGroupID]
       , @BuyingGroupName = [BuyingGroupName]
    FROM [Sales].[BuyingGroups]
   WHERE [ValidTo] = '9999-12-31 23:59:59.9999999'
     AND [BuyingGroupID] > 1
   ORDER BY NEWID()

END
```