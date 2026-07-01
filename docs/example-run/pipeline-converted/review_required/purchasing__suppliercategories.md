# Review Required: OLTP:Purchasing.SupplierCategories

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Purchasing/Tables/SupplierCategories.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `SupplierCategoryID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `ValidFrom` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Column `ValidTo` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Purchasing_SupplierCategories_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[
- Source table used SQL Server temporal tables (FOR SYSTEM_TIME / paired _Archive table). Recommended replacement: enable `delta.enableChangeDataFeed` and query history via `TIMESTAMP AS OF` / `VERSION AS OF`, or `table_changes()`. The paired _Archive table is converted separately and should be reconciled with this table's Delta history rather than kept as a second physical table long-term.

## Source DDL (for reference)

```sql
CREATE TABLE [Purchasing].[SupplierCategories] (
    [SupplierCategoryID]   INT                                         CONSTRAINT [DF_Purchasing_SupplierCategories_SupplierCategoryID] DEFAULT (NEXT VALUE FOR [Sequences].[SupplierCategoryID]) NOT NULL,
    [SupplierCategoryName] NVARCHAR (50)                               NOT NULL,
    [LastEditedBy]         INT                                         NOT NULL,
    [ValidFrom]            DATETIME2 (7) GENERATED ALWAYS AS ROW START NOT NULL,
    [ValidTo]              DATETIME2 (7) GENERATED ALWAYS AS ROW END   NOT NULL,
    CONSTRAINT [PK_Purchasing_SupplierCategories] PRIMARY KEY CLUSTERED ([SupplierCategoryID] ASC),
    CONSTRAINT [FK_Purchasing_SupplierCategories_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([PersonID]),
    CONSTRAINT [UQ_Purchasing_SupplierCategories_SupplierCategoryName] UNIQUE NONCLUSTERED ([SupplierCategoryName] ASC),
    PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE=[Purchasing].[SupplierCategories_Archive], DATA_CONSISTENCY_CHECK=ON));


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'Categories for suppliers (ie novelties, toys, clothing, packaging, etc.)', @level0type = N'SCHEMA', @level0name = N'Purchasing', @level1type = N'TABLE', @level1name = N'SupplierCategories';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Numeric ID used for reference to a supplier category within the database', @level0type = N'SCHEMA', @level0name = N'Purchasing', @level1type = N'TABLE', @level1name = N'SupplierCategories', @level2type = N'COLUMN', @level2name = N'SupplierCategoryID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Full name of the category that suppliers can be assigned to', @level0type = N'SCHEMA', @level0name = N'Purchasing', @level1type = N'TABLE', @level1name = N'SupplierCategories', @level2type = N'COLUMN', @level2name = N'SupplierCategoryName';
```