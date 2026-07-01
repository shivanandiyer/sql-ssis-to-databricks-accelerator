# Review Required: OLTP:Website.CalculateCustomerPrice

- **Object type:** SCALAR_FUNCTION
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Website/Functions/CalculateCustomerPrice.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review

- Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UDF equivalent — converted to a PySpark UDF stub requiring manual implementation of the equivalent access-control or looping logic using Unity Catalog row/column-level security or PySpark control flow.
- Original function is called inline from T-SQL SELECT statements — registered via spark.udf.register('CalculateCustomerPrice', ...) so it remains SQL-callable after conversion, rather than only usable from PySpark DataFrame code.

## Source DDL (for reference)

```sql
CREATE FUNCTION Website.CalculateCustomerPrice
(
    @CustomerID int,
    @StockItemID int,
    @PricingDate date
)
RETURNS decimal(18,2)
WITH EXECUTE AS OWNER
AS
BEGIN
    DECLARE @CalculatedPrice decimal(18,2);
    DECLARE @UnitPrice decimal(18,2);
    DECLARE @LowestUnitPrice decimal(18,2);
    DECLARE @HighestDiscountAmount decimal(18,2);
    DECLARE @HighestDiscountPercentage decimal(18,3);
    DECLARE @BuyingGroupID int;
    DECLARE @CustomerCategoryID int;
    DECLARE @DiscountedUnitPrice decimal(18,2);

    SELECT @BuyingGroupID = BuyingGroupID,
           @CustomerCategoryID = CustomerCategoryID
    FROM Sales.Customers
    WHERE CustomerID = @CustomerID;

    SELECT @UnitPrice = si.UnitPrice
    FROM Warehouse.StockItems AS si
    WHERE si.StockItemID = @StockItemID;

    SET @CalculatedPrice = @UnitPrice;

    SET @LowestUnitPrice = (SELECT MIN(sd.UnitPrice)
                            FROM Sales.SpecialDeals AS sd
                            WHERE ((sd.StockItemID = @StockItemID) OR (sd.StockItemID IS NULL))
                            AND ((sd.CustomerID = @CustomerID) OR (sd.CustomerID IS NULL))
                            AND ((sd.BuyingGroupID = @BuyingGroupID) OR (sd.BuyingGroupID IS NULL))
                            AND ((sd.CustomerCategoryID = @CustomerCategoryID) OR (sd.CustomerCategoryID IS NULL))
                            AND ((sd.StockGroupID IS NULL) OR EXISTS (SELECT 1 FROM Warehouse.StockItemStockGroups AS sisg
                                                                               WHERE sisg.StockItemID = @StockItemID
                                                                               AND sisg.StockGroupID = sd.StockGroupID))
                            AND sd.UnitPrice IS NOT NULL
                            AND @PricingDate BETWEEN sd.StartDate AND sd.EndDate);

    IF @LowestUnitPrice IS NOT NULL AND @LowestUnitPrice < @UnitPrice
    BEGIN
        SET @CalculatedPrice = @LowestUnitPrice;
    END;

    SET @HighestDiscountAmount = (SELECT MAX(sd.DiscountAmount)
                                  FROM Sales.SpecialDeals AS sd
                                  WHERE ((sd.StockItemID = @StockItemID) OR (sd.StockItemID IS NULL))
                                  AND ((sd.CustomerID = @CustomerID) OR (sd.CustomerID IS NULL))
                                  AND ((sd.BuyingGroupID = @BuyingGroupID) OR (sd.BuyingGroupID IS NULL))
                                  AND ((sd.CustomerCategoryID = @CustomerCategoryID) OR (sd.CustomerCategoryID IS NULL))
                                  AND ((sd.StockGroupID IS NULL) OR EXISTS (SELECT 1 FROM Warehouse.StockItemStockGroups AS sisg
                                                                                     WHERE sisg.StockItemID = @StockItemID
                                                                                     AND sisg.StockGroupID = sd.StockGroupID))
                                  AND sd.DiscountAmount IS NOT NULL
                
```