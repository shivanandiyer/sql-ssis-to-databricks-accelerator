-- Source: DW:Fact.Movement  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Fact/Tables/Movement.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.gold.movement (
    Movement STRING NOT NULL COMMENT 'source type: Key]',
    Date STRING NOT NULL COMMENT 'source type: Key]',
    Stock STRING NOT NULL COMMENT 'source type: Item',
    Customer STRING COMMENT 'source type: Key]',
    Supplier STRING COMMENT 'source type: Key]',
    Transaction STRING NOT NULL COMMENT 'source type: Type',
    WWI STRING NOT NULL COMMENT 'source type: Stock',
    WWI STRING COMMENT 'source type: Invoice',
    WWI STRING COMMENT 'source type: Purchase',
    Quantity INT NOT NULL,
    Lineage STRING NOT NULL COMMENT 'source type: Key]'
)
USING DELTA
-- TODO: confirm partition column from source PARTITION SCHEME before enabling:
-- PARTITIONED BY (<date_or_period_column>)
COMMENT 'Converted from DW:Fact.Movement'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Movement` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Movement` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Stock` (Item -> STRING): Unrecognised SQL Server type 'Item' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Transaction` (Type -> STRING): Unrecognised SQL Server type 'Type' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Stock -> STRING): Unrecognised SQL Server type 'Stock' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `WWI` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Purchase -> STRING): Unrecognised SQL Server type 'Purchase' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Movement_Customer_Key_Dimension_Customer] FOREIGN KEY ([Customer Key]) REFERENCES
-- [Dimension].[Custo
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Movement_Date_Key_Dimension_Date] FOREIGN KEY ([Date Key]) REFERENCES [Dimension].[Date]
-- ([Date])
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Movement_Stock_Item_Key_Dimension_Stock Item] FOREIGN KEY ([Stock Item Key]) REFERENCES
-- [Dimension].
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Movement_Supplier_Key_Dimension_Supplier] FOREIGN KEY ([Supplier Key]) REFERENCES
-- [Dimension].[Suppl
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Movement_Transaction_Type_Key_Dimension_Transaction Type] FOREIGN KEY ([Transaction Type
-- Key]) REFER