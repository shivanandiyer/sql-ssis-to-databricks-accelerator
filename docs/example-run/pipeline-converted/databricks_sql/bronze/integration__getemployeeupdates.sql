-- Source: OLTP:Integration.GetEmployeeUpdates  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Integration/Stored Procedures/GetEmployeeUpdates.sql)
-- Split 1 of 2: SQL transformation logic extracted from an orchestration-heavy
-- stored procedure (rule: separate SQL transformation from workflow orchestration).
-- The CURSOR/WHILE control flow that drove row-by-row iteration in the source is
-- NOT reproduced here — see the companion PySpark orchestration file, which expresses
-- the same iteration as a set-based MERGE or a small parameterised loop.

INSERT #EmployeeChanges
            ([WWI Employee ID], Employee, [Preferred Name], [Is Salesperson], Photo,
             [Valid From], [Valid To])
        SELECT p.PersonID, p.FullName, p.PreferredName, p.IsSalesperson, p.Photo,
               p.ValidFrom, p.ValidTo
        FROM `Application`.People FOR SYSTEM_TIME AS OF @ValidFrom AS p
        WHERE p.PersonID = @PersonID;

UPDATE cc
    SET [Valid To] = COALESCE((SELECT MIN([Valid From]) FROM #EmployeeChanges AS cc2
                                                        WHERE cc2.[WWI Employee ID] = cc.[WWI Employee ID]
                                                        AND cc2.[Valid From] > cc.[Valid From]), @EndOfTime)
    FROM #EmployeeChanges AS cc;