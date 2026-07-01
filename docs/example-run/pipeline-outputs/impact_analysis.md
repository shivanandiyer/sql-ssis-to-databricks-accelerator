# Wide World Importers — Migration Impact Analysis

> **Accelerator:** WWI SQL Server → Databricks Modernisation Accelerator v0.1.0  
> **Generated:** 2026-06-30 12:34 UTC  
> **Basis:** Static analysis of `inventory.json` (419 objects) and `dependencies.json` (402 nodes / 566 edges)  
> **Scope:** SQL Server (OLTP + DW) objects and SSIS package `DailyETLMain` → Databricks (Unity Catalog, Delta Lake, PySpark, Databricks Workflows)

---

## Executive Summary

- **431 objects** assessed across 12 impact dimensions (SQL dialect, procedural logic, SSIS control/data flow, dependency criticality, ordering constraints, data type risk, performance risk, security model change, operational scheduling, testing complexity, rollback complexity).
- **83 (19%)** objects are lift-and-shift friendly — straightforward DDL/DML translation with high automated-conversion confidence.
- **179 (42%)** are candidates for partial automation — deterministic pattern-based conversion with required manual review.
- **63 (15%)** require a rewrite — procedural logic or SSIS constructs with no direct Databricks equivalent.
- **106 (25%)** require manual redesign — data types, performance patterns, or compounding risk factors with no automated path.

### Migration Strategy Distribution

| Classification | Object Count | % of Total |
|---|---|---|
| Lift-and-shift friendly | 83 | 19% |
| Partial automation possible | 179 | 42% |
| Rewrite required | 63 | 15% |
| Manual redesign required | 106 | 25% |

### Average Risk Score by Dimension (0=none, 5=severe)

| Dimension | Average Score Across All Objects |
|---|---|
| Sql Dialect | 0.95 |
| Procedural Logic | 0.36 |
| Ssis Control Flow | 0.32 |
| Ssis Data Flow | 0.09 |
| Dependency Criticality | 1.0 |
| Ordering Constraints | 0.33 |
| Data Type Risk | 0.4 |
| Performance Risk | 0.3 |
| Security Risk | 0.56 |
| Operational Scheduling | 0.3 |
| Testing Complexity | 0.44 |
| Rollback Complexity | 0.76 |

---

## 1. SQL Dialect Conversion Complexity

T-SQL constructs scanned: `PIVOT`/`UNPIVOT`, `MERGE`, `FOR XML`/`FOR JSON`, `FOR SYSTEM_TIME`, `APPLY`, `OPENROWSET`/`OPENDATASOURCE`/linked servers, `OUTPUT INSERTED/DELETED`, `TOP(n)`, `IDENTITY()`, `ISNULL()`.

