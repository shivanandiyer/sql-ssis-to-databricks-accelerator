# Review Required: OLTP:Integration.GetStockItemUpdates

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Integration/Stored Procedures/GetStockItemUpdates.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- CURSOR — row-by-row processing; rewrite as a set-based DataFrame transformation (groupBy/window functions) or, if truly row-oriented, a Python loop over a collected (small) result set.
- WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. years), a Python for-loop generating one MERGE per iteration.
- Temp table — replace with a PySpark DataFrame (if used only within the procedure body) or a Delta table in a scratch/staging schema (if state must persist across steps).
- Orchestration-heavy procedure split per conversion rule 4: SQL transformation logic and workflow orchestration logic are emitted as separate files.

## Source DDL (for reference)

```sql
CREATE PROCEDURE Integration.GetStockItemUpdates
@LastCutoff datetime2(7),
@NewCutoff datetime2(7)
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @EndOfTime datetime2(7) = '99991231 23:59:59.9999999';

    CREATE TABLE #StockItemChanges
    (
        [WWI Stock Item ID] int,
        [Stock Item] nvarchar(100),
        Color nvarchar(20),
        [Selling Package] nvarchar(50),
        [Buying Package] nvarchar(50),
        Brand nvarchar(50),
        Size nvarchar(20),
        [Lead Time Days] int,
        [Quantity Per Outer] int,
        [Is Chiller Stock] bit,
        Barcode nvarchar(50),
        [Tax Rate] decimal(18,3),
        [Unit Price] decimal(18,2),
        [Recommended Retail Price] decimal(18,2),
        [Typical Weight Per Unit] decimal(18,3),
        Photo varbinary(max),
        [Valid From] datetime2(7),
        [Valid To] datetime2(7)
    );

    DECLARE @StockItemID int;
    DECLARE @ValidFrom datetime2(7);

    -- need to find any StockItem changes that have occurred, including during the initial load

    DECLARE StockItemChangeList CURSOR FAST_FORWARD READ_ONLY
    FOR
    SELECT c.StockItemID,
           c.ValidFrom
    FROM Warehouse.StockItems_Archive AS c
    WHERE c.ValidFrom > @LastCutoff
    AND c.ValidFrom <= @NewCutoff
    UNION ALL
    SELECT c.StockItemID,
           c.ValidFrom
    FROM Warehouse.StockItems AS c
    WHERE c.ValidFrom > @LastCutoff
    AND c.ValidFrom <= @NewCutoff
    ORDER BY ValidFrom;

    OPEN StockItemChangeList;
    FETCH NEXT FROM StockItemChangeList INTO @StockItemID, @ValidFrom;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        INSERT #StockItemChanges
            ([WWI Stock Item ID], [Stock Item], Color, [Selling Package],
             [Buying Package], Brand, Size, [Lead Time Days], [Quantity Per Outer],
             [Is Chiller Stock], Barcode, [Tax Rate], [Unit Price], [Recommended Retail Price],
             [Typical Weight Per Unit], Photo, [Valid From], [Valid To])
        SELECT si.StockItemID, si.StockItemName, c.ColorName, spt.PackageTypeName,
               bpt.PackageTypeName, si.Brand, si.Size, si.LeadTimeDays, si.QuantityPerOuter,
               si.IsChillerStock, si.Barcode, si.TaxRate, si.UnitPrice, si.RecommendedRetailPrice,
               si.TypicalWeightPerUnit, si.Photo, si.ValidFrom, si.ValidTo
        FROM Warehouse.StockItems FOR SYSTEM_TIME AS OF @ValidFrom AS si
        INNER JOIN Warehouse.PackageTypes FOR SYSTEM_TIME AS OF @ValidFrom AS spt
        ON si.UnitPackageID = spt.PackageTypeID
        INNER JOIN Warehouse.PackageTypes FOR SYSTEM_TIME AS OF @ValidFrom AS bpt
        ON si.OuterPackageID = bpt.PackageTypeID
        LEFT OUTER JOIN Warehouse.Colors FOR SYSTEM_TIME AS OF @ValidFrom AS c
        ON si.ColorID = c.ColorID
        WHERE si.StockItemID = @StockItemID;

        FETCH NEXT FROM StockItemChangeList INTO @StockItemID, @ValidFrom;
    END;

    CLOSE StockItemChangeList;
    DEALLOCATE StockItemChangeList;

```