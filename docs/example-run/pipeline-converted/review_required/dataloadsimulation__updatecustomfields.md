# Review Required: OLTP:DataLoadSimulation.UpdateCustomFields

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/UpdateCustomFields.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- CURSOR — row-by-row processing; rewrite as a set-based DataFrame transformation (groupBy/window functions) or, if truly row-oriented, a Python loop over a collected (small) result set.
- WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. years), a Python for-loop generating one MERGE per iteration.

## Source DDL (for reference)

```sql
-- Note this procedure is not included in the regular build, it
-- is called during the post deployment process.
-- This is due to the fact it updates temporal tables, and SSDT
-- will throw up an error when this occurs, despite the fact we
-- have procedures to deactivate the temporal tables and reactivate
-- when done.
DROP PROCEDURE IF EXISTS DataLoadSimulation.UpdateCustomFields;
GO

CREATE PROCEDURE DataLoadSimulation.UpdateCustomFields
@CurrentDateTime AS date
WITH EXECUTE AS OWNER
AS
BEGIN
    DECLARE @StartingWhen datetime2(7) = CAST(@CurrentDateTime AS date);

    SET @StartingWhen = DATEADD(hour, 23, @StartingWhen);

    -- Populate custom data for stock items

    UPDATE Warehouse.StockItems
    SET CustomFields = N'{ "CountryOfManufacture": '
                     + CASE WHEN IsChillerStock <> 0 THEN N'"USA", "ShelfLife": "7 days"'
                            WHEN StockItemName LIKE N'%USB food%' THEN N'"Japan"'
                            ELSE N'"China"'
                       END
                     + N', "Tags": []'
                     + CASE WHEN Size IN (N'S', N'XS', N'XXS', N'3XS') THEN N', "Range": "Children"'
                            WHEN Size IN (N'M') THEN N', "Range": "Teens/Young Adult"'
                            WHEN Size IN (N'L', N'XL', N'XXL', N'3XL', N'4XL', N'5XL', N'6XL', N'7XL') THEN N', "Range": "Adult"'
                            ELSE N''
                       END
                     + CASE WHEN StockItemName LIKE N'RC %' THEN N', "MinimumAge": "10"'
                            ELSE N''
                       END
                     + N' }',
        ValidFrom = @StartingWhen;

    SET @StartingWhen = DATEADD(minute, 1, @StartingWhen);

    UPDATE Warehouse.StockItems
    SET CustomFields = JSON_MODIFY(CustomFields, N'append $.Tags', N'Radio Control'),
        ValidFrom = @StartingWhen
    WHERE StockItemName LIKE N'RC %';

    SET @StartingWhen = DATEADD(minute, 1, @StartingWhen);

    UPDATE Warehouse.StockItems
    SET CustomFields = JSON_MODIFY(CustomFields, N'append $.Tags', N'Realistic Sound'),
        ValidFrom = @StartingWhen
    WHERE StockItemName LIKE N'RC %';

    SET @StartingWhen = DATEADD(minute, 1, @StartingWhen);

    UPDATE Warehouse.StockItems
    SET CustomFields = JSON_MODIFY(CustomFields, N'append $.Tags', N'Vintage'),
        ValidFrom = @StartingWhen
    WHERE StockItemName LIKE N'%vintage%';

    SET @StartingWhen = DATEADD(minute, 1, @StartingWhen);

    UPDATE Warehouse.StockItems
    SET CustomFields = JSON_MODIFY(CustomFields, N'append $.Tags', N'Halloween Fun'),
        ValidFrom = @StartingWhen
    WHERE StockItemName LIKE N'%halloween%';

    SET @StartingWhen = DATEADD(minute, 1, @StartingWhen);

    UPDATE Warehouse.StockItems
    SET CustomFields = JSON_MODIFY(CustomFields, N'append $.Tags', N'Super Value'),
        ValidFrom = @StartingWhen
    WHERE StockItemName LIKE N'%pack of%';

    SET @StartingWhen = DATEADD(minute, 1, @StartingWhen);

    UPDATE Warehouse.Stock
```