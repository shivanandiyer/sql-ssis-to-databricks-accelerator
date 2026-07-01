# Review Required: OLTP:Integration.GetCityUpdates

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Integration/Stored Procedures/GetCityUpdates.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- CURSOR — row-by-row processing; rewrite as a set-based DataFrame transformation (groupBy/window functions) or, if truly row-oriented, a Python loop over a collected (small) result set.
- WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. years), a Python for-loop generating one MERGE per iteration.
- Temp table — replace with a PySpark DataFrame (if used only within the procedure body) or a Delta table in a scratch/staging schema (if state must persist across steps).
- Orchestration-heavy procedure split per conversion rule 4: SQL transformation logic and workflow orchestration logic are emitted as separate files.

## Source DDL (for reference)

```sql
CREATE PROCEDURE Integration.GetCityUpdates
@LastCutoff datetime2(7),
@NewCutoff datetime2(7)
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @EndOfTime datetime2(7) = '99991231 23:59:59.9999999';
    DECLARE @InitialLoadDate date = '20200101';

    CREATE TABLE #CityChanges
    (
        [WWI City ID] int,
        City nvarchar(50),
        [State Province] nvarchar(50),
        Country nvarchar(50),
        Continent nvarchar(30),
        [Sales Territory] nvarchar(50),
        Region nvarchar(30),
        Subregion nvarchar(30),
        [Location] geography,
        [Latest Recorded Population] bigint,
        [Valid From] datetime2(7),
        [Valid To] datetime2(7) NULL
    );

    DECLARE @CountryID int;
    DECLARE @StateProvinceID int;
    DECLARE @CityID int;
    DECLARE @ValidFrom datetime2(7);

    -- first need to find any country changes that have occurred since initial load

    DECLARE CountryChangeList CURSOR FAST_FORWARD READ_ONLY
    FOR
    SELECT co.CountryID,
           co.ValidFrom
    FROM [Application].Countries_Archive AS co
    WHERE co.ValidFrom > @LastCutoff
    AND co.ValidFrom <= @NewCutoff
    AND co.ValidFrom <> @InitialLoadDate
    UNION ALL
    SELECT co.CountryID,
           co.ValidFrom
    FROM [Application].Countries AS co
    WHERE co.ValidFrom > @LastCutoff
    AND co.ValidFrom <= @NewCutoff
    AND co.ValidFrom <> @InitialLoadDate
    ORDER BY ValidFrom;

    OPEN CountryChangeList;
    FETCH NEXT FROM CountryChangeList INTO @CountryID, @ValidFrom;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        INSERT #CityChanges
            ([WWI City ID], City, [State Province], Country, Continent, [Sales Territory], Region, Subregion,
             [Location], [Latest Recorded Population], [Valid From], [Valid To])
        SELECT c.CityID, c.CityName, sp.StateProvinceName, co.CountryName, co.Continent, sp.SalesTerritory, co.Region, co.Subregion,
               c.[Location], COALESCE(c.LatestRecordedPopulation, 0), @ValidFrom, NULL
        FROM [Application].Cities FOR SYSTEM_TIME AS OF @ValidFrom AS c
        INNER JOIN [Application].StateProvinces FOR SYSTEM_TIME AS OF @ValidFrom AS sp
        ON c.StateProvinceID = sp.StateProvinceID
        INNER JOIN [Application].Countries FOR SYSTEM_TIME AS OF @ValidFrom AS co
        ON sp.CountryID = co.CountryID
        WHERE co.CountryID = @CountryID;

        FETCH NEXT FROM CountryChangeList INTO @CountryID, @ValidFrom;
    END;

    CLOSE CountryChangeList;
    DEALLOCATE CountryChangeList;

    -- next need to find any stateprovince changes that have occurred since initial load

    DECLARE StateProvinceChangeList CURSOR FAST_FORWARD READ_ONLY
    FOR
    SELECT sp.StateProvinceID,
           sp.ValidFrom
    FROM [Application].StateProvinces_Archive AS sp
    WHERE sp.ValidFrom > @LastCutoff
    AND sp.ValidFrom <= @NewCutoff
    AND sp.ValidFrom <> @InitialLoadDate
    UNION ALL
    SELECT sp.StateProvinceID,
           sp.ValidFr
```