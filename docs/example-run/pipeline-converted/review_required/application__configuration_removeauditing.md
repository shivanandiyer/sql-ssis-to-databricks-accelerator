# Review Required: OLTP:Application.Configuration_RemoveAuditing

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Stored Procedures/Configuration_RemoveAuditing.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure handling.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [Application].Configuration_RemoveAuditing
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @AreDatabaseAuditSpecificationsSupported bit = 0;
    DECLARE @SQL nvarchar(max);

    -- TODO !! - currently no separate test for audit
    -- but same editions with XTP support database audit specs
    IF SERVERPROPERTY(N'IsXTPSupported') <> 0 SET @AreDatabaseAuditSpecificationsSupported = 1;

    BEGIN TRY;

        IF @AreDatabaseAuditSpecificationsSupported <> 0
        BEGIN
            IF EXISTS (SELECT 1 FROM sys.database_audit_specifications WHERE name = N'WWI_DatabaseAuditSpecification')
            BEGIN
                SET @SQL = N'
DROP DATABASE AUDIT SPECIFICATION WWI_DatabaseAuditSpecification;';
                EXECUTE (@SQL);
            END;
        END;

        IF EXISTS (SELECT 1 FROM sys.server_audit_specifications WHERE name = N'WWI_ServerAuditSpecification')
        BEGIN
            SET @SQL = N'
USE master;

DROP SERVER AUDIT SPECIFICATION WWI_ServerAuditSpecification;';
            EXECUTE (@SQL);
        END;

        IF EXISTS (SELECT 1 FROM sys.server_audits WHERE name = N'WWI_Audit')
        BEGIN
            SET @SQL = N'
USE master;

DROP SERVER AUDIT [WWI_Audit];';
            EXECUTE (@SQL);

        END;

    END TRY
    BEGIN CATCH
        PRINT N'Unable to remove audit';
        THROW;
    END CATCH;
END;
```