-- Source: OLTP:Website.ActivateWebsiteLogon  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Website/Stored Procedures/ActivateWebsiteLogon.sql)
-- Converted: PROCEDURE -> Databricks SQL transformation logic (no procedural
-- constructs detected; safe to express as set-based SQL).

UPDATE `Application`.People
    SET IsPermittedToLogon = 1,
        LogonName = @LogonName,
        HashedPassword = HASHBYTES(N'SHA2_256', @InitialPassword + FullName),
        UserPreferences = (SELECT UserPreferences FROM `Application`.People WHERE PersonID = 1) -- Person 1 has User Preferences template
    WHERE PersonID = @PersonID
    AND PersonID <> 1
    AND IsPermittedToLogon = 0;