-- Source: OLTP:DataLoadSimulation.AddSpecialDeals  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/DataLoadSimulation/Stored Procedures/AddSpecialDeals.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

INSERT Sales.SpecialDeals
            (StockItemID, CustomerID, BuyingGroupID, CustomerCategoryID, StockGroupID,
             DealDescription, StartDate, EndDate, DiscountAmount, DiscountPercentage,
             UnitPrice, LastEditedBy, LastEditedWhen)
        VALUES
            (NULL, NULL, (SELECT BuyingGroupID FROM Sales.BuyingGroups WHERE BuyingGroupName = N'Wingtip Toys'),
             NULL, (SELECT StockGroupID FROM Warehouse.StockGroups WHERE StockGroupName = N'USB Novelties'),
             N'10% 1st qtr USB Wingtip', '20220101', '20220331', NULL, 10, NULL,
             2, @StartingWhen);

INSERT Sales.SpecialDeals
            (StockItemID, CustomerID, BuyingGroupID, CustomerCategoryID, StockGroupID,
             DealDescription, StartDate, EndDate, DiscountAmount, DiscountPercentage,
             UnitPrice, LastEditedBy, LastEditedWhen)
        VALUES
            (NULL, NULL, (SELECT BuyingGroupID FROM Sales.BuyingGroups WHERE BuyingGroupName = N'Tailspin Toys'),
             NULL, (SELECT StockGroupID FROM Warehouse.StockGroups WHERE StockGroupName = N'USB Novelties'),
             N'15% 2nd qtr USB Tailspin', '20220401', '20220630', NULL, 15, NULL,
             2, @StartingWhen);