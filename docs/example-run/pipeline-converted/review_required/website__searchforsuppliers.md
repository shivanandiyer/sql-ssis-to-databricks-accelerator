# Review Required: OLTP:Website.SearchForSuppliers

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Website/Stored Procedures/SearchForSuppliers.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review


## Source DDL (for reference)

```sql
CREATE PROCEDURE Website.SearchForSuppliers
@SearchText nvarchar(1000),
@MaximumRowsToReturn int
AS
BEGIN
    SELECT TOP(@MaximumRowsToReturn)
           s.SupplierID,
           s.SupplierName,
           c.CityName,
           s.PhoneNumber,
           s.FaxNumber ,
           p.FullName AS PrimaryContactFullName,
           p.PreferredName AS PrimaryContactPreferredName
    FROM Purchasing.Suppliers AS s
    INNER JOIN [Application].Cities AS c
    ON s.DeliveryCityID = c.CityID
    LEFT OUTER JOIN [Application].People AS p
    ON s.PrimaryContactPersonID = p.PersonID
    WHERE CONCAT(s.SupplierName, N' ', p.FullName, N' ', p.PreferredName) LIKE N'%' + @SearchText + N'%'
    ORDER BY s.SupplierName
    FOR JSON AUTO, ROOT(N'Suppliers');
END;
```