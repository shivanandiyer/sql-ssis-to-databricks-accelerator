# Review Required: DW:Integration.MigrateStagedMovementData

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Integration/Stored Procedures/MigrateStagedMovementData.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- Orchestration-heavy procedure split per conversion rule 4: SQL transformation logic and workflow orchestration logic are emitted as separate files.

## Source DDL (for reference)

```sql
CREATE PROCEDURE Integration.MigrateStagedMovementData
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    BEGIN TRAN;

    DECLARE @LineageKey int = (SELECT TOP(1) [Lineage Key]
                               FROM Integration.Lineage
                               WHERE [Table Name] = N'Movement'
                               AND [Data Load Completed] IS NULL
                               ORDER BY [Lineage Key] DESC);

    -- Find the dimension keys required

    UPDATE m
        SET m.[Stock Item Key] = COALESCE((SELECT TOP(1) si.[Stock Item Key]
                                           FROM Dimension.[Stock Item] AS si
                                           WHERE si.[WWI Stock Item ID] = m.[WWI Stock Item ID]
                                           AND m.[Last Modifed When] > si.[Valid From]
                                           AND m.[Last Modifed When] <= si.[Valid To]
									       ORDER BY si.[Valid From]), 0),
            m.[Customer Key] = COALESCE((SELECT TOP(1) c.[Customer Key]
                                         FROM Dimension.Customer AS c
                                         WHERE c.[WWI Customer ID] = m.[WWI Customer ID]
                                         AND m.[Last Modifed When] > c.[Valid From]
                                         AND m.[Last Modifed When] <= c.[Valid To]
									     ORDER BY c.[Valid From]), 0),
            m.[Supplier Key] = COALESCE((SELECT TOP(1) s.[Supplier Key]
                                         FROM Dimension.Supplier AS s
                                         WHERE s.[WWI Supplier ID] = m.[WWI Supplier ID]
                                         AND m.[Last Modifed When] > s.[Valid From]
                                         AND m.[Last Modifed When] <= s.[Valid To]
									     ORDER BY s.[Valid From]), 0),
            m.[Transaction Type Key] = COALESCE((SELECT TOP(1) tt.[Transaction Type Key]
                                                 FROM Dimension.[Transaction Type] AS tt
                                                 WHERE tt.[WWI Transaction Type ID] = m.[WWI Transaction Type ID]
                                                 AND m.[Last Modifed When] > tt.[Valid From]
                                                 AND m.[Last Modifed When] <= tt.[Valid To]
									             ORDER BY tt.[Valid From]), 0)
    FROM Integration.Movement_Staging AS m;

    -- Merge the data into the fact table

    MERGE Fact.Movement AS m
    USING Integration.Movement_Staging AS ms
    ON m.[WWI Stock Item Transaction ID] = ms.[WWI Stock Item Transaction ID]
    WHEN MATCHED THEN
        UPDATE SET m.[Date Key] = ms.[Date Key],
                   m.[Stock Item Key] = ms.[Stock Item Key],
                   m.[Customer Key] = ms.[Customer Key],
                   m.[Supplier Key] = ms.[Supplier Key],
                   m.[Transaction Type Key] = ms.[Transaction Type Key],
                   m.[WWI Invoice ID] = ms.[WWI Inv
```