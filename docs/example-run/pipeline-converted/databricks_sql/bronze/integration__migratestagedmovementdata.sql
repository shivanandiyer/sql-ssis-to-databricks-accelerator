-- Source: DW:Integration.MigrateStagedMovementData  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/MigrateStagedMovementData.sql)
-- Split 1 of 2: SQL transformation logic extracted from an orchestration-heavy
-- stored procedure (rule: separate SQL transformation from workflow orchestration).
-- The CURSOR/WHILE control flow that drove row-by-row iteration in the source is
-- NOT reproduced here — see the companion PySpark orchestration file, which expresses
-- the same iteration as a set-based MERGE or a small parameterised loop.

UPDATE m
        SET m.[Stock Item Key] = COALESCE((SELECT TOP(1) si.[Stock Item Key]
                                           FROM Dimension.[Stock Item] AS si
                                           WHERE si.[WWI Stock Item ID] = m.[WWI Stock Item ID]
                                           AND m.[Last Modifed When] > si.[Valid From]
                                           AND m.[Last Modifed When] <= si.[Valid To]
									       ORDER BY si.[Valid From]), 0),
            m.[Customer Key] = COALESCE((SELECT TOP(1) c.[Customer Key]
                                         FROM Dimension.Customer AS c
                                         WHERE c.[WWI Customer ID] = m.[WWI Customer ID]
                                         AND m.[Last Modifed When] > c.[Valid From]
                                         AND m.[Last Modifed When] <= c.[Valid To]
									     ORDER BY c.[Valid From]), 0),
            m.[Supplier Key] = COALESCE((SELECT TOP(1) s.[Supplier Key]
                                         FROM Dimension.Supplier AS s
                                         WHERE s.[WWI Supplier ID] = m.[WWI Supplier ID]
                                         AND m.[Last Modifed When] > s.[Valid From]
                                         AND m.[Last Modifed When] <= s.[Valid To]
									     ORDER BY s.[Valid From]), 0),
            m.[Transaction Type Key] = COALESCE((SELECT TOP(1) tt.[Transaction Type Key]
                                                 FROM Dimension.[Transaction Type] AS tt
                                                 WHERE tt.[WWI Transaction Type ID] = m.[WWI Transaction Type ID]
                                                 AND m.[Last Modifed When] > tt.[Valid From]
                                                 AND m.[Last Modifed When] <= tt.[Valid To]
									             ORDER BY tt.[Valid From]), 0)
    FROM Integration.Movement_Staging AS m;

Merge the data into the fact table

    MERGE Fact.Movement AS m
    USING Integration.Movement_Staging AS ms
    ON m.[WWI Stock Item Transaction ID] = ms.[WWI Stock Item Transaction ID]
    WHEN MATCHED THEN
        UPDATE SET m.[Date Key] = ms.[Date Key],
                   m.[Stock Item Key] = ms.[Stock Item Key],
                   m.[Customer Key] = ms.[Customer Key],
                   m.[Supplier Key] = ms.[Supplier Key],
                   m.[Transaction Type Key] = ms.[Transaction Type Key],
                   m.[WWI Invoice ID] = ms.[WWI Invoice ID],
                   m.[WWI Purchase Order ID] = ms.[WWI Purchase Order ID],
                   m.Quantity = ms.Quantity,
                   m.[Lineage Key] = @LineageKey
    WHEN NOT MATCHED THEN
        INSERT ([Date Key], [Stock Item Key], [Customer Key], [Supplier Key], [Transaction Type Key],
                [WWI Stock Item Transaction ID], [WWI Invoice ID], [WWI Purchase Order ID], Quantity, [Lineage Key])
        VALUES (ms.[Date Key], ms.[Stock Item Key], ms.[Customer Key], ms.[Supplier Key], ms.[Transaction Type Key],
                ms.[WWI Stock Item Transaction ID], ms.[WWI Invoice ID], ms.[WWI Purchase Order ID], ms.Quantity, @LineageKey);

UPDATE Integration.Lineage
        SET [Data Load Completed] = SYSDATETIME(),
            [Was Successful] = 1
    WHERE [Lineage Key] = @LineageKey;

UPDATE Integration.[ETL Cutoff]
        SET [Cutoff Time] = (SELECT [Source System Cutoff Time]
                             FROM Integration.Lineage
                             WHERE [Lineage Key] = @LineageKey)
    FROM Integration.[ETL Cutoff]
    WHERE [Table Name] = N'Movement';