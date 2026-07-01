-- Source: OLTP:WebApi.TransactionTypes  (/Users/shivaiyer/Documents/Claude/sql-server-samples/samples/databases/wide-world-importers/wwi-ssdt/wwi-ssdt/WebApi/Views/TransactionTypes.sql)
-- Converted: VIEW -> Databricks SQL view. Body translated with best-effort syntax
-- rewrites (bracket identifiers, ISNULL->COALESCE, GETDATE()->current_timestamp(),
-- TOP(n)->LIMIT n).

CREATE OR REPLACE VIEW wwi_<env>.silver.webapi__transactiontypes AS
SELECT TransactionTypeID, TransactionTypeName
FROM `Application`.TransactionTypes
;