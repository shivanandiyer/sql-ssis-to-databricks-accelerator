# Review Required: OLTP:DataLoadSimulation.DeactivateTemporalTablesBeforeDataLoad

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/DeactivateTemporalTablesBeforeDataLoad.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review


## Source DDL (for reference)

```sql
CREATE PROCEDURE DataLoadSimulation.DeactivateTemporalTablesBeforeDataLoad
AS BEGIN
    -- Disables the temporal nature of the temporal tables before a simulated data load
    SET NOCOUNT ON;

    IF EXISTS (SELECT 1 FROM sys.procedures WHERE name = N'Configuration_RemoveRowLevelSecurity')
    BEGIN
        EXEC [Application].Configuration_RemoveRowLevelSecurity;
    END;

    DECLARE @SQL nvarchar(max) = N'';
    DECLARE @CrLf nvarchar(2) = NCHAR(13) + NCHAR(10);
    DECLARE @Indent nvarchar(4) = N'    ';
    DECLARE @SchemaName sysname;
    DECLARE @TableName sysname;
    DECLARE @NormalColumnList nvarchar(max);
    DECLARE @NormalColumnListWithDPrefix nvarchar(max);
    DECLARE @PrimaryKeyColumn sysname;
    DECLARE @TemporalFromColumnName sysname = N'ValidFrom';
    DECLARE @TemporalToColumnName sysname = N'ValidTo';
    DECLARE @TemporalTableSuffix nvarchar(max) = N'Archive';
    DECLARE @LastEditedByColumnName sysname;

    ALTER TABLE [Application].[Cities] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Application].[Cities] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Application].[Countries] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Application].[Countries] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Application].[DeliveryMethods] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Application].[DeliveryMethods] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Application].[PaymentMethods] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Application].[PaymentMethods] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Application].[People] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Application].[People] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Application].[StateProvinces] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Application].[StateProvinces] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Application].[TransactionTypes] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Application].[TransactionTypes] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Purchasing].[SupplierCategories] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Purchasing].[SupplierCategories] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Purchasing].[Suppliers] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Purchasing].[Suppliers] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Sales].[BuyingGroups] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Sales].[BuyingGroups] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Sales].[CustomerCategories] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Sales].[CustomerCategories] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Sales].[Customers] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Sales].[Customers] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Warehouse].[ColdRoomTemperatures] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Warehouse].[ColdRoomTemperatures] DROP PERIOD FOR SYSTEM_TIME;

    ALTER TABLE [Warehouse].[Colors] SET (SYSTEM_VERSIONING = OFF);
    ALTER TABLE [Warehouse].[Colors] DROP PERIOD FOR 
```