-- Source: OLTP:Integration.GetTransactionTypeUpdates  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Integration/Stored Procedures/GetTransactionTypeUpdates.sql)
-- Split 1 of 2: SQL transformation logic extracted from an orchestration-heavy
-- stored procedure (rule: separate SQL transformation from workflow orchestration).
-- The CURSOR/WHILE control flow that drove row-by-row iteration in the source is
-- NOT reproduced here — see the companion PySpark orchestration file, which expresses
-- the same iteration as a set-based MERGE or a small parameterised loop.

INSERT #TransactionTypeChanges
            ([WWI Transaction Type ID], [Transaction Type], [Valid From], [Valid To])
        SELECT p.TransactionTypeID, p.TransactionTypeName, p.ValidFrom, p.ValidTo
        FROM `Application`.TransactionTypes FOR SYSTEM_TIME AS OF @ValidFrom AS p
        WHERE p.TransactionTypeID = @TransactionTypeID;

UPDATE cc
    SET [Valid To] = COALESCE((SELECT MIN([Valid From]) FROM #TransactionTypeChanges AS cc2
                                                        WHERE cc2.[WWI Transaction Type ID] = cc.[WWI Transaction Type ID]
                                                        AND cc2.[Valid From] > cc.[Valid From]), @EndOfTime)
    FROM #TransactionTypeChanges AS cc;