-- Source: DW:Fact.Sale  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Fact/Tables/Sale.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.gold.sale (
    Sale STRING NOT NULL COMMENT 'source type: Key]',
    City STRING NOT NULL COMMENT 'source type: Key]',
    Customer STRING NOT NULL COMMENT 'source type: Key]',
    Bill STRING NOT NULL COMMENT 'source type: To',
    Stock STRING NOT NULL COMMENT 'source type: Item',
    Invoice DATE NOT NULL,
    Delivery DATE,
    Salesperson STRING NOT NULL COMMENT 'source type: Key]',
    WWI STRING NOT NULL COMMENT 'source type: Invoice',
    Description STRING NOT NULL,
    Package STRING NOT NULL,
    Quantity INT NOT NULL,
    Unit STRING NOT NULL COMMENT 'source type: Price]',
    Tax STRING NOT NULL COMMENT 'source type: Rate]',
    Total STRING NOT NULL COMMENT 'source type: Excluding',
    Tax STRING NOT NULL COMMENT 'source type: Amount]',
    Profit DECIMAL(18,2) NOT NULL,
    Total STRING NOT NULL COMMENT 'source type: Including',
    Total STRING NOT NULL COMMENT 'source type: Dry',
    Total STRING NOT NULL COMMENT 'source type: Chiller',
    Lineage STRING NOT NULL COMMENT 'source type: Key]'
)
USING DELTA
-- TODO: confirm partition column from source PARTITION SCHEME before enabling:
-- PARTITIONED BY (<date_or_period_column>)
COMMENT 'Converted from DW:Fact.Sale'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Sale` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Sale` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS
-- IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `City` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Bill` (To -> STRING): Unrecognised SQL Server type 'To' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Salesperson` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Unit` (Price] -> STRING): Unrecognised SQL Server type 'Price]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Tax` (Rate] -> STRING): Unrecognised SQL Server type 'Rate]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Total` (Excluding -> STRING): Unrecognised SQL Server type 'Excluding' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Tax` (Amount] -> STRING): Unrecognised SQL Server type 'Amount]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Total` (Including -> STRING): Unrecognised SQL Server type 'Including' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Total` (Dry -> STRING): Unrecognised SQL Server type 'Dry' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Total` (Chiller -> STRING): Unrecognised SQL Server type 'Chiller' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Sale_Bill_To_Customer_Key_Dimension_Customer] FOREIGN KEY ([Bill To Customer Key])
-- REFERENCES [Dimen
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Sale_City_Key_Dimension_City] FOREIGN KEY ([City Key]) REFERENCES [Dimension].[City] ([City
-- Key])
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Sale_Customer_Key_Dimension_Customer] FOREIGN KEY ([Customer Key]) REFERENCES
-- [Dimension].[Customer]
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Sale_Delivery_Date_Key_Dimension_Date] FOREIGN KEY ([Delivery Date Key]) REFERENCES
-- [Dimension].[Dat
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Sale_Invoice_Date_Key_Dimension_Date] FOREIGN KEY ([Invoice Date Key]) REFERENCES
-- [Dimension].[Date]
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Sale_Salesperson_Key_Dimension_Employee] FOREIGN KEY ([Salesperson Key]) REFERENCES
-- [Dimension].[Emp
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Sale_Stock_Item_Key_Dimension_Stock Item] FOREIGN KEY ([Stock Item Key]) REFERENCES
-- [Dimension].[Sto