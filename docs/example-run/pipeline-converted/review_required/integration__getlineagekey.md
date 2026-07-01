# Review Required: DW:Integration.GetLineageKey

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/GetLineageKey.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Orchestration-heavy procedure split per conversion rule 4: SQL transformation logic and workflow orchestration logic are emitted as separate files.

## Source DDL (for reference)

```sql
CREATE PROCEDURE Integration.GetLineageKey
@TableName sysname,
@NewCutoffTime datetime2(7)
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @DataLoadStartedWhen datetime2(7) = SYSDATETIME();

    INSERT Integration.Lineage
        ([Data Load Started], [Table Name], [Data Load Completed],
         [Was Successful], [Source System Cutoff Time])
    OUTPUT
        inserted.[Lineage Key] as LineageKey
    VALUES
        (@DataLoadStartedWhen, @TableName, NULL,
         0, @NewCutoffTime);

    RETURN 0;
END;
```