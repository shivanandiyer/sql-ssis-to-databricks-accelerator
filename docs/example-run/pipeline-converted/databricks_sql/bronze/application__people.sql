-- Source: OLTP:Application.People  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/People.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.application__people (
    PersonID INT NOT NULL,
    FullName STRING NOT NULL,
    PreferredName STRING NOT NULL,
    SearchName STRING NOT NULL COMMENT 'source type: AS',
    IsPermittedToLogon BOOLEAN NOT NULL,
    LogonName STRING,
    IsExternalLogonProvider BOOLEAN NOT NULL,
    HashedPassword BINARY,
    IsSystemUser BOOLEAN NOT NULL,
    IsEmployee BOOLEAN NOT NULL,
    IsSalesperson BOOLEAN NOT NULL,
    UserPreferences STRING,
    PhoneNumber STRING,
    FaxNumber STRING,
    EmailAddress STRING,
    Photo BINARY,
    CustomFields STRING,
    OtherLanguages STRING COMMENT 'source type: AS',
    LastEditedBy INT NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Application.People'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);

-- Conversion notes:
-- Column `PersonID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED
-- ALWAYS AS IDENTITY` column or a surrogate-key generation step in the loading pipeline (see
-- target_state_architecture.md, Unity Catalog section).
-- Column `SearchName` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING. MANUAL
-- REVIEW REQUIRED.
-- Column `OtherLanguages` (AS -> STRING): Unrecognised SQL Server type 'AS' — defaulted to STRING.
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
-- [FK_Application_People_Application_People] FOREIGN KEY ([LastEditedBy]) REFERENCES
-- [Application].[People] ([P
-- Source table used SQL Server temporal tables (FOR SYSTEM_TIME / paired _Archive table). Recommended
-- replacement: enable `delta.enableChangeDataFeed` and query history via `TIMESTAMP AS OF` / `VERSION
-- AS OF`, or `table_changes()`. The paired _Archive table is converted separately and should be
-- reconciled with this table's Delta history rather than kept as a second physical table long-term.