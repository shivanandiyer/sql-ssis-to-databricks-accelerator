# Review Required: OLTP:Application.TransactionTypes

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/TransactionTypes.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `TransactionTypeID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `ValidFrom` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Column `ValidTo` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Application_TransactionTypes_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[P
- Source table used SQL Server temporal tables (FOR SYSTEM_TIME / paired _Archive table). Recommended replacement: enable `delta.enableChangeDataFeed` and query history via `TIMESTAMP AS OF` / `VERSION AS OF`, or `table_changes()`. The paired _Archive table is converted separately and should be reconciled with this table's Delta history rather than kept as a second physical table long-term.

## Source DDL (for reference)

```sql
CREATE TABLE [Application].[TransactionTypes] (
    [TransactionTypeID]   INT                                         CONSTRAINT [DF_Application_TransactionTypes_TransactionTypeID] DEFAULT (NEXT VALUE FOR [Sequences].[TransactionTypeID]) NOT NULL,
    [TransactionTypeName] NVARCHAR (50)                               NOT NULL,
    [LastEditedBy]        INT                                         NOT NULL,
    [ValidFrom]           DATETIME2 (7) GENERATED ALWAYS AS ROW START NOT NULL,
    [ValidTo]             DATETIME2 (7) GENERATED ALWAYS AS ROW END   NOT NULL,
    CONSTRAINT [PK_Application_TransactionTypes] PRIMARY KEY CLUSTERED ([TransactionTypeID] ASC),
    CONSTRAINT [FK_Application_TransactionTypes_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([PersonID]),
    CONSTRAINT [UQ_Application_TransactionTypes_TransactionTypeName] UNIQUE NONCLUSTERED ([TransactionTypeName] ASC),
    PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE=[Application].[TransactionTypes_Archive], DATA_CONSISTENCY_CHECK=ON));


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = N'Types of customer, supplier, or stock transactions (ie: invoice, credit note, etc.)', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'TransactionTypes';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Numeric ID used for reference to a transaction type within the database', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'TransactionTypes', @level2type = N'COLUMN', @level2name = N'TransactionTypeID';


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Full name of the transaction type', @level0type = N'SCHEMA', @level0name = N'Application', @level1type = N'TABLE', @level1name = N'TransactionTypes', @level2type = N'COLUMN', @level2name = N'TransactionTypeName';
```