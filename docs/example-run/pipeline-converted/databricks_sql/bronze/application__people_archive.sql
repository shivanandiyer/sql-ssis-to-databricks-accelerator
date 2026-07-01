-- Source: OLTP:Application.People_Archive  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Tables/People_Archive.sql)
-- Converted: TABLE -> Delta table. Semantics preserved; SQL Server-specific DDL clauses
-- (IDENTITY, system-versioning, MEMORY_OPTIMIZED, partition schemes) translated or
-- flagged below rather than silently dropped.

CREATE TABLE IF NOT EXISTS wwi_<env>.bronze.application__people_archive (
    PersonID INT NOT NULL,
    FullName STRING NOT NULL,
    PreferredName STRING NOT NULL,
    SearchName STRING NOT NULL,
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
    OtherLanguages STRING,
    LastEditedBy INT NOT NULL,
    ValidFrom TIMESTAMP NOT NULL,
    ValidTo TIMESTAMP NOT NULL
)
USING DELTA
COMMENT 'Converted from OLTP:Application.People_Archive'
TBLPROPERTIES (
  'delta.enableChangeDataFeed' = 'true'
);
