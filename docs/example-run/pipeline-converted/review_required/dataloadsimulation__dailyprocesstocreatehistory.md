# Review Required: OLTP:DataLoadSimulation.DailyProcessToCreateHistory

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/DailyProcessToCreateHistory.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. years), a Python for-loop generating one MERGE per iteration.
- Temp table — replace with a PySpark DataFrame (if used only within the procedure body) or a Delta table in a scratch/staging schema (if state must persist across steps).
- TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure handling.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [DataLoadSimulation].[DailyProcessToCreateHistory]
    @StartDate                           date
  , @EndDate                             date
  , @AverageNumberOfCustomerOrdersPerDay int = 30
  , @SaturdayPercentageOfNormalWorkDay   int
  , @SundayPercentageOfNormalWorkDay     int
  , @UpdateCustomFields                  bit
  , @IsSilentMode                        bit
  , @AreDatesPrinted                     bit
  , @MinYearlyGrowthPercent              int = -5
  , @MaxYearlyGrowthPercent              int = 15
  , @MinSeasonalVariationPercent         int = -10
  , @MaxSeasonalVariationPercent         int = 30
  , @MaxDailyVariationPercent            int = 20

AS
BEGIN
    SET NOCOUNT ON;
	SET XACT_ABORT ON;

    DECLARE @CurrentDateTime        datetime2(7) = @StartDate;
    DECLARE @EndOfTime              datetime2(7) =  '99991231 23:59:59.9999999';
    DECLARE @StartingWhen           datetime;
	DECLARE @OldNumberOfCustomerOrders int;
    DECLARE @NumberOfCustomerOrders int;
    DECLARE @IsWeekday              bit;
    DECLARE @IsSaturday             bit;
    DECLARE @IsSunday               bit;
    DECLARE @IsMonday               bit;
    DECLARE @Weekday                int;
    DECLARE @IsStaffOnly            bit;
    DECLARE @DateMessage            nvarchar(256);
	
	-- verify whether orders exist, and if so, compute the avg number of customer orders in the last year
	IF EXISTS (SELECT 1 FROM Sales.Orders)
	BEGIN
		SELECT @OldNumberOfCustomerOrders=	AVG(t.OrderCount)
		FROM (SELECT COUNT(*) AS OrderCount FROM Sales.Orders
			WHERE DATEPART(year,OrderDate) = DATEPART(year,(SELECT MAX(OrderDate) FROM Sales.Orders))
				AND DATEPART(weekday,OrderDate) NOT IN (1,7)
				AND BackorderOrderID IS NULL
			GROUP BY OrderDate) t
	END
	ELSE
		SET @OldNumberOfCustomerOrders = @AverageNumberOfCustomerOrdersPerDay


	/*


	delete from DataLoadSimulation.SeasonVariation
	DECLARE @MinSeasonalVariationPercent int = 7
	DECLARE @MaxSeasonalVariationPercent int = 25
	DECLARE @MinYearlyGrowthPercent int = 3
	DECLARE @MaxYearlyGrowthPercent int = 30
	declare @StartDate date = '20200101'
	declare @EndDate date = '20230101'
	declare @CurrentDateTime datetime2 = @StartDate
	declare @MaxDailyVariationPercent int = 5

	drop table if exists #result
	create table #result
	(OrderDate date, OrderCount int)*/
	
	-- compute actual seasonal variation
	DECLARE @CurrentYear int = DATEPART(year, @StartDate)
	WHILE @CurrentYear <= DATEPART(year, @EndDate)
	BEGIN
		DECLARE @CurrentSeason smallint = 1
		--compute new yearly variation for each year
		DECLARE @YearlyVariation float = 1 + (@MinYearlyGrowthPercent + RAND() * CAST(@MaxYearlyGrowthPercent - @MinYearlyGrowthPercent AS float))/100;
		WHILE @CurrentSeason <= 4
		BEGIN
			IF NOT EXISTS (SELECT 1 FROM DataLoadSimulation.SeasonVariation WHERE [Year]=@CurrentYear and Season=@CurrentSeason)
			BEGIN
				-- compute seasonal variation
				DECLARE @SeasonalVariation float
				SET @SeasonalVariation = 1 + (@MinSeason
```