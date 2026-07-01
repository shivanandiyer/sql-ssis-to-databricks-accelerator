-- Source: DW:Integration.MigrateStagedTransactionTypeData  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/MigrateStagedTransactionTypeData.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

UPDATE pm
        SET pm.[Valid To] = rtco.[Valid From]
    FROM Dimension.[Transaction Type] AS pm
    INNER JOIN RowsToCloseOff AS rtco
    ON pm.[WWI Transaction Type ID] = rtco.[WWI Transaction Type ID]
    WHERE pm.[Valid To] = @EndOfTime;

INSERT Dimension.[Transaction Type]
        ([WWI Transaction Type ID], [Transaction Type], [Valid From], [Valid To], [Lineage Key])
    SELECT [WWI Transaction Type ID], [Transaction Type], [Valid From], [Valid To],
           @LineageKey
    FROM Integration.TransactionType_Staging;

UPDATE Integration.Lineage
        SET [Data Load Completed] = SYSDATETIME(),
            [Was Successful] = 1
    WHERE [Lineage Key] = @LineageKey;

UPDATE Integration.[ETL Cutoff]
        SET [Cutoff Time] = (SELECT [Source System Cutoff Time]
                             FROM Integration.Lineage
                             WHERE [Lineage Key] = @LineageKey)
    FROM Integration.[ETL Cutoff]
    WHERE [Table Name] = N'Transaction Type';