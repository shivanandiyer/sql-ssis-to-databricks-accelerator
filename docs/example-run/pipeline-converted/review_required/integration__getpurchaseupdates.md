# Review Required: OLTP:Integration.GetPurchaseUpdates

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Integration/Stored Procedures/GetPurchaseUpdates.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE Integration.GetPurchaseUpdates
@LastCutoff datetime2(7),
@NewCutoff datetime2(7)
WITH EXECUTE AS OWNER
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;


    SELECT CAST(po.OrderDate AS date) AS [Date Key],
           po.PurchaseOrderID AS [WWI Purchase Order ID],
           pol.OrderedOuters AS [Ordered Outers],
           pol.OrderedOuters * si.QuantityPerOuter AS [Ordered Quantity],
           pol.ReceivedOuters AS [Received Outers],
           pt.PackageTypeName AS Package,
           pol.IsOrderLineFinalized AS [Is Order Finalized],
           po.SupplierID AS [WWI Supplier ID],
           pol.StockItemID AS [WWI Stock Item ID],
           CASE WHEN pol.LastEditedWhen > po.LastEditedWhen THEN pol.LastEditedWhen ELSE po.LastEditedWhen END AS [Last Modified When]
    FROM Purchasing.PurchaseOrders AS po
    INNER JOIN Purchasing.PurchaseOrderLines AS pol
    ON po.PurchaseOrderID = pol.PurchaseOrderID
    INNER JOIN Warehouse.StockItems AS si
    ON pol.StockItemID = si.StockItemID
    INNER JOIN Warehouse.PackageTypes AS pt
    ON pol.PackageTypeID = pt.PackageTypeID
    WHERE CASE WHEN pol.LastEditedWhen > po.LastEditedWhen THEN pol.LastEditedWhen ELSE po.LastEditedWhen END > @LastCutoff
    AND CASE WHEN pol.LastEditedWhen > po.LastEditedWhen THEN pol.LastEditedWhen ELSE po.LastEditedWhen END <= @NewCutoff
    ORDER BY po.PurchaseOrderID;

    RETURN 0;
END;
```