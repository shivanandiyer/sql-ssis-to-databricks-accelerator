-- Source: OLTP:Integration.GetCityUpdates  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Integration/Stored Procedures/GetCityUpdates.sql)
-- Split 1 of 2: SQL transformation logic extracted from an orchestration-heavy
-- stored procedure (rule: separate SQL transformation from workflow orchestration).
-- The CURSOR/WHILE control flow that drove row-by-row iteration in the source is
-- NOT reproduced here — see the companion PySpark orchestration file, which expresses
-- the same iteration as a set-based MERGE or a small parameterised loop.

INSERT #CityChanges
            ([WWI City ID], City, [State Province], Country, Continent, [Sales Territory], Region, Subregion,
             `Location`, [Latest Recorded Population], [Valid From], [Valid To])
        SELECT c.CityID, c.CityName, sp.StateProvinceName, co.CountryName, co.Continent, sp.SalesTerritory, co.Region, co.Subregion,
               c.`Location`, COALESCE(c.LatestRecordedPopulation, 0), @ValidFrom, NULL
        FROM `Application`.Cities FOR SYSTEM_TIME AS OF @ValidFrom AS c
        INNER JOIN `Application`.StateProvinces FOR SYSTEM_TIME AS OF @ValidFrom AS sp
        ON c.StateProvinceID = sp.StateProvinceID
        INNER JOIN `Application`.Countries FOR SYSTEM_TIME AS OF @ValidFrom AS co
        ON sp.CountryID = co.CountryID
        WHERE co.CountryID = @CountryID;

INSERT #CityChanges
            ([WWI City ID], City, [State Province], Country, Continent, [Sales Territory], Region, Subregion,
             `Location`, [Latest Recorded Population], [Valid From], [Valid To])
        SELECT c.CityID, c.CityName, sp.StateProvinceName, co.CountryName, co.Continent, sp.SalesTerritory, co.Region, co.Subregion,
               c.`Location`, COALESCE(c.LatestRecordedPopulation, 0), @ValidFrom, NULL
        FROM `Application`.Cities FOR SYSTEM_TIME AS OF @ValidFrom AS c
        INNER JOIN `Application`.StateProvinces FOR SYSTEM_TIME AS OF @ValidFrom AS sp
        ON c.StateProvinceID = sp.StateProvinceID
        INNER JOIN `Application`.Countries FOR SYSTEM_TIME AS OF @ValidFrom AS co
        ON sp.CountryID = co.CountryID
        WHERE sp.StateProvinceID = @StateProvinceID;

INSERT #CityChanges
            ([WWI City ID], City, [State Province], Country, Continent, [Sales Territory], Region, Subregion,
             `Location`, [Latest Recorded Population], [Valid From], [Valid To])
        SELECT c.CityID, c.CityName, sp.StateProvinceName, co.CountryName, co.Continent, sp.SalesTerritory, co.Region, co.Subregion,
               c.`Location`, COALESCE(c.LatestRecordedPopulation, 0), @ValidFrom, NULL
        FROM `Application`.Cities FOR SYSTEM_TIME AS OF @ValidFrom AS c
        INNER JOIN `Application`.StateProvinces FOR SYSTEM_TIME AS OF @ValidFrom AS sp
        ON c.StateProvinceID = sp.StateProvinceID
        INNER JOIN `Application`.Countries FOR SYSTEM_TIME AS OF @ValidFrom AS co
        ON sp.CountryID = co.CountryID
        WHERE c.CityID = @CityID;

UPDATE cc
    SET [Valid To] = COALESCE((SELECT MIN([Valid From]) FROM #CityChanges AS cc2
                                                        WHERE cc2.[WWI City ID] = cc.[WWI City ID]
                                                        AND cc2.[Valid From] > cc.[Valid From]), @EndOfTime)
    FROM #CityChanges AS cc;