-- Source: DW:Integration.MigrateStagedCityData  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/MigrateStagedCityData.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

UPDATE c
        SET c.[Valid To] = rtco.[Valid From]
    FROM Dimension.City AS c
    INNER JOIN RowsToCloseOff AS rtco
    ON c.[WWI City ID] = rtco.[WWI City ID]
    WHERE c.[Valid To] = @EndOfTime;

INSERT Dimension.City
        ([WWI City ID], City, [State Province], Country, Continent,
         [Sales Territory], Region, Subregion, `Location`,
         [Latest Recorded Population], [Valid From], [Valid To],
         [Lineage Key])
    SELECT [WWI City ID], City, [State Province], Country, Continent,
           [Sales Territory], Region, Subregion, `Location`,
           [Latest Recorded Population], [Valid From], [Valid To],
           @LineageKey
    FROM Integration.City_Staging;

UPDATE Integration.Lineage
        SET [Data Load Completed] = SYSDATETIME(),
            [Was Successful] = 1
    WHERE [Lineage Key] = @LineageKey;

UPDATE Integration.[ETL Cutoff]
        SET [Cutoff Time] = (SELECT [Source System Cutoff Time]
                             FROM Integration.Lineage
                             WHERE [Lineage Key] = @LineageKey)
    FROM Integration.[ETL Cutoff]
    WHERE [Table Name] = N'City';