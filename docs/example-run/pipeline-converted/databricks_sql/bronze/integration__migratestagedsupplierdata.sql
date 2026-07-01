-- Source: DW:Integration.MigrateStagedSupplierData  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/MigrateStagedSupplierData.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

UPDATE s
        SET s.[Valid To] = rtco.[Valid From]
    FROM Dimension.`Supplier` AS s
    INNER JOIN RowsToCloseOff AS rtco
    ON s.[WWI Supplier ID] = rtco.[WWI Supplier ID]
    WHERE s.[Valid To] = @EndOfTime;

INSERT Dimension.`Supplier`
        ([WWI Supplier ID], Supplier, Category, [Primary Contact], [Supplier Reference],
         [Payment Days], [Postal Code], [Valid From], [Valid To], [Lineage Key])
    SELECT [WWI Supplier ID], Supplier, Category, [Primary Contact], [Supplier Reference],
           [Payment Days], [Postal Code], [Valid From], [Valid To],
           @LineageKey
    FROM Integration.Supplier_Staging;

UPDATE Integration.Lineage
        SET [Data Load Completed] = SYSDATETIME(),
            [Was Successful] = 1
    WHERE [Lineage Key] = @LineageKey;

UPDATE Integration.[ETL Cutoff]
        SET [Cutoff Time] = (SELECT [Source System Cutoff Time]
                             FROM Integration.Lineage
                             WHERE [Lineage Key] = @LineageKey)
    FROM Integration.[ETL Cutoff]
    WHERE [Table Name] = N'Supplier';