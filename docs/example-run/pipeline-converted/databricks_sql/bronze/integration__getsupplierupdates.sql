-- Source: OLTP:Integration.GetSupplierUpdates  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Integration/Stored Procedures/GetSupplierUpdates.sql)
-- Split 1 of 2: SQL transformation logic extracted from an orchestration-heavy
-- stored procedure (rule: separate SQL transformation from workflow orchestration).
-- The CURSOR/WHILE control flow that drove row-by-row iteration in the source is
-- NOT reproduced here — see the companion PySpark orchestration file, which expresses
-- the same iteration as a set-based MERGE or a small parameterised loop.

INSERT #SupplierChanges
            ([WWI Supplier ID], Supplier, Category, [Primary Contact], [Supplier Reference],
             [Payment Days], [Postal Code], [Valid From], [Valid To])
        SELECT s.SupplierID, s.SupplierName, sc.SupplierCategoryName, p.FullName, s.SupplierReference,
               s.PaymentDays, s.DeliveryPostalCode, s.ValidFrom, s.ValidTo
        FROM Purchasing.Suppliers FOR SYSTEM_TIME AS OF @ValidFrom AS s
        INNER JOIN Purchasing.SupplierCategories FOR SYSTEM_TIME AS OF @ValidFrom AS sc
        ON s.SupplierCategoryID = sc.SupplierCategoryID
        INNER JOIN `Application`.People FOR SYSTEM_TIME AS OF @ValidFrom AS p
        ON s.PrimaryContactPersonID = p.PersonID
        WHERE sc.SupplierCategoryID = @SupplierCategoryID;

INSERT #SupplierChanges
            ([WWI Supplier ID], Supplier, Category, [Primary Contact], [Supplier Reference],
             [Payment Days], [Postal Code], [Valid From], [Valid To])
        SELECT s.SupplierID, s.SupplierName, sc.SupplierCategoryName, p.FullName, s.SupplierReference,
               s.PaymentDays, s.DeliveryPostalCode, s.ValidFrom, s.ValidTo
        FROM Purchasing.Suppliers FOR SYSTEM_TIME AS OF @ValidFrom AS s
        INNER JOIN Purchasing.SupplierCategories FOR SYSTEM_TIME AS OF @ValidFrom AS sc
        ON s.SupplierCategoryID = sc.SupplierCategoryID
        INNER JOIN `Application`.People FOR SYSTEM_TIME AS OF @ValidFrom AS p
        ON s.PrimaryContactPersonID = p.PersonID
        WHERE s.SupplierID = @SupplierID;

UPDATE cc
    SET [Valid To] = COALESCE((SELECT MIN([Valid From]) FROM #SupplierChanges AS cc2
                                                        WHERE cc2.[WWI Supplier ID] = cc.[WWI Supplier ID]
                                                        AND cc2.[Valid From] > cc.[Valid From]), @EndOfTime)
    FROM #SupplierChanges AS cc;