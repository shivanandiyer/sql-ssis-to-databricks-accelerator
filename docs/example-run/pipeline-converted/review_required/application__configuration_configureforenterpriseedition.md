# Review Required: OLTP:Application.Configuration_ConfigureForEnterpriseEdition

- **Object type:** PROCEDURE
- **Source file:** /Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/Application/Stored Procedures/Configuration_ConfigureForEnterpriseEdition.sql
- **Classification:** PARTIAL_AUTOMATION

## Why this needs manual review

- No executable SQL statement could be extracted from this procedure's body — this usually means it uses a construct our extractor doesn't recognise (e.g. OPENJSON, a non-standard DML shape) rather than that it has no logic. MANUAL REVIEW REQUIRED before deployment; do not treat this as a safe no-op.

## Source DDL (for reference)

```sql
CREATE PROCEDURE [Application].[Configuration_ConfigureForEnterpriseEdition]
AS
BEGIN

    EXEC [Application].[Configuration_ApplyColumnstoreIndexing];

    EXEC [Application].[Configuration_ApplyFullTextIndexing];

    EXEC [Application].[Configuration_EnableInMemory];

    EXEC [Application].[Configuration_ApplyPartitioning];

END;
```