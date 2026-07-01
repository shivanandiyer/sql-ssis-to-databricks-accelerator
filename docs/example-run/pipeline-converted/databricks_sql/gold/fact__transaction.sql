-- Source: DW:Fact.Transaction  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-dw-ssdt/wwi-dw-ssdt/Fact/Tables/Transaction.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.gold.transaction (
    Transaction STRING NOT NULL COMMENT 'source type: Key]',
    Date STRING NOT NULL COMMENT 'source type: Key]',
    Customer STRING COMMENT 'source type: Key]',
    Bill STRING COMMENT 'source type: To',
    Supplier STRING COMMENT 'source type: Key]',
    Transaction STRING NOT NULL COMMENT 'source type: Type',
    Payment STRING COMMENT 'source type: Method',
    WWI STRING COMMENT 'source type: Customer',
    WWI STRING COMMENT 'source type: Supplier',
    WWI STRING COMMENT 'source type: Invoice',
    WWI STRING COMMENT 'source type: Purchase',
    Supplier STRING COMMENT 'source type: Invoice',
    Total STRING NOT NULL COMMENT 'source type: Excluding',
    Tax STRING NOT NULL COMMENT 'source type: Amount]',
    Total STRING NOT NULL COMMENT 'source type: Including',
    Outstanding STRING NOT NULL COMMENT 'source type: Balance]',
    Is STRING NOT NULL COMMENT 'source type: Finalized]',
    Lineage STRING NOT NULL COMMENT 'source type: Key]'
)
USING DELTA
-- TODO: confirm partition column from source PARTITION SCHEME before enabling:
-- PARTITIONED BY (<date_or_period_column>)
COMMENT 'Converted from DW:Fact.Transaction'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `Transaction` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Transaction` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `Date` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `Customer` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Bill` (To -> STRING): Unrecognised SQL Server type 'To' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `Supplier` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Transaction` (Type -> STRING): Unrecognised SQL Server type 'Type' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Payment` (Method -> STRING): Unrecognised SQL Server type 'Method' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Customer -> STRING): Unrecognised SQL Server type 'Customer' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Supplier -> STRING): Unrecognised SQL Server type 'Supplier' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `WWI` (Purchase -> STRING): Unrecognised SQL Server type 'Purchase' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Supplier` (Invoice -> STRING): Unrecognised SQL Server type 'Invoice' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Total` (Excluding -> STRING): Unrecognised SQL Server type 'Excluding' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Tax` (Amount] -> STRING): Unrecognised SQL Server type 'Amount]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Total` (Including -> STRING): Unrecognised SQL Server type 'Including' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Outstanding` (Balance] -> STRING): Unrecognised SQL Server type 'Balance]' — defaulted to
-- STRING. MANUAL REVIEW REQUIRED.
-- Column `Is` (Finalized] -> STRING): Unrecognised SQL Server type 'Finalized]' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `Lineage` (Key] -> STRING): Unrecognised SQL Server type 'Key]' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Transaction_Bill_To_Customer_Key_Dimension_Customer] FOREIGN KEY ([Bill To Customer Key])
-- REFERENCES
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Transaction_Customer_Key_Dimension_Customer] FOREIGN KEY ([Customer Key]) REFERENCES
-- [Dimension].[Cu
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Transaction_Date_Key_Dimension_Date] FOREIGN KEY ([Date Key]) REFERENCES [Dimension].[Date]
-- ([Date])
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Transaction_Payment_Method_Key_Dimension_Payment Method] FOREIGN KEY ([Payment Method Key])
-- REFERENC
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Transaction_Supplier_Key_Dimension_Supplier] FOREIGN KEY ([Supplier Key]) REFERENCES
-- [Dimension].[Su
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Fact_Transaction_Transaction_Type_Key_Dimension_Transaction Type] FOREIGN KEY ([Transaction Type
-- Key]) RE