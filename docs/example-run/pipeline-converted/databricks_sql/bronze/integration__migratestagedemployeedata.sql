-- Source: DW:Integration.MigrateStagedEmployeeData  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/MigrateStagedEmployeeData.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

UPDATE e
        SET e.[Valid To] = rtco.[Valid From]
    FROM Dimension.Employee AS e
    INNER JOIN RowsToCloseOff AS rtco
    ON e.[WWI Employee ID] = rtco.[WWI Employee ID]
    WHERE e.[Valid To] = @EndOfTime;

INSERT Dimension.Employee
        ([WWI Employee ID], Employee, [Preferred Name], [Is Salesperson], Photo, [Valid From], [Valid To], [Lineage Key])
    SELECT [WWI Employee ID], Employee, [Preferred Name], [Is Salesperson], Photo, [Valid From], [Valid To],
           @LineageKey
    FROM Integration.Employee_Staging;

UPDATE Integration.Lineage
        SET [Data Load Completed] = SYSDATETIME(),
            [Was Successful] = 1
    WHERE [Lineage Key] = @LineageKey;

UPDATE Integration.[ETL Cutoff]
        SET [Cutoff Time] = (SELECT [Source System Cutoff Time]
                             FROM Integration.Lineage
                             WHERE [Lineage Key] = @LineageKey)
    FROM Integration.[ETL Cutoff]
    WHERE [Table Name] = N'Employee';