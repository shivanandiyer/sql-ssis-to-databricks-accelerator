# Review Required: OLTP:Application.AddRoleMemberIfNonexistent

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Stored Procedures/AddRoleMemberIfNonexistent.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure handling.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [Application].AddRoleMemberIfNonexistent
@RoleName sysname,
@UserName sysname
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    IF NOT EXISTS (SELECT 1 FROM sys.database_role_members AS drm
                            INNER JOIN sys.database_principals AS dpr
                            ON drm.role_principal_id = dpr.principal_id
                            AND dpr.type = N'R'
                            INNER JOIN sys.database_principals AS dpu
                            ON drm.member_principal_id = dpu.principal_id
                            AND dpu.type = N'S'
                            WHERE dpr.name = @RoleName
                            AND dpu.name = @UserName)
    BEGIN
        BEGIN TRY

            DECLARE @SQL nvarchar(max) = N'ALTER ROLE ' + QUOTENAME(@RoleName)
                                       + N' ADD MEMBER ' + QUOTENAME(@UserName) + N';'
            EXECUTE (@SQL);

            PRINT N'User ' + @UserName + N' added to role ' + @RoleName;

        END TRY
        BEGIN CATCH
            PRINT N'Unable to add user ' + @UserName + N' to role ' + @RoleName;
            THROW;
        END CATCH;
    END;
END;
```