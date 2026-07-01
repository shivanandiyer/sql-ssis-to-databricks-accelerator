# Review Required: OLTP:DataLoadSimulation.MakeTemporalChanges

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/MakeTemporalChanges.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. years), a Python for-loop generating one MERGE per iteration.

## Source DDL (for reference)

```sql
-- Note this procedure is not included in the regular build, it
-- is called during the post deployment process.
-- This is due to the fact it updates temporal tables, and SSDT
-- will throw up an error when this occurs, despite the fact we
-- have procedures to deactivate the temporal tables and reactivate
-- when done.
DROP PROCEDURE IF EXISTS DataLoadSimulation.MakeTemporalChanges;
GO

CREATE PROCEDURE DataLoadSimulation.MakeTemporalChanges
@CurrentDateTime datetime2(7),
@StartingWhen datetime,
@EndOfTime datetime2(7),
@IsSilentMode bit
AS
BEGIN

    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @Counter int;
    DECLARE @RowsToModify int;
    DECLARE @StaffMember int = (SELECT TOP(1) PersonID FROM [Application].People WHERE IsEmployee <> 0 ORDER BY NEWID());

    IF DAY(@StartingWhen) = 1 AND MONTH(@StartingWhen) = 7
    BEGIN
        SET @Counter = 0;
        SET @RowsToModify = CEILING(RAND() * 20);

        WHILE @Counter < @RowsToModify
        BEGIN
            UPDATE [Application].Cities
            SET LatestRecordedPopulation = LatestRecordedPopulation * 1.04,
                LastEditedBy = @StaffMember,
                ValidFrom = @StartingWhen
            WHERE CityID = (SELECT TOP(1) CityID FROM [Application].Cities ORDER BY NEWID());
            SET @Counter += 1;
        END;
    END;

    IF DAY(@StartingWhen) = 1 AND MONTH(@StartingWhen) = 7
    BEGIN
        SET @Counter = 0;
        SET @RowsToModify = CEILING(RAND() * 20);

        WHILE @Counter < @RowsToModify
        BEGIN
            UPDATE [Application].StateProvinces
            SET LatestRecordedPopulation = LatestRecordedPopulation * 1.04,
                LastEditedBy = @StaffMember,
                ValidFrom = @StartingWhen
            WHERE StateProvinceID = (SELECT TOP(1) StateProvinceID FROM [Application].StateProvinces ORDER BY NEWID());
            SET @Counter += 1;
        END;
    END;

    IF DAY(@StartingWhen) = 1 AND MONTH(@StartingWhen) = 7
    BEGIN
        SET @Counter = 0;
        SET @RowsToModify = CEILING(RAND() * 20);

        WHILE @Counter < @RowsToModify
        BEGIN
            UPDATE [Application].Countries
            SET LatestRecordedPopulation = LatestRecordedPopulation * 1.04,
                LastEditedBy = @StaffMember,
                ValidFrom = @StartingWhen
            WHERE CountryID = (SELECT TOP(1) CountryID FROM [Application].Countries ORDER BY NEWID());
            SET @Counter += 1;
        END;
    END;

    IF CAST(@StartingWhen AS date) = '20210101'
    BEGIN
        UPDATE [Application].DeliveryMethods
            SET DeliveryMethodName = N'Chilled Van',
                LastEditedBy = @StaffMember,
                ValidFrom = @StartingWhen
            WHERE DeliveryMethodName = N'Van with Chiller';
    END;

    IF CAST(@StartingWhen AS date) = '20220101'
    BEGIN
        UPDATE [Application].PaymentMethods
            SET PaymentMethodName = N'Credit-Card',
                LastEditedBy = @StaffMember,
            
```