-- Source: DW:Integration.MigrateStagedStockItemData  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/MigrateStagedStockItemData.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

UPDATE s
        SET s.[Valid To] = rtco.[Valid From]
    FROM Dimension.[Stock Item] AS s
    INNER JOIN RowsToCloseOff AS rtco
    ON s.[WWI Stock Item ID] = rtco.[WWI Stock Item ID]
    WHERE s.[Valid To] = @EndOfTime;

INSERT Dimension.[Stock Item]
        ([WWI Stock Item ID], [Stock Item], Color, [Selling Package], [Buying Package],
         Brand, Size, [Lead Time Days], [Quantity Per Outer], [Is Chiller Stock],
         Barcode, [Tax Rate], [Unit Price], [Recommended Retail Price], [Typical Weight Per Unit],
         Photo, [Valid From], [Valid To], [Lineage Key])
    SELECT [WWI Stock Item ID], [Stock Item], Color, [Selling Package], [Buying Package],
           Brand, Size, [Lead Time Days], [Quantity Per Outer], [Is Chiller Stock],
           Barcode, [Tax Rate], [Unit Price], [Recommended Retail Price], [Typical Weight Per Unit],
           Photo, [Valid From], [Valid To],
           @LineageKey
    FROM Integration.StockItem_Staging;

UPDATE Integration.Lineage
        SET [Data Load Completed] = SYSDATETIME(),
            [Was Successful] = 1
    WHERE [Lineage Key] = @LineageKey;

UPDATE Integration.[ETL Cutoff]
        SET [Cutoff Time] = (SELECT [Source System Cutoff Time]
                             FROM Integration.Lineage
                             WHERE [Lineage Key] = @LineageKey)
    FROM Integration.[ETL Cutoff]
    WHERE [Table Name] = N'Stock Item';