# Review Required: OLTP:Application.People

- **Object type:** TABLE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/People.sql
- **Classification:** MANUAL_REDESIGN

## Why this needs manual review

- Column `PersonID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see target_state_architecture.md, Unity Catalog section).
- Column `SearchName` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `OtherLanguages` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING. MANUAL REVIEW REQUIRED.
- Column `ValidFrom` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Column `ValidTo` is a SQL Server system-versioning period column (GENERATED ALWAYS AS ROW START/END) — dropped from the Delta DDL. NOTE: Delta Time Travel (VERSION/TIMESTAMP AS OF) is NOT equivalent to this column's semantics — Time Travel returns the whole table's state at a commit, while this column tracks each row's own validity window independent of write/commit history. Any query that did `... FOR SYSTEM_TIME AS OF @ts` must be rewritten as an explicit point-in-time filter (`WHERE valid_from <= @ts AND (valid_to > @ts OR valid_to IS NULL)`) against the still-present ValidFrom/ValidTo columns — not replaced with Delta Time Travel. MANUAL REVIEW REQUIRED.
- Foreign key not enforced by Delta Lake (informational only): CONSTRAINT [FK_Application_People_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([P
- Source table used SQL Server temporal tables (FOR SYSTEM_TIME / paired _Archive table). Recommended replacement: enable `delta.enableChangeDataFeed` and query history via `TIMESTAMP AS OF` / `VERSION AS OF`, or `table_changes()`. The paired _Archive table is converted separately and should be reconciled with this table's Delta history rather than kept as a second physical table long-term.

## Source DDL (for reference)

```sql
CREATE TABLE [Application].[People] (
    [PersonID]                INT                                         CONSTRAINT [DF_Application_People_PersonID] DEFAULT (NEXT VALUE FOR [Sequences].[PersonID]) NOT NULL,
    [FullName]                NVARCHAR (50)                               NOT NULL,
    [PreferredName]           NVARCHAR (50)                               NOT NULL,
    [SearchName]              AS                                          (concat([PreferredName],N' ',[FullName])) PERSISTED NOT NULL,
    [IsPermittedToLogon]      BIT                                         NOT NULL,
    [LogonName]               NVARCHAR (256)                              NULL,
    [IsExternalLogonProvider] BIT                                         NOT NULL,
    [HashedPassword]          VARBINARY (MAX)                             NULL,
    [IsSystemUser]            BIT                                         NOT NULL,
    [IsEmployee]              BIT                                         NOT NULL,
    [IsSalesperson]           BIT                                         NOT NULL,
    [UserPreferences]         NVARCHAR (MAX)                              NULL,
    [PhoneNumber]             NVARCHAR (20)                               NULL,
    [FaxNumber]               NVARCHAR (20)                               NULL,
    [EmailAddress]            NVARCHAR (256)                              NULL,
    [Photo]                   VARBINARY (MAX)                             NULL,
    [CustomFields]            NVARCHAR (MAX)                              NULL,
    [OtherLanguages]          AS                                          (json_query([CustomFields],N'$.OtherLanguages')),
    [LastEditedBy]            INT                                         NOT NULL,
    [ValidFrom]               DATETIME2 (7) GENERATED ALWAYS AS ROW START NOT NULL,
    [ValidTo]                 DATETIME2 (7) GENERATED ALWAYS AS ROW END   NOT NULL,
    CONSTRAINT [PK_Application_People] PRIMARY KEY CLUSTERED ([PersonID] ASC),
    CONSTRAINT [FK_Application_People_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES [Application].[People] ([PersonID]),
    PERIOD FOR SYSTEM_TIME ([ValidFrom], [ValidTo])
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE=[Application].[People_Archive], DATA_CONSISTENCY_CHECK=ON));




GO
CREATE NONCLUSTERED INDEX [IX_Application_People_IsEmployee]
    ON [Application].[People]([IsEmployee] ASC);


GO
CREATE NONCLUSTERED INDEX [IX_Application_People_IsSalesperson]
    ON [Application].[People]([IsSalesperson] ASC);


GO
CREATE NONCLUSTERED INDEX [IX_Application_People_FullName]
    ON [Application].[People]([FullName] ASC);


GO
CREATE NONCLUSTERED INDEX [IX_Application_People_Perf_20160301_05]
    ON [Application].[People]([IsPermittedToLogon] ASC, [PersonID] ASC)
    INCLUDE([FullName], [EmailAddress]);


GO
EXECUTE sp_addextendedproperty @name = N'Description', @value = 'Allows quickly locating employees', @level0type = N'SCHEMA', @level0n
```