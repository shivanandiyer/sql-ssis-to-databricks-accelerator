# Review Required: OLTP:Integration.GetTransactionTypeUpdates

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Integration/Stored Procedures/GetTransactionTypeUpdates.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- CURSOR — row-by-row processing; rewrite as a set-based DataFrame transformation (groupBy/window functions) or, if truly row-oriented, a Python loop over a collected (small) result set.
- WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. years), a Python for-loop generating one MERGE per iteration.
- Temp table — replace with a PySpark DataFrame (if used only within the procedure body) or a Delta table in a scratch/staging schema (if state must persist across steps).
- Orchestration-heavy procedure split per conversion rule 4: SQL transformation logic and workflow orchestration logic are emitted as separate files.

## Source DDL (for reference)

```sql
CREATE PROCEDURE Integration.GetTransactionTypeUpdates
@LastCutoff datetime2(7),
@NewCutoff datetime2(7)
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @EndOfTime datetime2(7) = '99991231 23:59:59.9999999';

    CREATE TABLE #TransactionTypeChanges
    (
        [WWI Transaction Type ID] int,
        [Transaction Type] nvarchar(50),
        [Valid From] datetime2(7),
        [Valid To] datetime2(7)
    );

    DECLARE @TransactionTypeID int;
    DECLARE @ValidFrom datetime2(7);

    -- need to find any Transaction Type changes that have occurred, including during the initial load

    DECLARE ChangeList CURSOR FAST_FORWARD READ_ONLY
    FOR
    SELECT tt.TransactionTypeID,
           tt.ValidFrom
    FROM [Application].TransactionTypes_Archive AS tt
    WHERE tt.ValidFrom > @LastCutoff
    AND tt.ValidFrom <= @NewCutoff
    UNION ALL
    SELECT tt.TransactionTypeID,
           tt.ValidFrom
    FROM [Application].TransactionTypes AS tt
    WHERE tt.ValidFrom > @LastCutoff
    AND tt.ValidFrom <= @NewCutoff
    ORDER BY ValidFrom;

    OPEN ChangeList;
    FETCH NEXT FROM ChangeList INTO @TransactionTypeID, @ValidFrom;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        INSERT #TransactionTypeChanges
            ([WWI Transaction Type ID], [Transaction Type], [Valid From], [Valid To])
        SELECT p.TransactionTypeID, p.TransactionTypeName, p.ValidFrom, p.ValidTo
        FROM [Application].TransactionTypes FOR SYSTEM_TIME AS OF @ValidFrom AS p
        WHERE p.TransactionTypeID = @TransactionTypeID;

        FETCH NEXT FROM ChangeList INTO @TransactionTypeID, @ValidFrom;
    END;

    CLOSE ChangeList;
    DEALLOCATE ChangeList;

    -- add an index to make lookups faster

    CREATE INDEX IX_TransactionTypeChanges ON #TransactionTypeChanges ([WWI Transaction Type ID], [Valid From]);

    -- work out the [Valid To] value by taking the [Valid From] of any row that's for the same entry but later
    -- otherwise take the end of time

    UPDATE cc
    SET [Valid To] = COALESCE((SELECT MIN([Valid From]) FROM #TransactionTypeChanges AS cc2
                                                        WHERE cc2.[WWI Transaction Type ID] = cc.[WWI Transaction Type ID]
                                                        AND cc2.[Valid From] > cc.[Valid From]), @EndOfTime)
    FROM #TransactionTypeChanges AS cc;

    SELECT [WWI Transaction Type ID], [Transaction Type], [Valid From], [Valid To]
    FROM #TransactionTypeChanges
    ORDER BY [Valid From];

    DROP TABLE #TransactionTypeChanges;

    RETURN 0;
END;
```