# Review Required: OLTP:Application.Configuration_DisableInMemory

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Stored Procedures/Configuration_DisableInMemory.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. years), a Python for-loop generating one MERGE per iteration.
- TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure handling.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [Application].[Configuration_DisableInMemory]
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

		DECLARE @SQL nvarchar(max) = N'';

		BEGIN TRY

/*-------------------------------------------------------------------------------------*/
/* Drop the procedures that are used by the table types                                */
/*-------------------------------------------------------------------------------------*/
      SET @SQL = N'DROP PROCEDURE IF EXISTS Website.InvoiceCustomerOrders;';
      EXECUTE (@SQL);

      SET @SQL = N'DROP PROCEDURE IF EXISTS Website.InsertCustomerOrders;';
      EXECUTE (@SQL);
			
      SET @SQL = N'DROP PROCEDURE IF EXISTS Website.RecordColdRoomTemperatures;';
			EXECUTE (@SQL);

      -- Drop the table types
      SET @SQL = N'DROP TYPE IF EXISTS Website.OrderIDList;';
      EXECUTE (@SQL);

      SET @SQL = N'DROP TYPE IF EXISTS Website.OrderLineList;';
      EXECUTE (@SQL);

      SET @SQL = N'DROP TYPE IF EXISTS Website.OrderList;';
      EXECUTE (@SQL);

      SET @SQL = N'DROP TYPE IF EXISTS Website.SensorDataList;';
      EXECUTE (@SQL);


/*-------------------------------------------------------------------------------------*/
/* Cold Room Temperatures - Recreate as non temporal and not memory optimized          */
/*-------------------------------------------------------------------------------------*/
      IF NOT EXISTS (SELECT 1 FROM sys.tables WHERE name = N'ColdRoomTemperatures' AND is_memory_optimized = 0)
      BEGIN

            SET @SQL = N'
ALTER TABLE Warehouse.ColdRoomTemperatures SET (SYSTEM_VERSIONING = OFF);
ALTER TABLE Warehouse.ColdRoomTemperatures DROP PERIOD FOR SYSTEM_TIME;';
            EXECUTE (@SQL);

            SET @SQL = N'
CREATE TABLE Warehouse.ColdRoomTemperatures_Staging
(
    ColdRoomTemperatureID bigint IDENTITY(1,1) NOT NULL,
    ColdRoomSensorNumber int NOT NULL,
    RecordedWhen datetime2(7) NOT NULL,
    Temperature decimal(10, 2) NOT NULL,
    ValidFrom datetime2(7) NOT NULL,
    ValidTo datetime2(7) NOT NULL,
);';
            EXECUTE (@SQL);

            SET @SQL = N'
SET IDENTITY_INSERT Warehouse.ColdRoomTemperatures_Staging ON;

INSERT Warehouse.ColdRoomTemperatures_Staging (ColdRoomTemperatureID, ColdRoomSensorNumber, RecordedWhen, Temperature,
                                       ValidFrom, ValidTo)
SELECT ColdRoomTemperatureID, ColdRoomSensorNumber, RecordedWhen, Temperature, ValidFrom, ValidTo
FROM Warehouse.ColdRoomTemperatures;

SET IDENTITY_INSERT Warehouse.ColdRoomTemperatures_Staging OFF;';
        EXECUTE (@SQL);

        SET @SQL = N'DROP TABLE Warehouse.ColdRoomTemperatures;';
        EXECUTE (@SQL);

        SET @SQL = N'
EXEC dbo.sp_rename @objname = N''Warehouse.ColdRoomTemperatures_Staging'',
                   @newname = N''ColdRoomTemperatures'',
                   @objtype = N''OBJECT'';';
        EXECUTE (@SQL);

        SET @SQL = '
CREATE NONCLUSTERED INDEX [IX_Warehouse_ColdRoomTemperatures_ColdRoomSensorNumber]
  ON Wareho
```