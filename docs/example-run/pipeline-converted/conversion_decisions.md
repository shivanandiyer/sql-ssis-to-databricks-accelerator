# Conversion Decisions

> **Generated:** 2026-06-30 03:39 UTC  
> **Objects converted:** 279  
> **Flagged for manual review:** 201

---

## Conversion Principle

Semantics are preserved first, syntax second. Where a SQL Server construct has no direct Databricks equivalent, this layer emits a best-effort skeleton with an explicit comment describing the gap rather than silently dropping or guessing at behaviour. Every such gap is also logged to `conversion_manifest.json` and, where it blocks safe deployment, to a file under `output/review_required/`.

## Materialized Views

0 materialized views (SQL Server indexed views) were detected in the source corpus. Wide World Importers does not use indexed/materialized views — all 26 VIEW objects are ordinary views and were converted as such. If a future source corpus includes indexed views, the recommended target is a Delta table refreshed by a scheduled Workflow task (Databricks has no native materialized-view DDL equivalent to SQL Server's indexed view at the time of writing) or `CREATE MATERIALIZED VIEW` where Databricks SQL materialized views are available in the target workspace tier.

## Type Mapping Summary

| SQL Server Type | Databricks Type | Notes |
|---|---|---|
| NVARCHAR/VARCHAR/NCHAR/CHAR/TEXT | STRING | Length bound intentionally dropped (Spark STRING is unbounded) |
| INT / BIGINT / SMALLINT / TINYINT | INT / BIGINT / SMALLINT / TINYINT | Direct mapping |
| BIT | BOOLEAN | Direct mapping |
| DECIMAL/NUMERIC(p,s) | DECIMAL(p,s) | Precision/scale preserved |
| MONEY / SMALLMONEY | DECIMAL(19,4) | Matches SQL Server's documented MONEY precision |
| FLOAT / REAL | DOUBLE / FLOAT | Direct mapping |
| DATE | DATE | Direct mapping |
| DATETIME/DATETIME2/SMALLDATETIME | TIMESTAMP | Direct mapping |
| DATETIMEOFFSET | TIMESTAMP | **Review:** explicit UTC offset is not preserved |
| TIME | STRING | **Review:** no native Spark TIME type |
| UNIQUEIDENTIFIER | STRING | Direct mapping |
| VARBINARY/BINARY/IMAGE | BINARY | Direct mapping |
| XML | STRING | **Review:** XPath operations need reimplementation via xpath_* functions |
| geography/geometry | STRING (WKT) | **Manual review required:** no native geospatial type |
| hierarchyid | STRING | **Manual review required:** no native hierarchical type |
| sql_variant | STRING | **Manual review required:** no dynamic type equivalent |
| rowversion/timestamp | BINARY | **Review:** replace change-detection use with Delta CDF |

## Procedural Construct Mapping

| T-SQL Construct | Databricks Pattern |
|---|---|
| CURSOR | Set-based DataFrame transform (preferred) or bounded Python loop |
| WHILE loop | Vectorised DataFrame op, or Python for-loop over a small fixed list |
| sp_executesql / dynamic EXEC() | Parameterised PySpark/Python string templating or Databricks SQL parameter markers |
| Temp table (#table) | PySpark DataFrame (procedure-local) or scratch-schema Delta table (cross-step state) |
| TRY/CATCH | Python try/except, or Workflow task-level retry/failure handling |
| EXECUTE AS OWNER | Unity Catalog grants — no procedural impersonation needed |

## Orchestration-Heavy Procedure Split (Rule 4)

Procedures tagged with ETL orchestration semantics (cutoff-window watermark management, staging-to-DW migration, lineage tracking) or living in the `Integration` schema are split into two files: a `databricks_sql` file containing the extracted set-based DML, and a `pyspark` `_orchestration.py` file containing the Workflow task entry point (watermark read/advance, invocation of the SQL logic). This keeps transformation logic testable and reusable independent of how/when it's scheduled.

Procedures split this way: 11

## Conversion Method Distribution

| Method | Object Count |
|---|---|
| databricks_sql | 172 |
| pyspark | 96 |
| split_sql_pyspark | 11 |

## Objects Flagged for Manual Review

See `output/review_required/*.md` for full detail per object. Summary:

| Object | Type | Classification | Top Warning |
|---|---|---|---|
| OLTP:Application.DetermineCustomerAccess | TVF_INLINE | PARTIAL_AUTOMATION | Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UD... |
| OLTP:Application.AddRoleMemberIfNonexistent | PROCEDURE | PARTIAL_AUTOMATION | TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure... |
| OLTP:Application.Configuration_ApplyAuditing | PROCEDURE | PARTIAL_AUTOMATION | TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure... |
| OLTP:Application.Configuration_ApplyColumnstoreIndexing | PROCEDURE | PARTIAL_AUTOMATION | TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure... |
| OLTP:Application.Configuration_ApplyFullTextIndexing | PROCEDURE | PARTIAL_AUTOMATION | No executable SQL statement could be extracted from this procedure's body — this usually means it us... |
| OLTP:Application.Configuration_ApplyPartitioning | PROCEDURE | PARTIAL_AUTOMATION | No executable SQL statement could be extracted from this procedure's body — this usually means it us... |
| OLTP:Application.Configuration_ApplyRowLevelSecurity | PROCEDURE | MANUAL_REDESIGN | TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure... |
| OLTP:Application.Configuration_ConfigureForEnterpriseEdition | PROCEDURE | PARTIAL_AUTOMATION | No executable SQL statement could be extracted from this procedure's body — this usually means it us... |
| OLTP:Application.Configuration_DisableInMemory | PROCEDURE | MANUAL_REDESIGN | WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. ... |
| OLTP:Application.Configuration_EnableInMemory | PROCEDURE | MANUAL_REDESIGN | WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. ... |
| OLTP:Application.Configuration_PrepareForAzureStandard | PROCEDURE | PARTIAL_AUTOMATION | No executable SQL statement could be extracted from this procedure's body — this usually means it us... |
| OLTP:Application.Configuration_RemoveAuditing | PROCEDURE | PARTIAL_AUTOMATION | TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure... |
| OLTP:Application.Configuration_RemoveColumnstoreIndexing | PROCEDURE | PARTIAL_AUTOMATION | TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure... |
| OLTP:Application.Configuration_RemoveRowLevelSecurity | PROCEDURE | MANUAL_REDESIGN | TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure... |
| OLTP:Application.CreateRoleIfNonexistent | PROCEDURE | REWRITE_REQUIRED | TRY/CATCH — replace with Python try/except in the PySpark task, or Workflow task-level retry/failure... |
| OLTP:Application.Cities | TABLE | MANUAL_REDESIGN | Column `CityID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAYS ... |
| OLTP:Application.Cities_Archive | TABLE | MANUAL_REDESIGN | Column `Location` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend ... |
| OLTP:Application.Countries | TABLE | MANUAL_REDESIGN | Column `CountryID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWA... |
| OLTP:Application.Countries_Archive | TABLE | MANUAL_REDESIGN | Column `Border` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend st... |
| OLTP:Application.DeliveryMethods | TABLE | MANUAL_REDESIGN | Column `DeliveryMethodID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERAT... |
| OLTP:Application.Logs | TABLE | PARTIAL_AUTOMATION | Column `INDEX` (CCX_Application_Logs -> STRING): Unrecognised SQL Server type 'CCX_Application_Logs'... |
| OLTP:Application.PaymentMethods | TABLE | MANUAL_REDESIGN | Column `PaymentMethodID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATE... |
| OLTP:Application.People | TABLE | MANUAL_REDESIGN | Column `PersonID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATED ALWAY... |
| OLTP:Application.StateProvinces | TABLE | MANUAL_REDESIGN | Column `StateProvinceID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERATE... |
| OLTP:Application.StateProvinces_Archive | TABLE | MANUAL_REDESIGN | Column `Border` ([sys].[geography] -> STRING): No native geospatial type in Delta Lake. Recommend st... |
| OLTP:Application.SystemParameters | TABLE | MANUAL_REDESIGN | Column `SystemParameterID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERA... |
| OLTP:Application.TransactionTypes | TABLE | MANUAL_REDESIGN | Column `TransactionTypeID` used IDENTITY/NEXT VALUE FOR in the source — replace with a Delta `GENERA... |
| OLTP:DataLoadSimulation.GetAreaCode | SCALAR_FUNCTION | PARTIAL_AUTOMATION | Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UD... |
| OLTP:DataLoadSimulation.GetBogativePhoneNumber | PROCEDURE | PARTIAL_AUTOMATION | No executable SQL statement could be extracted from this procedure's body — this usually means it us... |
| OLTP:DataLoadSimulation.GetCityLocation | SCALAR_FUNCTION | MANUAL_REDESIGN | Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UD... |
| OLTP:DataLoadSimulation.GetCustomerCount | SCALAR_FUNCTION | PARTIAL_AUTOMATION | Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UD... |
| OLTP:DataLoadSimulation.GetDeliveryMethodID | SCALAR_FUNCTION | PARTIAL_AUTOMATION | Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UD... |
| OLTP:DataLoadSimulation.GetPaymentMethodID | SCALAR_FUNCTION | PARTIAL_AUTOMATION | Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UD... |
| OLTP:DataLoadSimulation.GetPersonID | SCALAR_FUNCTION | PARTIAL_AUTOMATION | Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UD... |
| OLTP:DataLoadSimulation.GetStateProvinceID | SCALAR_FUNCTION | PARTIAL_AUTOMATION | Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UD... |
| OLTP:DataLoadSimulation.GetSupplierCategoryID | SCALAR_FUNCTION | PARTIAL_AUTOMATION | Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UD... |
| OLTP:DataLoadSimulation.GetTransactionTypeID | SCALAR_FUNCTION | PARTIAL_AUTOMATION | Function body uses procedural/security constructs (e.g. IS_ROLEMEMBER, WHILE, CURSOR) with no SQL UD... |
| OLTP:DataLoadSimulation.ActivateWebsiteLogons | PROCEDURE | REWRITE_REQUIRED | WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. ... |
| OLTP:DataLoadSimulation.AddCustomers | PROCEDURE | REWRITE_REQUIRED | WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. ... |
| OLTP:DataLoadSimulation.ChangePasswords | PROCEDURE | REWRITE_REQUIRED | WHILE loop — rewrite as a vectorised DataFrame operation, or, if iterating a small fixed list (e.g. ... |

_...and 161 more — see `conversion_manifest.json` for the complete list._

---

_This layer converts SQL objects only. SSIS orchestration assets, Databricks Workflow job definitions, and the deployment bundle are produced in a later step._