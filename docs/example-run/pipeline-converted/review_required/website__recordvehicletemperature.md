# Review Required: OLTP:Website.RecordVehicleTemperature

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Website/Stored Procedures/RecordVehicleTemperature.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure handling.
- OPENJSON — no Spark SQL equivalent; rewrite as PySpark from_json()/explode() against an explicit schema derived from the source's WITH clause column list. MANUAL REVIEW REQUIRED — do not treat as ordinary set-based SQL.

## Source DDL (for reference)

```sql
CREATE PROCEDURE Website.RecordVehicleTemperature
@FullSensorDataArray nvarchar(1000)
WITH EXECUTE AS OWNER
AS
BEGIN
    SET XACT_ABORT ON;

    DECLARE @CrLf nchar(2) = nchar(13) + nchar(10);
    DECLARE @HelpMessage nvarchar(max) = N'JSON sensor data is invalid. An example of what is required is as follows:' + @CrLf + @CrLf
              + N'{"Recordings":' + @CrLf
              + N'    [' + @CrLf
              + N'        {"type":"Feature", "geometry": {"type":"Point", "coordinates":[-89.7600464,50.4742420] }, "properties":{"rego":"WWI-321-A","sensor":1,"when":"2016-01-01T07:00:00","temp":3.96}},' + @CrLf
              + N'        {"type":"Feature", "geometry": {"type":"Point", "coordinates":[-89.7600464,50.4742420] }, "properties":{"rego":"WWI-321-A","sensor":2,"when":"2016-01-01T07:00:00","temp":3.98}}' + @CrLf
              + N'    ]' + @CrLf
              + N'}';

    IF ISJSON(@FullSensorDataArray) = 0
    BEGIN
        PRINT @HelpMessage;
        THROW 51000, N'FullSensorDataArray must be valid JSON data', 1;
        RETURN 1;
    END;

    BEGIN TRY

        BEGIN TRAN;

        INSERT Warehouse.VehicleTemperatures
            (VehicleRegistration, ChillerSensorNumber, RecordedWhen, Temperature,
			 FullSensorData, IsCompressed, CompressedSensorData)
		SELECT VehicleRegistration, ChillerSensorNumber, RecordedWhen, Temperature,
		       FullSensorData, 0, NULL
		FROM OPENJSON(@FullSensorDataArray, N'$.Recordings')
        WITH ( VehicleRegistration nvarchar(40) N'$.properties.rego',
               ChillerSensorNumber int N'$.properties.sensor',
        	   RecordedWhen datetime2(7) N'$.properties.when',
        	   Temperature decimal(18,2) N'$.properties.temp',
        	   FullSensorData nvarchar(max) N'$' AS JSON);

        IF @@ROWCOUNT = 0
        BEGIN
            PRINT N'Warning: No valid sensor data found';
            PRINT @HelpMessage;
        END;

        COMMIT;

    END TRY
    BEGIN CATCH
        PRINT @HelpMessage;

        THROW 51000, N'Valid JSON was supplied but does not match the temperature recordings array structure', 2;

        IF XACT_STATE() <> 0 ROLLBACK TRAN;

        RETURN 1;
    END CATCH;
END;
```