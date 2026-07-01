# Review Required: OLTP:DataLoadSimulation.AddCustomers

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/AddCustomers.sql
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
DROP PROCEDURE IF EXISTS DataLoadSimulation.AddCustomers;
GO

CREATE PROCEDURE DataLoadSimulation.AddCustomers
@CurrentDateTime datetime2(7),
@StartingWhen datetime,
@EndOfTime datetime2(7),
@IsSilentMode bit
WITH EXECUTE AS OWNER
AS
BEGIN

    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    -- add a customer one in 15 days average
    DECLARE @NumberOfCustomersToAdd int = (SELECT TOP(1) Quantity
                                              FROM (VALUES (0), (0), (0), (0), (0),
                                                           (0), (0), (0), (0), (0),
                                                           (0), (0), (0), (0), (0),
                                                           (0), (0), (0), (0), (0),
                                                           (0), (0), (0), (0), (1)) AS q(Quantity)
                                              ORDER BY NEWID());
    -- Pushed Notifications to calling proc
    --IF @IsSilentMode = 0
    --BEGIN
    --    PRINT N'Adding ' + CAST(@NumberOfCustomersToAdd AS nvarchar(20)) + N' customers for ' + LEFT(CAST(@CurrentDateTime AS NVARCHAR), 10);
    --END;

    DECLARE @Counter INT = 0;
    DECLARE @CityID INT;
    DECLARE @CityName NVARCHAR(max);
    DECLARE @CityStateProvinceID INT;
    DECLARE @CityStateProvinceCode NVARCHAR(5);
    DECLARE @CityStateProvinceName NVARCHAR(50);
    DECLARE @AreaCode INT;
    DECLARE @CustomerCategoryID INT;

    DECLARE @InUseCounter INT = 0;


    DECLARE @CustomerID int;
    DECLARE @PrimaryContactFullName nvarchar(50);
    DECLARE @PrimaryContactPersonID int;
    DECLARE @PrimaryContactFirstName nvarchar(50);
    DECLARE @PrimaryContactLastName AS NVARCHAR(20);
    DECLARE @CustomerName AS NVARCHAR(100);
    DECLARE @DeliveryMethodID int = [DataLoadSimulation].[GetDeliveryMethodID] (N'Delivery Van');
    DECLARE @DeliveryAddressLine1 nvarchar(max);
    DECLARE @DeliveryAddressLine2 nvarchar(max);
    DECLARE @DeliveryPostalCode nvarchar(max);
    DECLARE @PostalAddressLine1 nvarchar(max);
    DECLARE @PostalAddressLine2 nvarchar(max);
    DECLARE @PostalPostalCode nvarchar(max);
    DECLARE @StreetSuffix nvarchar(max);
    DECLARE @CompanySuffix nvarchar(max);
    DECLARE @StorePrefix nvarchar(max);
    DECLARE @CreditLimit int;

    DECLARE @BuyingGroupID INT
    DECLARE @BuyingGroupName NVARCHAR(50)

    DECLARE @BGWebDomain             AS NVARCHAR(256)
    DECLARE @BGEmailDomain           AS NVARCHAR(256)
    DECLARE @PhoneNumber             AS NVARCHAR(20)
    DECLARE @FaxNumber               AS NVARCHAR(20)
    DECLARE @EmailTo                 AS NVARCHAR(75)
    DECLARE @EmailAddress            AS NVARCHAR(256)
    DECLARE @p
```