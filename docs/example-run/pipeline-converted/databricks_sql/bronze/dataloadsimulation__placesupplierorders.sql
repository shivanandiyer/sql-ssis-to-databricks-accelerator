-- Source: OLTP:DataLoadSimulation.PlaceSupplierOrders  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/PlaceSupplierOrders.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

INSERT @OrderLines (StockItemID, `Description`, SupplierID, QuantityOfOuters, LeadTimeDays, OuterPackageID, LastOuterCostPrice)
    SELECT sito.StockItemID,
           sito.`Description`,
           sito.SupplierID,
           CEILING((sito.TargetStockLevel - sito.EffectiveStockLevel) / sito.QuantityPerOuter) AS OutersRequired,
           sito.LeadTimeDays,
           sito.OuterPackageID,
           ROUND(sito.LastCostPrice * sito.QuantityPerOuter, 2) AS LastOuterCostPrice
    FROM StockItemsToOrder AS sito;

INSERT @Orders (SupplierID, PurchaseOrderID, DeliveryMethodID, ContactPersonID, SupplierReference)
    SELECT s.SupplierID
         , NEXT VALUE FOR Sequences.PurchaseOrderID
         , s.DeliveryMethodID
         , @SupplierPersonID
         , s.SupplierReference
    FROM Purchasing.Suppliers AS s
    WHERE s.SupplierID IN (SELECT SupplierID FROM @OrderLines);

INSERT Purchasing.PurchaseOrders
        (PurchaseOrderID, SupplierID, OrderDate, DeliveryMethodID, ContactPersonID,
         ExpectedDeliveryDate, SupplierReference, IsOrderFinalized, Comments,
         InternalComments, LastEditedBy, LastEditedWhen)
    SELECT o.PurchaseOrderID, o.SupplierID, CAST(@StartingWhen AS date), o.DeliveryMethodID, o.ContactPersonID,
           DATEADD(day, (SELECT MAX(LeadTimeDays) FROM @OrderLines), CAST(@StartingWhen AS date)),
           o.SupplierReference, 0, NULL,
           NULL, 1, @StartingWhen
    FROM @Orders AS o;

INSERT Purchasing.PurchaseOrderLines
        (PurchaseOrderID, StockItemID, OrderedOuters, `Description`,
         ReceivedOuters, PackageTypeID, ExpectedUnitPricePerOuter, LastReceiptDate,
         IsOrderLineFinalized, LastEditedBy, LastEditedWhen)
    SELECT o.PurchaseOrderID, ol.StockItemID, ol.QuantityOfOuters, ol.`Description`,
           0, ol.OuterPackageID, ol.LastOuterCostPrice, NULL,
           0, @ContactPersonID, @StartingWhen
    FROM @OrderLines AS ol
    INNER JOIN @Orders AS o
    ON ol.SupplierID = o.SupplierID;