| Object | Type | Score | Factors |
|---|---|---|---|
| OLTP:Integration.GetStockItemUpdates | PROCEDURE | 5 | FOR\s+SYSTEM_TIME(+4); ISNULL\s*\((+1) |
| OLTP:Application.Configuration_EnableInMemory | PROCEDURE | 5 | MERGE(+3); FOR\s+SYSTEM_TIME(+4); APPLY(+3); IDENTITY\s*\((+1) |
| OLTP:Warehouse.ColdRoomTemperatures | TABLE | 5 | FOR\s+SYSTEM_TIME(+4); IDENTITY\s*\((+1) |
| OLTP:Application.Configuration_DisableInMemory | PROCEDURE | 5 | MERGE(+3); FOR\s+SYSTEM_TIME(+4); APPLY(+3); IDENTITY\s*\((+1) |
| OLTP:Website.RecordColdRoomTemperatures | PROCEDURE | 5 | MERGE(+3); APPLY(+3) |
| OLTP:WebApi.InsertBuyingGroupsFromJson | PROCEDURE | 5 | OPENJSON(+4); OUTPUT\s+INSERTED(+2) |
| OLTP:WebApi.InsertCitiesFromJson | PROCEDURE | 5 | OPENJSON(+4); OUTPUT\s+INSERTED(+2) |
| OLTP:WebApi.InsertColorsFromJson | PROCEDURE | 5 | OPENJSON(+4); OUTPUT\s+INSERTED(+2) |
| OLTP:WebApi.InsertCountriesFromJson | PROCEDURE | 5 | OPENJSON(+4); OUTPUT\s+INSERTED(+2) |
| OLTP:WebApi.InsertCustomerCategoriesFromJson | PROCEDURE | 5 | OPENJSON(+4); OUTPUT\s+INSERTED(+2) |
| OLTP:WebApi.InsertCustomersFromJson | PROCEDURE | 5 | OPENJSON(+4); OUTPUT\s+INSERTED(+2) |
| OLTP:WebApi.InsertDeliveryMethodsFromJson | PROCEDURE | 5 | OPENJSON(+4); OUTPUT\s+INSERTED(+2) |
| OLTP:WebApi.InsertPackageTypesFromJson | PROCEDURE | 5 | OPENJSON(+4); OUTPUT\s+INSERTED(+2) |
| OLTP:WebApi.InsertPaymentMethodsFromJson | PROCEDURE | 5 | OPENJSON(+4); OUTPUT\s+INSERTED(+2) |
| OLTP:WebApi.InsertStateProvincesFromJson | PROCEDURE | 5 | OPENJSON(+4); OUTPUT\s+INSERTED(+2) |

## 2. T-SQL Procedural Logic Complexity

Patterns scanned: `CURSOR`, `sp_executesql`/dynamic `EXEC()`, `WHILE`, `GOTO`, `TRY/CATCH`, temp tables, table variables, `RAISERROR`/`THROW`. These have no direct PySpark/Databricks SQL equivalent and require translation to set-based DataFrame/SQL logic or Python control flow.

| Object | Type | Score | Factors |
|---|---|---|---|
| OLTP:Integration.GetCityUpdates | PROCEDURE | 5 | CURSOR(+5); WHILE(+3); #\w+(+2) |
| OLTP:Integration.GetStockItemUpdates | PROCEDURE | 5 | CURSOR(+5); WHILE(+3); #\w+(+2) |
| OLTP:Integration.GetEmployeeUpdates | PROCEDURE | 5 | CURSOR(+5); WHILE(+3); #\w+(+2) |
| OLTP:DataLoadSimulation.UpdateCustomFields | PROCEDURE | 5 | CURSOR(+5); WHILE(+3); RAISERROR(+1) |
| OLTP:Integration.GetCustomerUpdates | PROCEDURE | 5 | CURSOR(+5); WHILE(+3); #\w+(+2) |
| OLTP:Integration.GetSupplierUpdates | PROCEDURE | 5 | CURSOR(+5); WHILE(+3); #\w+(+2) |
| OLTP:Integration.GetPaymentMethodUpdates | PROCEDURE | 5 | CURSOR(+5); WHILE(+3); #\w+(+2) |
| OLTP:Integration.GetTransactionTypeUpdates | PROCEDURE | 5 | CURSOR(+5); WHILE(+3); #\w+(+2) |
| OLTP:DataLoadSimulation.PickStockForCustomerOrders | PROCEDURE | 5 | CURSOR(+5); WHILE(+3) |
| OLTP:DataLoadSimulation.RecordInvoiceDeliveries | PROCEDURE | 5 | CURSOR(+5); WHILE(+3) |
| OLTP:DataLoadSimulation.DailyProcessToCreateHistory | PROCEDURE | 5 | WHILE(+3); #\w+(+2); RAISERROR(+1) |
| OLTP:DataLoadSimulation.InvoicePickedOrders | PROCEDURE | 5 | CURSOR(+5); WHILE(+3) |
| OLTP:DataLoadSimulation.ReceivePurchaseOrders | PROCEDURE | 5 | CURSOR(+5); WHILE(+3) |
| OLTP:Application.Configuration_EnableInMemory | PROCEDURE | 4 | WHILE(+3); RAISERROR(+1) |
| OLTP:Application.Configuration_DisableInMemory | PROCEDURE | 4 | WHILE(+3); RAISERROR(+1) |

## 3. SSIS Control Flow Conversion Complexity

Every SSIS task/container/package becomes a Databricks Workflow task or notebook orchestration step. `DailyETLMain` has 13 Sequence Containers (one per entity) each running a fixed 5-step pattern (cutoff lookup → truncate staging → extract → lineage key → migrate). Precedence constraints map to Workflow task dependencies; SSIS Expressions (15 found) require manual translation since Databricks Workflows has no direct expression-language equivalent — these become Python/Jinja parameterisation.

| Object Type | Count | Avg Score |
|---|---|---|
| SSIS_EXECUTE_SQL | 53 | 1.0 |
| SSIS_EXPRESSION | 15 | 3.0 |
| SSIS_PACKAGE | 1 | 2.0 |
| SSIS_SEQUENCE_CONTAINER | 13 | 3.0 |

## 4. SSIS Data Flow Conversion Complexity

13 Data Flow tasks (`Extract Updated <Entity> Data to Staging`) extract from OLTP source tables/views into `Integration.<Entity>_Staging` tables. Each maps to a PySpark read → transform → write (Delta, overwrite mode) job. Components beyond simple OLE DB Source → Destination (lookups, derived columns, conditional splits) raise conversion complexity.

| Object | Score | Classification | Factors |
|---|---|---|---|
| SSIS:DailyETLMain:Extract Updated City Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract Updated Customer Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract Updated Employee Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract Updated Movement Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract Updated Order Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract Updated Payment Method Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract Updated Purchase Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract Updated Sale Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract All Stock Holding Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract Updated Stock Item Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract Updated Supplier Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract Updated Transaction Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |
| SSIS:DailyETLMain:Extract Updated Transaction Type Data to Staging | 3 | Partial automation possible | data_flow_pipeline_to_pyspark(+2); components=2(+1) |

## 5. Dependency Criticality & Blast Radius

Criticality is derived from fan-in (direct dependents) in the dependency graph; blast radius adds the full transitive closure of downstream dependents — i.e. everything that breaks, directly or indirectly, if this object's conversion is wrong or delayed.

### Highest Blast-Radius Objects

| Object | Type | Direct Dependents | Transitive Dependents | Sample Downstream |
|---|---|---|---|---|
| DW:Integration.Lineage | TABLE | 15 | 76 | DW:Application.Configuration_PopulateLargeSaleTable, DW:Integration.GetLineageKey, DW:Integration.MigrateStagedCityData, DW:Integration.MigrateStagedCustomerData |
| DW:Integration.ETL | TABLE | 14 | 75 | DW:Integration.GetLastETLCutoffTime, DW:Integration.MigrateStagedCityData, DW:Integration.MigrateStagedCustomerData, DW:Integration.MigrateStagedEmployeeData |
| DW:Dimension.Stock | TABLE | 6 | 41 | DW:Integration.MigrateStagedMovementData, DW:Integration.MigrateStagedOrderData, DW:Integration.MigrateStagedPurchaseData, DW:Integration.MigrateStagedSaleData |
| OLTP:Application.People | TABLE | 27 | 39 | OLTP:Application.Configuration_ApplyFullTextIndexing, OLTP:Application.Configuration_ConfigureForEnterpriseEdition, OLTP:DataLoadSimulation.ActivateWebsiteLogons, OLTP:DataLoadSimulation.AddCustomers |
| DW:Dimension.Customer | TABLE | 7 | 39 | DW:Application.Configuration_ReseedETL, DW:Integration.MigrateStagedCustomerData, DW:Integration.MigrateStagedMovementData, DW:Integration.MigrateStagedOrderData |
| DW:Integration.GetLastETLCutoffTime | PROCEDURE | 13 | 35 | SSIS:DailyETLMain:Get Last City ETL Cutoff Time, SSIS:DailyETLMain:Get Last Customer ETL Cutoff Time, SSIS:DailyETLMain:Get Last Employee ETL Cutoff Time, SSIS:DailyETLMain:Get Last Movement ETL Cutoff Time |
| DW:Dimension.Supplier | TABLE | 4 | 35 | DW:Integration.MigrateStagedMovementData, DW:Integration.MigrateStagedPurchaseData, DW:Integration.MigrateStagedSupplierData, DW:Integration.MigrateStagedTransactionData |
| DW:Dimension.City | TABLE | 5 | 33 | DW:Application.Configuration_ReseedETL, DW:Integration.MigrateStagedCityData, DW:Integration.MigrateStagedOrderData, DW:Integration.MigrateStagedSaleData |
| DW:Dimension.Employee | TABLE | 5 | 33 | DW:Application.Configuration_ReseedETL, DW:Integration.MigrateStagedEmployeeData, DW:Integration.MigrateStagedOrderData, DW:Integration.MigrateStagedSaleData |
| DW:Dimension.Transaction | TABLE | 3 | 32 | DW:Integration.MigrateStagedMovementData, DW:Integration.MigrateStagedTransactionData, DW:Integration.MigrateStagedTransactionTypeData, SSIS:DailyETLMain:Extract Updated Movement Data to Staging |
| OLTP:Sales.Customers | TABLE | 24 | 31 | OLTP:Application.Configuration_ApplyFullTextIndexing, OLTP:Application.Configuration_ConfigureForEnterpriseEdition, OLTP:Application.Configuration_DisableInMemory, OLTP:Application.Configuration_EnableInMemory |
| OLTP:Warehouse.StockItems | TABLE | 23 | 29 | OLTP:Application.Configuration_ApplyFullTextIndexing, OLTP:Application.Configuration_ConfigureForEnterpriseEdition, OLTP:Application.Configuration_DisableInMemory, OLTP:Application.Configuration_EnableInMemory |
| DW:Dimension.Payment | TABLE | 2 | 29 | DW:Integration.MigrateStagedPaymentMethodData, DW:Integration.MigrateStagedTransactionData, SSIS:DailyETLMain:Extract Updated Payment Method Data to Staging, SSIS:DailyETLMain:Extract Updated Transaction Data to Staging |
| DW:Integration.Sale_Staging | TABLE | 2 | 26 | DW:Application.Configuration_PopulateLargeSaleTable, DW:Fact.Sale, DW:Integration.MigrateStagedSaleData, SSIS:DailyETLMain:Extract Updated Sale Data to Staging |
| OLTP:Application.Cities | TABLE | 17 | 25 | OLTP:Application.Configuration_ApplyFullTextIndexing, OLTP:Application.Configuration_ApplyRowLevelSecurity, OLTP:Application.Configuration_ConfigureForEnterpriseEdition, OLTP:Application.DetermineCustomerAccess |

## 6. Ordering Constraints

Migration sequencing is governed by: (a) dimension-before-fact load order (SCD2 surrogate keys must exist before fact loads resolve them), (b) the per-entity cutoff-window watermark chain (`Get Last ETL Cutoff Time` → extract → `Get Lineage Key` → migrate), and (c) staging truncate-then-load within a single run. Any reordering during cutover risks silent data loss or duplicate loads.

| Object | Type | Score | Factors |
|---|---|---|---|
| DW:Integration.MigrateStagedMovementData | PROCEDURE | 3 | watermark_dependent_run_order(+2); fan_out=7(broad_upstream_reads) |
| DW:Integration.MigrateStagedCityData | PROCEDURE | 3 | watermark_dependent_run_order(+2); fan_out=5(broad_upstream_reads) |
| DW:Integration.MigrateStagedCustomerData | PROCEDURE | 3 | watermark_dependent_run_order(+2); fan_out=5(broad_upstream_reads) |
| DW:Integration.MigrateStagedEmployeeData | PROCEDURE | 3 | watermark_dependent_run_order(+2); fan_out=5(broad_upstream_reads) |
| DW:Integration.MigrateStagedOrderData | PROCEDURE | 3 | watermark_dependent_run_order(+2); fan_out=8(broad_upstream_reads) |
| DW:Integration.MigrateStagedPurchaseData | PROCEDURE | 3 | watermark_dependent_run_order(+2); fan_out=7(broad_upstream_reads) |
| DW:Integration.MigrateStagedSaleData | PROCEDURE | 3 | watermark_dependent_run_order(+2); fan_out=9(broad_upstream_reads) |
| DW:Integration.MigrateStagedTransactionData | PROCEDURE | 3 | watermark_dependent_run_order(+2); fan_out=7(broad_upstream_reads) |
| SSIS:DailyETLMain:Get Last Movement ETL Cutoff Time | SSIS_EXECUTE_SQL | 3 | watermark_dependent_run_order(+2); fan_out=12(broad_upstream_reads) |
| SSIS:DailyETLMain:Get Last Movement ETL Cutoff Time | SSIS_EXECUTE_SQL | 3 | watermark_dependent_run_order(+2); fan_out=12(broad_upstream_reads) |
| SSIS:DailyETLMain:Get Last Movement ETL Cutoff Time | SSIS_EXECUTE_SQL | 3 | watermark_dependent_run_order(+2); fan_out=12(broad_upstream_reads) |
| SSIS:DailyETLMain:Get Last Movement ETL Cutoff Time | SSIS_EXECUTE_SQL | 3 | watermark_dependent_run_order(+2); fan_out=12(broad_upstream_reads) |

## 7. Data Type Mapping Risks

`geography`/`geometry`, `hierarchyid`, `sql_variant`, and `xml` have no native Delta Lake/Spark type. The **geography** column appears in 14 objects (City/Country/StateProvince/Supplier/Customer tables and their `_Archive` pairs, plus the DW `Dimension.City` and the `GetCityUpdates` procedure) and is the single largest data-type migration risk in this solution — no automated mapping exists; it must be redesigned as WKT/WKB `STRING` with an optional H3 or geospatial-library index (e.g. Mosaic, Sedona).

| Object | Type | Score | Factors |
|---|---|---|---|
| OLTP:Application.Cities | TABLE | 5 | geography(+5) |
| OLTP:Application.StateProvinces | TABLE | 5 | geography(+5) |
| OLTP:Integration.GetCityUpdates | PROCEDURE | 5 | geography(+5) |
| OLTP:Purchasing.Suppliers | TABLE | 5 | geography(+5) |
| OLTP:Sales.Customers | TABLE | 5 | geography(+5) |
| OLTP:Application.Countries | TABLE | 5 | geography(+5) |
| DW:Dimension.City | TABLE | 5 | geography(+5) |
| OLTP:DataLoadSimulation.RecordDeliveryVanTemperatures | PROCEDURE | 5 | geometry(+5) |
| OLTP:Website.RecordVehicleTemperature | PROCEDURE | 5 | geometry(+5); nvarchar\(max\)(+1) |
| DW:Integration.City_Staging | TABLE | 5 | geography(+5) |
| OLTP:Application.Cities_Archive | TABLE | 5 | geography(+5) |
| OLTP:Application.Countries_Archive | TABLE | 5 | geography(+5) |
| OLTP:Application.StateProvinces_Archive | TABLE | 5 | geography(+5) |
| OLTP:Purchasing.Suppliers_Archive | TABLE | 5 | geography(+5) |
| OLTP:Sales.Customers_Archive | TABLE | 5 | geography(+5) |
| OLTP:WebApi.Customers | VIEW | 5 | geometry(+5) |
| OLTP:WebApi.Suppliers | VIEW | 5 | geometry(+5) |
| OLTP:WebApi.Cities | VIEW | 5 | geometry(+5) |
| OLTP:WebApi.SalesOrders | VIEW | 5 | geometry(+5) |
| OLTP:Application.SystemParameters | TABLE | 5 | geography(+5) |
| OLTP:DataLoadSimulation.GetCityLocation | SCALAR_FUNCTION | 5 | geography(+5) |
| OLTP:WebApi.StateProvinces | VIEW | 5 | geometry(+5) |
| OLTP:Integration.GetStockItemUpdates | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.Configuration_EnableInMemory | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Integration.GetEmployeeUpdates | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:DataLoadSimulation.UpdateCustomFields | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.Configuration_DisableInMemory | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:DataLoadSimulation.AddCustomers | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:DataLoadSimulation.ActivateWebsiteLogons | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:DataLoadSimulation.ChangePasswords | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:DataLoadSimulation.RecordInvoiceDeliveries | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.Configuration_ApplyRowLevelSecurity | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:DataLoadSimulation.InvoicePickedOrders | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:DataLoadSimulation.DeactivateTemporalTablesBeforeDataLoad | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.Configuration_ApplyColumnstoreIndexing | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.Configuration_ApplyFullTextIndexing | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.Configuration_RemoveRowLevelSecurity | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertBuyingGroupsFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertCitiesFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertColorsFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertCountriesFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertCustomerCategoriesFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertCustomersFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertDeliveryMethodsFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertPackageTypesFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertPaymentMethodsFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertStateProvincesFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertStockGroupsFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertStockItemsFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertSupplierCategoriesFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertSuppliersFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.InsertTransactionTypesFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateCustomerFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateCustomerTransactionFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateInvoiceFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdatePurchaseOrderFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateSalesOrderFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateSpecialDealFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateStockItemFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateSupplierFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateSupplierTransactionFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateBuyingGroupFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateCityFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateColorFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateCountryFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateCustomerCategoryFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateDeliveryMethodFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdatePackageTypeFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdatePaymentMethodFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateStateProvinceFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateStockGroupFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateSupplierCategoryFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:WebApi.UpdateTransactionTypeFromJson | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.CreateRoleIfNonexistent | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| DW:Sequences.ReseedSequenceBeyondTableValues | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.Configuration_ApplyAuditing | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.Configuration_RemoveColumnstoreIndexing | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| DW:Application.Configuration_ApplyPolybase | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.AddRoleMemberIfNonexistent | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.Configuration_ApplyPartitioning | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.Logs | TABLE | 1 | nvarchar\(max\)(+1) |
| OLTP:Sequences.ReseedSequenceBeyondTableValues | PROCEDURE | 1 | nvarchar\(max\)(+1) |
| OLTP:Application.Configuration_RemoveAuditing | PROCEDURE | 1 | nvarchar\(max\)(+1) |

## 8. Performance Risks

Risk sources: memory-optimised tables (no Spark equivalent — becomes a standard Delta table, losing in-memory OLTP semantics), columnstore indexes (replaced by Delta's native columnar format + Z-ORDER), partition schemes (replaced by `PARTITIONED BY`), temporal tables queried via `FOR SYSTEM_TIME` (NOT a drop-in Delta Time Travel replacement — Time Travel is a whole-table commit snapshot, while `FOR SYSTEM_TIME AS OF` is a per-row validity-window lookup; the correct rewrite is an explicit `WHERE valid_from <= ts AND (valid_to > ts OR valid_to IS NULL)` filter against the preserved ValidFrom/ValidTo columns), and row-by-row CURSOR processing (must be rewritten as set-based/distributed operations or it will not scale on Spark).

| Object | Type | Score | Factors |
|---|---|---|---|
| OLTP:Warehouse.ColdRoomTemperatures | TABLE | 4 | MEMORY_OPTIMIZED(+4) |
| OLTP:DataLoadSimulation.ColdRoomTemperatures_temp | TABLE | 4 | MEMORY_OPTIMIZED(+4) |
| OLTP:Warehouse.VehicleTemperatures | TABLE | 4 | MEMORY_OPTIMIZED(+4) |
| DW:Fact.Purchase | TABLE | 4 | COLUMNSTORE(+2); PARTITIONED(+2) |
| DW:Fact.Sale | TABLE | 4 | COLUMNSTORE(+2); PARTITIONED(+2) |
| DW:Fact.Order | TABLE | 4 | COLUMNSTORE(+2); PARTITIONED(+2) |
| DW:Fact.Movement | TABLE | 4 | COLUMNSTORE(+2); PARTITIONED(+2) |
| DW:Fact.Transaction | TABLE | 4 | COLUMNSTORE(+2); PARTITIONED(+2) |
| OLTP:Application.Cities | TABLE | 3 | TEMPORAL(+3) |
| OLTP:Application.StateProvinces | TABLE | 3 | TEMPORAL(+3) |
| OLTP:Purchasing.Suppliers | TABLE | 3 | TEMPORAL(+3) |
| OLTP:Sales.Customers | TABLE | 3 | TEMPORAL(+3) |
| OLTP:Application.Countries | TABLE | 3 | TEMPORAL(+3) |
| OLTP:Application.DeliveryMethods | TABLE | 3 | TEMPORAL(+3) |
| OLTP:Application.People | TABLE | 3 | TEMPORAL(+3) |

## 9. Security / Access Model Changes

SQL Server uses schema-level `GRANT`/`DENY`, database roles, and `EXECUTE AS OWNER` impersonation on Integration procedures. Unity Catalog replaces this with catalog/schema/table-level grants and row/column-level security via dynamic views — there is no procedural impersonation model, so any `EXECUTE AS` logic must be redesigned as Unity Catalog access policies.

| Object | Type | Score | Factors |
|---|---|---|---|
| OLTP:Application.Configuration_ApplyRowLevelSecurity | PROCEDURE | 5 | EXECUTE\s+AS\s+OWNER(+2); ROW\s+LEVEL\s+SECURITY(+4) |
| OLTP:Application.Configuration_RemoveRowLevelSecurity | PROCEDURE | 5 | EXECUTE\s+AS\s+OWNER(+2); ROW\s+LEVEL\s+SECURITY(+4) |
| OLTP:DataLoadSimulation.DailyProcessToCreateHistory | PROCEDURE | 4 | ROW\s+LEVEL\s+SECURITY(+4) |
| OLTP:Application.CreateRoleIfNonexistent | PROCEDURE | 4 | EXECUTE\s+AS\s+OWNER(+2); CREATE\s+ROLE(+2) |
| OLTP:Integration.GetCityUpdates | PROCEDURE | 2 | EXECUTE\s+AS\s+OWNER(+2) |
| OLTP:Integration.GetStockItemUpdates | PROCEDURE | 2 | EXECUTE\s+AS\s+OWNER(+2) |
| OLTP:Application.Configuration_EnableInMemory | PROCEDURE | 2 | EXECUTE\s+AS\s+OWNER(+2) |
| OLTP:Integration.GetEmployeeUpdates | PROCEDURE | 2 | EXECUTE\s+AS\s+OWNER(+2) |
| OLTP:DataLoadSimulation.UpdateCustomFields | PROCEDURE | 2 | EXECUTE\s+AS\s+OWNER(+2) |
| OLTP:Integration.GetCustomerUpdates | PROCEDURE | 2 | EXECUTE\s+AS\s+OWNER(+2) |

## 10. Operational Scheduling Changes

Today, `DailyETLMain.dtsx` is invoked by a SQL Server Agent job on a fixed daily schedule, with package-level success/failure handling. On Databricks this becomes a multi-task Workflow with the same task graph; the watermark state (`Integration.ETL Cutoff`) must move from an in-database table read at task start to a Delta table or Workflow task-value pattern. Failure/retry semantics, alerting, and SLA monitoring must be re-implemented using Databricks Workflows' native retry/alert configuration rather than SSIS's package-level error handling.


## 11. Testing Complexity

Recommended test depth scales with classification (see `manual_intervention_list.md` and the register's `recommended_test_depth` column):

| Classification | Recommended Test Depth |
|---|---|
| Lift-and-shift friendly | Schema/row-count parity check + column-level checksum sample (Tier 1) |
| Partial automation possible | Row-level reconciliation (statistically sampled) + business-rule unit tests for the automated portion + manual review of generated code (Tier 2) |
| Rewrite required | Full regression suite: unit tests per logic branch/condition, golden-record reconciliation against source, edge-case/boundary tests, side-by-side parallel run (Tier 3) |
| Manual redesign required | Full parallel-run validation across at least one complete ETL cycle, manual functional sign-off, extended UAT, rollback rehearsal (Tier 4) |

## 12. Rollback Complexity

Stateful objects (SCD2 dimensions, lineage tracking, temporal `_Archive` pairs) are the hardest to roll back — a failed cutover after a Dimension/Fact load has run requires restoring history state, not just re-pointing a query. Stateless staging/full-load objects roll back cleanly (truncate + rerun).

| Object | Type | Score | Factors |
|---|---|---|---|
| OLTP:Application.Cities | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |
| OLTP:Application.StateProvinces | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |
| OLTP:Purchasing.Suppliers | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |
| OLTP:Sales.Customers | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |
| OLTP:Application.Countries | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |
| OLTP:Application.DeliveryMethods | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |
| OLTP:Application.People | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |
| OLTP:Application.TransactionTypes | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |
| OLTP:Sales.BuyingGroups | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |
| OLTP:Sales.CustomerCategories | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |
| OLTP:Warehouse.PackageTypes | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |
| OLTP:Warehouse.StockItems | TABLE | 5 | scd2_history_state(+3); temporal_history_table(+2) |

---

## Top 20 Highest-Impact Objects (overall score)

| Object | Type | Classification | Overall Score |
|---|---|---|---|
| OLTP:Application.Cities | TABLE | Manual redesign required | 2.0 |
| OLTP:Application.StateProvinces | TABLE | Manual redesign required | 2.0 |
| OLTP:Integration.GetCityUpdates | PROCEDURE | Manual redesign required | 2.0 |
| OLTP:Purchasing.Suppliers | TABLE | Manual redesign required | 2.0 |
| OLTP:Sales.Customers | TABLE | Manual redesign required | 2.0 |
| OLTP:Application.Countries | TABLE | Manual redesign required | 1.92 |
| OLTP:Integration.GetStockItemUpdates | PROCEDURE | Manual redesign required | 1.67 |
| OLTP:Application.Configuration_EnableInMemory | PROCEDURE | Manual redesign required | 1.58 |
| OLTP:Application.DeliveryMethods | TABLE | Manual redesign required | 1.58 |
| OLTP:Application.People | TABLE | Manual redesign required | 1.58 |
| OLTP:Application.TransactionTypes | TABLE | Manual redesign required | 1.58 |
| OLTP:Integration.GetEmployeeUpdates | PROCEDURE | Manual redesign required | 1.58 |
| OLTP:Sales.BuyingGroups | TABLE | Manual redesign required | 1.58 |
| OLTP:Sales.CustomerCategories | TABLE | Manual redesign required | 1.58 |
| OLTP:Warehouse.PackageTypes | TABLE | Manual redesign required | 1.58 |
| OLTP:Warehouse.StockItems | TABLE | Manual redesign required | 1.58 |
| OLTP:Application.PaymentMethods | TABLE | Manual redesign required | 1.5 |
| OLTP:DataLoadSimulation.UpdateCustomFields | PROCEDURE | Manual redesign required | 1.5 |
| OLTP:Integration.GetCustomerUpdates | PROCEDURE | Manual redesign required | 1.5 |
| OLTP:Integration.GetSupplierUpdates | PROCEDURE | Manual redesign required | 1.5 |

## Confidence

| Section | Confidence | Basis |
|---|---|---|
| SQL dialect / procedural logic scoring | HIGH | Direct regex pattern match against raw DDL text |
| SSIS control/data flow scoring | MEDIUM | Derived from parsed XML structure; component-level data-flow detail is partially flattened |
| Dependency criticality / blast radius | HIGH | Computed from the validated 402-node/566-edge dependency graph (0 cycles) |
| Data type risk | HIGH | Exhaustive substring scan confirmed against raw DDL |
| Security risk | MEDIUM | Heuristic pattern match; full impersonation chain not modelled |
| Operational scheduling | LOW | Narrative inference — no live SQL Agent job definition was available in the source corpus |

_Generated by the WWI Modernisation Accelerator's impact-analysis module. Does not yet propose target-state design or generate code — see Step 5 (target-state design) and Step 6 (conversion)._