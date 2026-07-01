-- Source: DW:Integration.MigrateStagedPurchaseData  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/MigrateStagedPurchaseData.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

UPDATE p
        SET p.[Supplier Key] = COALESCE((SELECT TOP(1) s.[Supplier Key]
                                     FROM Dimension.Supplier AS s
                                     WHERE s.[WWI Supplier ID] = p.[WWI Supplier ID]
                                     AND p.[Last Modified When] > s.[Valid From]
                                     AND p.[Last Modified When] <= s.[Valid To]
									 ORDER BY s.[Valid From]), 0),
            p.[Stock Item Key] = COALESCE((SELECT TOP(1) si.[Stock Item Key]
                                           FROM Dimension.[Stock Item] AS si
                                           WHERE si.[WWI Stock Item ID] = p.[WWI Stock Item ID]
                                           AND p.[Last Modified When] > si.[Valid From]
                                           AND p.[Last Modified When] <= si.[Valid To]
									       ORDER BY si.[Valid From]), 0)
    FROM Integration.Purchase_Staging AS p;

DELETE p
    FROM Fact.Purchase AS p
    WHERE p.[WWI Purchase Order ID] IN (SELECT [WWI Purchase Order ID] FROM Integration.Purchase_Staging);

Insert all current details for these purchase orders

    INSERT Fact.Purchase
        ([Date Key], [Supplier Key], [Stock Item Key], [WWI Purchase Order ID], [Ordered Outers], [Ordered Quantity],
         [Received Outers], Package, [Is Order Finalized], [Lineage Key])
    SELECT [Date Key], [Supplier Key], [Stock Item Key], [WWI Purchase Order ID], [Ordered Outers], [Ordered Quantity],
           [Received Outers], Package, [Is Order Finalized], @LineageKey
    FROM Integration.Purchase_Staging;

UPDATE Integration.Lineage
        SET [Data Load Completed] = SYSDATETIME(),
            [Was Successful] = 1
    WHERE [Lineage Key] = @LineageKey;

UPDATE Integration.[ETL Cutoff]
        SET [Cutoff Time] = (SELECT [Source System Cutoff Time]
                             FROM Integration.Lineage
                             WHERE [Lineage Key] = @LineageKey)
    FROM Integration.[ETL Cutoff]
    WHERE [Table Name] = N'Purchase';