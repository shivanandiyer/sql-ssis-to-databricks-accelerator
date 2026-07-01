-- Source: OLTP:Warehouse.StockItems  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Warehouse/Tables/StockItems.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.warehouse__stockitems (
    StockItemID INT NOT NULL,
    StockItemName STRING NOT NULL,
    SupplierID INT NOT NULL,
    ColorID INT,
    UnitPackageID INT NOT NULL,
    OuterPackageID INT NOT NULL,
    Brand STRING,
    Size STRING,
    LeadTimeDays INT NOT NULL,
    QuantityPerOuter INT NOT NULL,
    IsChillerStock BOOLEAN NOT NULL,
    Barcode STRING,
    TaxRate DECIMAL(18,3) NOT NULL,
    UnitPrice DECIMAL(18,2) NOT NULL,
    RecommendedRetailPrice DECIMAL(18,2),
    TypicalWeightPerUnit DECIMAL(18,3) NOT NULL,
    MarketingComments STRING,
    InternalComments STRING,
    Photo BINARY,
    CustomFields STRING,
    Tags STRING COMMENT 'source type: AS',
    SearchDetails STRING COMMENT 'source type: AS',
    LastEditedBy INT NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Warehouse.StockItems'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `StockItemID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `Tags` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING. MANUAL REVIEW
-- REQUIRED.
-- Column `SearchDetails` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING.
-- MANUAL REVIEW REQUIRED.
-- Column `ValidFrom` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW
-- START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT
-- equivalent to this column's semantics — Time Travel returns the whole table's state at a commit,
-- while this column tracks each row's own validity window independent of write/commit history. Any
-- query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter
-- (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present
-- ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
-- Column `ValidTo` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END)
-- — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to
-- this column's semantics — Time Travel returns the whole table's state at a commit, while this column
-- tracks each row's own validity window independent of write/commit history. Any query that did `...
-- FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from
-- <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo
-- columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItems_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[People] (
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItems_ColorID_Warehouse_Colors] FOREIGN KEY ([ColorID]) REFERENCES
-- [Warehouse].[Colors] ([
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItems_OuterPackageID_Warehouse_PackageTypes] FOREIGN KEY ([OuterPackageID])
-- REFERENCES [Wa
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItems_SupplierID_Purchasing_Suppliers] FOREIGN KEY ([SupplierID]) REFERENCES
-- [Purchasing].
-- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT
-- [FK_Warehouse_StockItems_UnitPackageID_Warehouse_PackageTypes] FOREIGN KEY ([UnitPackageID])
-- REFERENCES [Ware
-- Source table used SQL Server temporal tables (FOR SYSTEM_TIME / paired _Archive table). Recommended
-- replacement: enable `delta.enableChangeDataFeed` and query history via `TIMESTAMP AS OF` / `VERSION
-- AS OF`, or `table_changes()`. The paired _Archive table is converted separately and should be
-- reconciled with this table's Delta history rather than kept as a second physical table long-term.