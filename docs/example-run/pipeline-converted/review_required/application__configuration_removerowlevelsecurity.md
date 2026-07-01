# Review Required: OLTP:Application.Configuration_RemoveRowLevelSecurity

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Stored Procedures/Configuration_RemoveRowLevelSecurity.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure handling.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [Application].Configuration_RemoveRowLevelSecurity
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @SQL nvarchar(max);

    BEGIN TRY;

        SET @SQL = N'DROP SECURITY POLICY IF EXISTS [Application].FilterCustomersBySalesTerritoryRole;';
        EXECUTE (@SQL);

        SET @SQL = N'DROP FUNCTION IF EXISTS [Application].DetermineCustomerAccess;';
        EXECUTE (@SQL);

        PRINT N'Successfully removed row level security';
    END TRY
    BEGIN CATCH
        PRINT N'Unable to remove row level security';
        THROW 51000, N'Unable to remove row level security', 1;
    END CATCH;
END;
```