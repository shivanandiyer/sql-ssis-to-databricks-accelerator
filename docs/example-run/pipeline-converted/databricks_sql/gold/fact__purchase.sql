-- Source: DW:Fact.Purchase  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Fact/Tables/Purchase.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.gold.purchase (
    Purchase STRING NOT NULL COMMENT 'source type: Key]',
    Date STRING NOT NULL COMMENT 'source type: Key]',
    Supplier STRING NOT NULL COMMENT 'source type: Key]',
    Stock STRING NOT NULL COMMENT 'source type: Item',
    WWI STRING COMMENT 'source type: Purchase',
    Ordered STRING NOT NULL COMMENT 'source type: Outers]',
    Ordered STRING NOT NULL COMMENT 'source type: Quantity]',
    Received STRING NOT NULL COMMENT 'source type: Outers]',
    Package STRING NOT NULL,
    Is STRING NOT NULL COMMENT 'source type: Order',
    Lineage STRING NOT NULL COMMENT 'source type: Key]'
)
USING DELTA
-- TODO: confirm partition column from source PARTITION SCHEME before enabling:
-- PARTITIONED BY (<date_or_period_column>)
COMMENT 'Converted from DW:Fact.Purchase'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Purchase` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Purchase` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Purchase -> STRING): Unrecognised SQL Server type 'Purchase' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Ordered` (Outers] -> STRING): Unrecognised SQL Server type 'Outers]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Ordered` (Quantity] -> STRING): Unrecognised SQL Server type 'Quantity]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Received` (Outers] -> STRING): Unrecognised SQL Server type 'Outers]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Is` (Order -> STRING): Unrecognised SQL Server type 'Order' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Purchase_Date_Key_Dimension_Date] FOREIGN KEY ([Date Key]) REFERENCES [Dimension].[Date]
-- ([Date])
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Purchase_Stock_Item_Key_Dimension_Stock Item] FOREIGN KEY ([Stock Item Key]) REFERENCES
-- [Dimension].
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Purchase_Supplier_Key_Dimension_Supplier] FOREIGN KEY ([Supplier Key]) REFERENCES
-- [Dimension].[Suppl