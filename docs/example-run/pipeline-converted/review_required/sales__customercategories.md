# Review Required: OLTP:Sales.CustomerCategories

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Sales/Tables/CustomerCategories.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `CustomerCategoryID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `ValidFrom` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Column `ValidTo` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Sales_CustomerCategories_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[Peopl
- Source table used SQL Server temporal tables (FOR SYSTEM_TIME / paired _Archive table). Recommended replacement: enable `delta.enableChangeDataFeed` and query history via `TIMESTAMP AS OF` / `VERSION AS OF`, or `table_changes()`. The paired _Archive table is converted separately and should be reconciled with this table's Delta history rather than kept as a second physical table long-term.

## Source DDL (for reference)

```sql
CREATE TABLE [Sales].[CustomerCategories] (
    [CustomerCategoryID]   INT                                         CONSTRAINT [DF_Sales_CustomerCategories_CustomerCategoryID] DEFAULT (NEXT VALUE FOR [Sequences].[CustomerCategoryID]) NOT NULL,
    [CustomerCategoryName] NVARCHAR (50)                               NOT NULL,
    [LastEditedBy]         INT                                         NOT NULL,
    [ValidFrom]            DATETIME2 (7) GENERATED ALWAYS AS ROW START NOT NULL,
    [ValidTo]              DATETIME2 (7) GENERATED ALWAYS AS ROW END   NOT NULL,
    CONSTRAINT [PK_Sales_CustomerCategories] PRIMARY KEY CLUSTERED ([CustomerCategoryID] ASC),
    CONSTRAINT [FK_Sales_CustomerCategories_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([PersonID]),
    CONSTRAINT [UQ_Sales_CustomerCategories_CustomerCategoryName] UNIQUE NONCLUSTERED ([CustomerCategoryName] ASC),
    PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE=[Sales].[CustomerCategories_Archive], DATA_CONSISTENCY_CHECK=ON));


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'Categories for customers (ie restaurants, cafes, supermarkets, etc.)', @level0type = N'SCHEMA', @level0name = N'Sales', @level1type = N'TABLE', @level1name = N'CustomerCategories';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Numeric ID used for reference to a customer category within the database', @level0type = N'SCHEMA', @level0name = N'Sales', @level1type = N'TABLE', @level1name = N'CustomerCategories', @level2type = N'COLUMN', @level2name = N'CustomerCategoryID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Full name of the category that customers can be assigned to', @level0type = N'SCHEMA', @level0name = N'Sales', @level1type = N'TABLE', @level1name = N'CustomerCategories', @level2type = N'COLUMN', @level2name = N'CustomerCategoryName';
```