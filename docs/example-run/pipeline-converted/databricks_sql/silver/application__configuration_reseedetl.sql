-- Source: DW:Application.Configuration_ReseedETL  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Application/Stored Procedures/Configuration_ReseedETL.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

UPDATE Integration.[ETL Cutoff]
		SET [Cutoff Time] = @StartingETLCutoffTime;

DELETE Dimension.City;

DELETE Dimension.Customer;

DELETE Dimension.Employee;

DELETE Dimension.[Payment Method];

DELETE Dimension.[Stock Item];

DELETE Dimension.Supplier;

DELETE Dimension.[Transaction Type];

INSERT Dimension.City
        ([City Key], [WWI City ID], City, [State Province], Country, Continent, [Sales Territory], Region, Subregion,
         `Location`, [Latest Recorded Population], [Valid From], [Valid To], [Lineage Key])
    VALUES
        (0, 0, N'Unknown', N'N/A', N'N/A', N'N/A', N'N/A', N'N/A', N'N/A',
         NULL, 0, @StartOfTime, @EndOfTime, 0);

INSERT Dimension.Customer
        ([Customer Key], [WWI Customer ID], `Customer`, [Bill To Customer], Category, [Buying Group],
         [Primary Contact], [Postal Code], [Valid From], [Valid To], [Lineage Key])
    VALUES
        (0, 0, N'Unknown', N'N/A', N'N/A', N'N/A',
         N'N/A', N'N/A', @StartOfTime, @EndOfTime, 0);

INSERT Dimension.Employee
        ([Employee Key], [WWI Employee ID], Employee, [Preferred Name],
         [Is Salesperson], Photo, [Valid From], [Valid To], [Lineage Key])
    VALUES
        (0, 0, N'Unknown', N'N/A',
         0, NULL, @StartOfTime, @EndOfTime, 0);

INSERT Dimension.[Payment Method]
        ([Payment Method Key], [WWI Payment Method ID], [Payment Method], [Valid From], [Valid To], [Lineage Key])
    VALUES
        (0, 0, N'Unknown', @StartOfTime, @EndOfTime, 0);

INSERT Dimension.[Stock Item]
        ([Stock Item Key], [WWI Stock Item ID], [Stock Item], Color, [Selling Package], [Buying Package],
         Brand, Size, [Lead Time Days], [Quantity Per Outer], [Is Chiller Stock],
         Barcode, [Tax Rate], [Unit Price], [Recommended Retail Price], [Typical Weight Per Unit],
         Photo, [Valid From], [Valid To], [Lineage Key])
    VALUES
        (0, 0, N'Unknown', N'N/A', N'N/A', N'N/A',
         N'N/A', N'N/A', 0, 0, 0,
         N'N/A', 0, 0, 0, 0,
         NULL, @StartOfTime, @EndOfTime, 0);

INSERT Dimension.`Supplier`
        ([Supplier Key], [WWI Supplier ID], Supplier, Category, [Primary Contact], [Supplier Reference],
         [Payment Days], [Postal Code], [Valid From], [Valid To], [Lineage Key])
    VALUES
        (0, 0, N'Unknown', N'N/A', N'N/A', N'N/A',
         0, N'N/A', @StartOfTime, @EndOfTime, 0);

INSERT Dimension.[Transaction Type]
        ([Transaction Type Key], [WWI Transaction Type ID], [Transaction Type], [Valid From], [Valid To], [Lineage Key])
    VALUES
        (0, 0, N'Unknown', @StartOfTime, @EndOfTime, 0);