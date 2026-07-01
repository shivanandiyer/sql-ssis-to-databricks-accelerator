# Review Required: OLTP:DataLoadSimulation.RecordInvoiceDeliveries

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/RecordInvoiceDeliveries.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- CURSOR — row-by-row processing; rewrite as a set-based DataFrame transformation (groupBy/window functions) or, if truly row-oriented, a Python loop over a collected (small) result set.
- WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. years), a Python for-loop generating one MERGE per iteration.

## Source DDL (for reference)

```sql
CREATE PROCEDURE DataLoadSimulation.RecordInvoiceDeliveries
@CurrentDateTime datetime2(7),
@StartingWhen datetime,
@EndOfTime datetime2(7),
@IsSilentMode bit
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    -- Pushed Notifications to calling proc
    --IF @IsSilentMode = 0
    --BEGIN
    --    PRINT N'Recording invoice deliveries for ' + LEFT(CAST(@CurrentDateTime AS NVARCHAR), 10);
    --END;

    --DECLARE @DeliveryDriverPersonID int = (SELECT TOP(1) PersonID
    --                                       FROM [Application].People
    --                                       WHERE IsEmployee <> 0
    --                                       ORDER BY NEWID());
    DECLARE @DeliveryDriverPersonID INT
    EXEC [DataLoadSimulation].[GetRandomEmployeePerson]
      @EmployeePersonID = @DeliveryDriverPersonID OUTPUT

    DECLARE @ReturnedDeliveryData nvarchar(max);
    DECLARE @InvoiceID int;
    DECLARE @CustomerName nvarchar(100);
    DECLARE @PrimaryContactFullName nvarchar(50);
    DECLARE @Latitude decimal(18,7);
    DECLARE @Longitude decimal(18,7);
    DECLARE @DeliveryAttemptWhen datetime2(7);
    DECLARE @Counter int = 0;
    DECLARE @DeliveryEvent nvarchar(max);
    DECLARE @IsDelivered bit;

    DECLARE InvoiceList CURSOR FAST_FORWARD READ_ONLY
    FOR
    SELECT i.InvoiceID, i.ReturnedDeliveryData, c.CustomerName
         , p.FullName, ct.[Location].Lat, ct.[Location].Long
      FROM Sales.Invoices AS i
     INNER JOIN Sales.Customers AS c
        ON i.CustomerID = c.CustomerID
     INNER JOIN [Application].Cities AS ct
        ON c.DeliveryCityID = ct.CityID
     INNER JOIN [Application].People AS p
        ON c.PrimaryContactPersonID = p.PersonID
     WHERE i.ConfirmedDeliveryTime IS NULL
       AND i.InvoiceDate < CAST(@StartingWhen AS date)
     ORDER BY i.InvoiceID;

    OPEN InvoiceList;
    FETCH NEXT FROM InvoiceList INTO @InvoiceID, @ReturnedDeliveryData, @CustomerName, @PrimaryContactFullName, @Latitude, @Longitude;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        SET @Counter += 1;
        SET @DeliveryAttemptWhen = DATEADD(minute, @Counter * 5, @StartingWhen);

        SET @DeliveryEvent = N'{ }';
        SET @DeliveryEvent = JSON_MODIFY(@DeliveryEvent, N'$.Event', N'DeliveryAttempt');
        SET @DeliveryEvent = JSON_MODIFY(@DeliveryEvent, N'$.EventTime', CONVERT(nvarchar(20), @DeliveryAttemptWhen, 126));
        SET @DeliveryEvent = JSON_MODIFY(@DeliveryEvent, N'$.ConNote', N'EAN-125-' + CAST(@InvoiceID + 1050 AS nvarchar(20)));
        SET @DeliveryEvent = JSON_MODIFY(@DeliveryEvent, N'$.DriverID', @DeliveryDriverPersonID);
        SET @DeliveryEvent = JSON_MODIFY(@DeliveryEvent, N'$.Latitude', @Latitude);
        SET @DeliveryEvent = JSON_MODIFY(@DeliveryEvent, N'$.Longitude', @Longitude);

        SET @IsDelivered = 0;

        IF RAND() < 0.1 -- 10 % chance of non-delivery on this attempt
        BEGIN
            SET @DeliveryEvent = JSON_MODIFY(@DeliveryEvent, N'$.Comment', N'Receiver not pr
```