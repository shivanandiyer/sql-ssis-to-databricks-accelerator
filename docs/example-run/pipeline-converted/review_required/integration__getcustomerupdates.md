# Review Required: OLTP:Integration.GetCustomerUpdates

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Integration/Stored Procedures/GetCustomerUpdates.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- CURSOR — row-by-row processing; rewrite as a set-based DataFrame transformation (groupBy/window functions) or, if truly row-oriented, a Python loop over a collected (small) result set.
- WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. years), a Python for-loop generating one MERGE per iteration.
- Temp table — replace with a PySpark DataFrame (if used only within the procedure body) or a Delta table in a scratch/staging schema (if state must persist across steps).
- Orchestration-heavy procedure split per conversion rule 4: SQL transformation logic and workflow orchestration logic are emitted as separate files.

## Source DDL (for reference)

```sql
CREATE PROCEDURE Integration.GetCustomerUpdates
@LastCutoff datetime2(7),
@NewCutoff datetime2(7)
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    DECLARE @EndOfTime datetime2(7) = '99991231 23:59:59.9999999';
    DECLARE @InitialLoadDate date = '20200101';

    CREATE TABLE #CustomerChanges
    (
        [WWI Customer ID] int,
        Customer nvarchar(100),
        [Bill To Customer] nvarchar(100),
        Category nvarchar(50),
        [Buying Group] nvarchar(50),
        [Primary Contact] nvarchar(50),
        [Postal Code] nvarchar(10),
        [Valid From] datetime2(7),
        [Valid To] datetime2(7) NULL
    );

    DECLARE @BuyingGroupID int;
    DECLARE @CustomerCategoryID int;
    DECLARE @CustomerID int;
    DECLARE @ValidFrom datetime2(7);

    -- first need to find any buying group changes that have occurred since initial load

    DECLARE BuyingGroupChangeList CURSOR FAST_FORWARD READ_ONLY
    FOR
    SELECT bg.BuyingGroupID,
           bg.ValidFrom
    FROM Sales.BuyingGroups_Archive AS bg
    WHERE bg.ValidFrom > @LastCutoff
    AND bg.ValidFrom <= @NewCutoff
    AND bg.ValidFrom <> @InitialLoadDate
    UNION ALL
    SELECT bg.BuyingGroupID,
           bg.ValidFrom
    FROM Sales.BuyingGroups AS bg
    WHERE bg.ValidFrom > @LastCutoff
    AND bg.ValidFrom <= @NewCutoff
    AND bg.ValidFrom <> @InitialLoadDate
    ORDER BY ValidFrom;

    OPEN BuyingGroupChangeList;
    FETCH NEXT FROM BuyingGroupChangeList INTO @BuyingGroupID, @ValidFrom;

    WHILE @@FETCH_STATUS = 0
    BEGIN
        INSERT #CustomerChanges
            ([WWI Customer ID], Customer, [Bill To Customer], Category,
             [Buying Group], [Primary Contact], [Postal Code],
             [Valid From], [Valid To])
        SELECT c.CustomerID, c.CustomerName, bt.CustomerName, cc.CustomerCategoryName,
               bg.BuyingGroupName, p.FullName, c.DeliveryPostalCode,
               c.ValidFrom, c.ValidTo
        FROM Sales.Customers FOR SYSTEM_TIME AS OF @ValidFrom AS c
        INNER JOIN Sales.CustomerCategories FOR SYSTEM_TIME AS OF @ValidFrom AS cc
        ON c.CustomerCategoryID = cc.CustomerCategoryID
        INNER JOIN Sales.Customers FOR SYSTEM_TIME AS OF @ValidFrom AS bt
        ON c.BillToCustomerID = bt.CustomerID
        INNER JOIN [Application].People FOR SYSTEM_TIME AS OF @ValidFrom AS p
        ON c.PrimaryContactPersonID = p.PersonID
        LEFT JOIN Sales.BuyingGroups FOR SYSTEM_TIME AS OF @ValidFrom AS bg
        ON c.BuyingGroupID = bg.BuyingGroupID
        WHERE c.BuyingGroupID = @BuyingGroupID;

        FETCH NEXT FROM BuyingGroupChangeList INTO @BuyingGroupID, @ValidFrom;
    END;

    CLOSE BuyingGroupChangeList;
    DEALLOCATE BuyingGroupChangeList;

    -- next need to find any customer category changes that have occurred since initial load

    DECLARE CustomerCategoryChangeList CURSOR FAST_FORWARD READ_ONLY
    FOR
    SELECT cc.CustomerCategoryID,
           cc.ValidFrom
    FROM Sales.CustomerCategories_Ar
```