-- Source: DW:Integration.MigrateStagedOrderData  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/MigrateStagedOrderData.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

UPDATE o
        SET o.[City Key] = COALESCE((SELECT TOP(1) c.[City Key]
                                     FROM Dimension.City AS c
                                     WHERE c.[WWI City ID] = o.[WWI City ID]
                                     AND o.[Last Modified When] > c.[Valid From]
                                     AND o.[Last Modified When] <= c.[Valid To]
									 ORDER BY c.[Valid From]), 0),
            o.[Customer Key] = COALESCE((SELECT TOP(1) c.[Customer Key]
                                         FROM Dimension.Customer AS c
                                         WHERE c.[WWI Customer ID] = o.[WWI Customer ID]
                                         AND o.[Last Modified When] > c.[Valid From]
                                         AND o.[Last Modified When] <= c.[Valid To]
    									 ORDER BY c.[Valid From]), 0),
            o.[Stock Item Key] = COALESCE((SELECT TOP(1) si.[Stock Item Key]
                                           FROM Dimension.[Stock Item] AS si
                                           WHERE si.[WWI Stock Item ID] = o.[WWI Stock Item ID]
                                           AND o.[Last Modified When] > si.[Valid From]
                                           AND o.[Last Modified When] <= si.[Valid To]
					                       ORDER BY si.[Valid From]), 0),
            o.[Salesperson Key] = COALESCE((SELECT TOP(1) e.[Employee Key]
                                         FROM Dimension.Employee AS e
                                         WHERE e.[WWI Employee ID] = o.[WWI Salesperson ID]
                                         AND o.[Last Modified When] > e.[Valid From]
                                         AND o.[Last Modified When] <= e.[Valid To]
									     ORDER BY e.[Valid From]), 0),
            o.[Picker Key] = COALESCE((SELECT TOP(1) e.[Employee Key]
                                       FROM Dimension.Employee AS e
                                       WHERE e.[WWI Employee ID] = o.[WWI Picker ID]
                                       AND o.[Last Modified When] > e.[Valid From]
                                       AND o.[Last Modified When] <= e.[Valid To]
									   ORDER BY e.[Valid From]), 0)
    FROM Integration.Order_Staging AS o;

DELETE o
    FROM Fact.`Order` AS o
    WHERE o.[WWI Order ID] IN (SELECT [WWI Order ID] FROM Integration.Order_Staging);

Insert all current details for these orders

    INSERT Fact.`Order`
        ([City Key], [Customer Key], [Stock Item Key], [Order Date Key], [Picked Date Key],
         [Salesperson Key], [Picker Key], [WWI Order ID], [WWI Backorder ID], `Description`,
         Package, Quantity, [Unit Price], [Tax Rate], [Total Excluding Tax], [Tax Amount],
         [Total Including Tax], [Lineage Key])
    SELECT [City Key], [Customer Key], [Stock Item Key], [Order Date Key], [Picked Date Key],
           [Salesperson Key], [Picker Key], [WWI Order ID], [WWI Backorder ID], `Description`,
           Package, Quantity, [Unit Price], [Tax Rate], [Total Excluding Tax], [Tax Amount],
           [Total Including Tax], @LineageKey
    FROM Integration.Order_Staging;

UPDATE Integration.Lineage
        SET [Data Load Completed] = SYSDATETIME(),
            [Was Successful] = 1
    WHERE [Lineage Key] = @LineageKey;

UPDATE Integration.[ETL Cutoff]
        SET [Cutoff Time] = (SELECT [Source System Cutoff Time]
                             FROM Integration.Lineage
                             WHERE [Lineage Key] = @LineageKey)
    FROM Integration.[ETL Cutoff]
    WHERE [Table Name] = N'Order';