# Review Required: OLTP:Website.SearchForPeople

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Website/Stored Procedures/SearchForPeople.sql
- **Classification:** REWRITE_REQUIRED

## Why this needs manual review


## Source DDL (for reference)

```sql
CREATE PROCEDURE Website.SearchForPeople
@SearchText nvarchar(1000),
@MaximumRowsToReturn int
AS
BEGIN
    SELECT TOP(@MaximumRowsToReturn)
           p.PersonID,
           p.FullName,
           p.PreferredName,
           CASE WHEN p.IsSalesperson <> 0 THEN N'Salesperson'
                WHEN p.IsEmployee <> 0 THEN N'Employee'
                WHEN c.CustomerID IS NOT NULL THEN N'Customer'
                WHEN sp.SupplierID IS NOT NULL THEN N'Supplier'
                WHEN sa.SupplierID IS NOT NULL THEN N'Supplier'
           END AS Relationship,
           COALESCE(c.CustomerName, sp.SupplierName, sa.SupplierName, N'WWI') AS Company
    FROM [Application].People AS p
    LEFT OUTER JOIN Sales.Customers AS c
    ON c.PrimaryContactPersonID = p.PersonID
    LEFT OUTER JOIN Purchasing.Suppliers AS sp
    ON sp.PrimaryContactPersonID = p.PersonID
    LEFT OUTER JOIN Purchasing.Suppliers AS sa
    ON sa.AlternateContactPersonID = p.PersonID
    WHERE p.SearchName LIKE N'%' + @SearchText + N'%'
    ORDER BY p.FullName
    FOR JSON AUTO, ROOT(N'People');
END;
```