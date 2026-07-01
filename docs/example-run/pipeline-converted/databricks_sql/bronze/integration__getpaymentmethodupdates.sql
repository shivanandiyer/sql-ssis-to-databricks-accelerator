-- Source: OLTP:Integration.GetPaymentMethodUpdates  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Integration/Stored Procedures/GetPaymentMethodUpdates.sql)
-- Split 1 of 2: SQL transformation logic extracted from an orchestration-heavy
-- stored procedure (rule: separate SQL transformation from workflow orchestration).
-- The CURSOR/WHILE control flow that drove row-by-row iteration in the source is
-- NOT reproduced here — see the companion PySpark orchestration file, which expresses
-- the same iteration as a set-based MERGE or a small parameterised loop.

INSERT #PaymentMethodChanges
            ([WWI Payment Method ID], [Payment Method], [Valid From], [Valid To])
        SELECT p.PaymentMethodID, p.PaymentMethodName, p.ValidFrom, p.ValidTo
        FROM `Application`.PaymentMethods FOR SYSTEM_TIME AS OF @ValidFrom AS p
        WHERE p.PaymentMethodID = @PaymentMethodID;

UPDATE cc
    SET [Valid To] = COALESCE((SELECT MIN([Valid From]) FROM #PaymentMethodChanges AS cc2
                                                        WHERE cc2.[WWI Payment Method ID] = cc.[WWI Payment Method ID]
                                                        AND cc2.[Valid From] > cc.[Valid From]), @EndOfTime)
    FROM #PaymentMethodChanges AS cc;