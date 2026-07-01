# Review Required: OLTP:DataLoadSimulation.ReceivePurchaseOrders

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/ReceivePurchaseOrders.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- CURSOR — row-by-row processing; rewrite as a set-based DataFrame transformation (groupBy/window functions) or, if truly row-oriented, a Python loop over a collected (small) result set.
- WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. years), a Python for-loop generating one MERGE per iteration.

## Source DDL (for reference)

```sql
CREATE PROCEDURE DataLoadSimulation.ReceivePurchaseOrders
@CurrentDateTime datetime2(7),
@StartingWhen datetime,
@EndOfTime datetime2(7),
@IsSilentMode bit
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    -- Pushed Notifications to calling proc
    --IF @IsSilentMode = 0
    --BEGIN
    --    PRINT N'Receiving stock from purchase orders for ' + LEFT(CAST(@CurrentDateTime AS NVARCHAR), 10);
    --END;

    DECLARE @StaffMemberPersonID int = (SELECT TOP(1) PersonID
                                        FROM [Application].People
                                        WHERE IsEmployee <> 0
                                        ORDER BY NEWID());
    DECLARE @PurchaseOrderID int;
    DECLARE @SupplierID int;
    DECLARE @TotalExcludingTax decimal(18,2);
    DECLARE @TotalIncludingTax decimal(18,2);

    DECLARE PurchaseOrderList CURSOR FAST_FORWARD READ_ONLY
    FOR
    SELECT PurchaseOrderID, SupplierID
    FROM Purchasing.PurchaseOrders AS po
    WHERE po.IsOrderFinalized = 0
    AND po.ExpectedDeliveryDate >= @StartingWhen;

    OPEN PurchaseOrderList;
    FETCH NEXT FROM PurchaseOrderList INTO @PurchaseOrderID, @SupplierID;

    WHILE @@FETCH_STATUS = 0
    BEGIN

        BEGIN TRAN;

        UPDATE Purchasing.PurchaseOrderLines
        SET ReceivedOuters = OrderedOuters,
            IsOrderLineFinalized = 1,
            LastReceiptDate = CAST(@StartingWhen as date),
            LastEditedBy = @StaffMemberPersonID,
            LastEditedWhen = @StartingWhen
        WHERE PurchaseOrderID = @PurchaseOrderID;

        UPDATE sih
        SET sih.QuantityOnHand += pol.ReceivedOuters * si.QuantityPerOuter,
            sih.LastEditedBy = @StaffMemberPersonID,
            sih.LastEditedWhen = @StartingWhen
        FROM Warehouse.StockItemHoldings AS sih
        INNER JOIN Purchasing.PurchaseOrderLines AS pol
        ON sih.StockItemID = pol.StockItemID
        INNER JOIN Warehouse.StockItems AS si
        ON sih.StockItemID = si.StockItemID;

        INSERT Warehouse.StockItemTransactions
            (StockItemID, TransactionTypeID, CustomerID, InvoiceID, SupplierID, PurchaseOrderID,
             TransactionOccurredWhen, Quantity, LastEditedBy, LastEditedWhen)
        SELECT pol.StockItemID, (SELECT TransactionTypeID FROM [Application].TransactionTypes WHERE TransactionTypeName = N'Stock Receipt'),
               NULL, NULL, @SupplierID, pol.PurchaseOrderID,
               @StartingWhen, pol.ReceivedOuters * si.QuantityPerOuter, @StaffMemberPersonID, @StartingWhen
        FROM Purchasing.PurchaseOrderLines AS pol
        INNER JOIN Warehouse.StockItems AS si
        ON pol.StockItemID = si.StockItemID
        WHERE pol.PurchaseOrderID = @PurchaseOrderID;

        UPDATE Purchasing.PurchaseOrders
        SET IsOrderFinalized = 1,
            LastEditedBy = @StaffMemberPersonID,
            LastEditedWhen = @StartingWhen
        WHERE PurchaseOrderID = @PurchaseOrderID;

        SELECT @TotalExcludingTax = SUM(ROUND(pol.OrderedOuters * pol.Expe
```