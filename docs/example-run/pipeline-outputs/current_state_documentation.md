# Wide World Importers — Current State Documentation

> **Accelerator:** WWI SQL Server → Databricks Modernisation Accelerator v0.1.0  
> **Generated:** 2026-06-30 04:57 UTC  
> **Source corpus:** `microsoft/sql-server-samples` — WideWorldImporters  
> **Analysis basis:** Static code analysis (no live database connection required)

---

## Executive Summary

> **Confidence:** 🟢 HIGH

Wide World Importers (WWI) is a fictional wholesale novelty goods company whose SQL Server estate represents a well-structured, real-world OLTP + data warehouse pattern. The system consists of two SQL Server databases and one SSIS package that performs a daily incremental ETL.

### At a Glance

| Dimension | Value |
|---|---|
| Total source objects analysed | 431 |
| OLTP database (WideWorldImporters) | 268 |
| DW database (WideWorldImportersDW) | 68 |
| SSIS artefacts | 95 |
| Tables (OLTP, live) | 37 |
| Dimension tables (DW) | 8 |
| Fact tables (DW) | 6 |
| Staging tables (DW Integration schema) | 13 |
| Stored procedures | 157 |
| Views | 28 |
| Dependency edges | 584 |
| Dependency cycles | 0 |
| Average conversion confidence | 72.4% |
| Objects requiring manual remediation | 7 |
| Unsupported / skipped objects | 18 |

### Migration Readiness

The WWI estate is a **well-suited** candidate for automated migration to Databricks:

- The DW schema structure (`Integration` → `Dimension` → `Fact`) **maps directly** to the Databricks medallion architecture (Bronze → Silver → Gold).
- The ETL pattern is consistent: 13 identical Sequence Containers in one SSIS package, each following the same 5-step extract→stage→migrate loop.
- Complexity is concentrated in **8 OLTP Integration procedures** that use T-SQL CURSOR loops over temporal table history — these require rewrite to PySpark temporal joins.
- No dynamic SQL, linked servers, CLR objects, or OPENROWSET references were detected.
- The `geography` spatial data type in `Dimension.City` / `Application.Cities` is the single **CRITICAL** data type gap — requires manual conversion to WKT string.

---

## 1. Source Platform Overview

> **Confidence:** 🟢 HIGH

### Databases

| Database | Version / Edition | Role | SSDT Project |
|---|---|---|---|
| WideWorldImporters | SQL Server 2016+ (v13.0.4001.0 per SSIS metadata) | OLTP transactional system | `wwi-ssdt` |
| WideWorldImportersDW | SQL Server 2016+ | Star-schema analytical data warehouse | `wwi-dw-ssdt` |

### Connectivity

Both databases reside on the same SQL Server instance (Data Source = `.` / localhost). The SSIS package connects via **OLE DB / SQLNCLI11** using Windows Integrated Security.

| Connection Manager | Type | Target Database | Auth |
|---|---|---|---|
| `WWI_Source_DB` | OLEDB / SQLNCLI11 | WideWorldImporters | SSPI / Windows |
| `WWI_DW_Destination_DB` | OLEDB / SQLNCLI11 | WideWorldImportersDW | SSPI / Windows |

### Scheduling

No SQL Agent job metadata was present in the SSDT projects. The SSIS package `DailyETLMain.dtsx` is named for daily execution and contains a cutoff-time window pattern (`LastETLCutoffTime` → `TargetETLCutoffTime`) consistent with a nightly incremental load schedule.

### Source-Control Artefacts

| Artefact | Type | Files |
|---|---|---|
| `wwi-ssdt` | SQL Server Data Tools (.sqlproj) | 336 `.sql` files |
| `wwi-dw-ssdt` | SQL Server Data Tools (.sqlproj) | 73 `.sql` files |
| `wwi-ssis` | SSIS project (.dtproj + .dtsx) | 1 package, 2 connection managers |

## 2. Schema Inventory

> **Confidence:** 🟢 HIGH

### WideWorldImporters (OLTP) — Schema Catalogue

| Schema | Object Count | Purpose |
|---|---|---|
| Application | 31 | Reference / master data — Countries, Cities, StateProvinces, People, DeliveryMethods, PaymentMethods, TransactionTypes, SystemParameters. All reference tables are **system-versioned temporal tables**. |
| Sales | 12 | Core transactional domain — Customers, Orders, OrderLines, Invoices, InvoiceLines, CustomerTransactions, BuyingGroups, SpecialDeals. Customers is temporal; InvoiceLines and OrderLines use columnstore indexes. |
| Purchasing | 7 | Supplier procurement — Suppliers, SupplierCategories, PurchaseOrders, PurchaseOrderLines, SupplierTransactions. Suppliers is temporal. |
| Warehouse | 14 | Inventory management — StockItems, StockItemHoldings, StockItemTransactions, StockItemStockGroups, Colors, PackageTypes, StockGroups. StockItems temporal. ColdRoomTemperatures and VehicleTemperatures are **memory-optimised** IoT sensor tables. |
| Integration | 13 | ETL extraction layer — 13 stored procedures (`Get<Entity>Updates`) that use temporal table AS-OF queries and CURSOR loops to extract changed rows within a cutoff time window. |
| Website | 19 | Application API — 11 stored procedures (order placement, invoicing, password management, IoT sensor recording) and 3 views for the web app. |
| WebApi | 76 | REST API surface — 24 views + 53 CRUD stored procedures providing a thin read/write layer over the OLTP tables. |
| DataLoadSimulation | 56 | Test data generation — 43 stored procedures and 4 helper tables used to simulate realistic transactional workloads. **Not in scope for migration to DW.** |
| Sequences | 28 | 26 SEQUENCE objects providing identity generation for all entity PKs. |
| dbo | 12 | Version metadata table (`SampleVersion`). |

### WideWorldImportersDW (Data Warehouse) — Schema Catalogue

| Schema | Object Count | Medallion Layer | Purpose |
|---|---|---|---|
| Integration | 32 | Bronze | ETL staging layer — 13 `<Entity>_Staging` tables, 2 ETL control tables (`ETL Cutoff`, `Lineage`), and 16 stored procedures (GetLastETLCutoffTime, GetLineageKey, MigrateStaged*, PopulateDateDimensionForYear). Maps to **Bronze** in target architecture. |
| Dimension | 8 | Silver | 8 conformed dimensions (City, Customer, Date, Employee, Payment Method, Stock Item, Supplier, Transaction Type). All SCD Type 2 with `Valid From` / `Valid To` / `Lineage Key`. Maps to **Silver** in target architecture. |
| Fact | 6 | Gold | 6 fact tables (Sale, Order, Purchase, Movement, Transaction, Stock Holding). All use columnstore indexes and date-range partition schemes (`PS_Date`). Maps to **Gold** in target architecture. |
| Sequences | 10 | — | 8 SEQUENCE objects for dimension surrogate key generation. |
| Application | 3 | — | 3 configuration procedures (Polybase setup, large sale table, ETL reseed). |
| dbo | 9 | — | Version metadata table. |

## 3. ETL / Orchestration Overview

> **Confidence:** 🟢 HIGH

### Package: DailyETLMain

A single SSIS package orchestrates the entire daily load from WideWorldImporters (OLTP) into WideWorldImportersDW. The package is **flat** — no sub-packages, no Execute Package Tasks, no conditional branching beyond precedence constraints.

| Metric | Value |
|---|---|
| SSIS version | 13.0.4001.0 (SQL Server 2016 Integration Services) |
| Protection level | 0 (DontSaveSensitive) |
| Total tasks | 94 |
| Sequence Containers | 13 |
| Data Flow Tasks | 13 |
| Execute SQL Tasks | 53 |
| Expression Tasks | 15 |
| Data movement paths | 26 |

### Package-Level Variables

| Variable | Type | Purpose |
|---|---|---|
| `LastETLCutoffTime` | DateTime | Watermark: last successful ETL run end time (read from `Integration.ETL Cutoff`) |
| `TargetETLCutoffTime` | DateTime | Current run cutoff = `GETUTCDATE() - 5 minutes` (expression task) |
| `LineageKey` | Int32 | Current run lineage record key (from `Integration.GetLineageKey`) |
| `TableName` | String | Entity name passed to `GetLineageKey` (set by expression task per container) |

### The 5-Step Pattern (repeated for all 13 entities)

Every entity follows an identical Sequence Container structure:

```
┌─ Sequence Container: Load <Entity> [Dimension|Fact]
│  1. Get Last <Entity> ETL Cutoff Time   → Execute SQL → Integration.GetLastETLCutoffTime
│  2. Set TableName to <Entity>            → Expression  → @TableName = '<Entity>'
│  3. Truncate <Entity>_Staging            → Execute SQL → DELETE FROM Integration.<Entity>_Staging
│  4. Extract Updated <Entity> Data        → Data Flow   → OLTP.Integration.Get<Entity>Updates
│                                                           → DW.Integration.<Entity>_Staging
│  5. Get Lineage Key                      → Execute SQL → Integration.GetLineageKey
│  6. Migrate Staged <Entity> Data         → Execute SQL → Integration.MigrateStaged<Entity>Data
└──────────────────────────────────────────────────────────────────────────────────
```

### Sequence Container Load Order (Dimensions before Facts)

| # | Container | Type | Upstream Deps |
|---|---|---|---|
| 1 | Load City Dimension | Dimension | — |
| 2 | Load Customer Dimension | Dimension | — |
| 3 | Load Employee Dimension | Dimension | — |
| 4 | Load Payment Method Dimension | Dimension | — |
| 5 | Load Stock Item Dimension | Dimension | — |
| 6 | Load Supplier Dimension | Dimension | — |
| 7 | Load Transaction Type Dimension | Dimension | — |
| 8 | Load Movement Fact | Fact | Dimensions must complete first |
| 9 | Load Order Fact | Fact | Dimensions must complete first |
| 10 | Load Purchase Fact | Fact | Dimensions must complete first |
| 11 | Load Sale Fact | Fact | Dimensions must complete first |
| 12 | Load Stock Holding Fact | Fact | Dimensions must complete first |
| 13 | Load Transaction Fact | Fact | Dimensions must complete first |

### ETL Cutoff Window Logic

The package implements a **sliding time-window incremental** pattern:

1. `TargetETLCutoffTime` = `GETUTCDATE() - 5 minutes` (expression task at package start)
2. Per entity: `LastETLCutoffTime` read from `Integration.ETL Cutoff` table
3. OLTP `Get<Entity>Updates` proc extracts rows where `ValidFrom > @LastCutoff AND ValidFrom <= @NewCutoff`
4. After successful `MigrateStaged*` proc: `Integration.ETL Cutoff.[Cutoff Time]` updated to `TargetETLCutoffTime`
5. `Integration.Lineage` records start time, end time, success flag, and cutoff per run

**The 5-minute buffer** prevents race conditions between the OLTP transaction commit and the ETL read window.

## 4. Object Taxonomy

### 4a. Tables

> **Confidence:** 🟢 HIGH

#### OLTP Core Domain Tables

**Application schema** (9 tables)

| Table | Columns | Special Features |
|---|---|---|
| `Application.Cities` | 7 | `TEMPORAL` |
| `Application.Countries` | 13 | `TEMPORAL` |
| `Application.DeliveryMethods` | 5 | `TEMPORAL` |
| `Application.Logs` | 5 | `COLUMNSTORE` |
| `Application.PaymentMethods` | 5 | `TEMPORAL` |
| `Application.People` | 19 | `TEMPORAL` |
| `Application.StateProvinces` | 9 | `TEMPORAL` |
| `Application.SystemParameters` | 12 | — |
| `Application.TransactionTypes` | 5 | `TEMPORAL` |

**Sales schema** (9 tables)

| Table | Columns | Special Features |
|---|---|---|
| `Sales.BuyingGroups` | 5 | `TEMPORAL` |
| `Sales.CustomerCategories` | 5 | `TEMPORAL` |
| `Sales.CustomerTransactions` | 13 | `PARTITIONED` |
| `Sales.Customers` | 30 | `TEMPORAL` |
| `Sales.InvoiceLines` | 13 | `COLUMNSTORE` |
| `Sales.Invoices` | 23 | — |
| `Sales.OrderLines` | 12 | `COLUMNSTORE` |
| `Sales.Orders` | 16 | — |
| `Sales.SpecialDeals` | 14 | — |

**Purchasing schema** (5 tables)

| Table | Columns | Special Features |
|---|---|---|
| `Purchasing.PurchaseOrderLines` | 12 | — |
| `Purchasing.PurchaseOrders` | 12 | — |
| `Purchasing.SupplierCategories` | 5 | `TEMPORAL` |
| `Purchasing.SupplierTransactions` | 14 | `PARTITIONED` |
| `Purchasing.Suppliers` | 23 | `TEMPORAL` |

**Warehouse schema** (9 tables)

| Table | Columns | Special Features |
|---|---|---|
| `Warehouse.ColdRoomTemperatures` | 6 | `MEMORY_OPTIMIZED` |
| `Warehouse.Colors` | 5 | `TEMPORAL` |
| `Warehouse.PackageTypes` | 5 | `TEMPORAL` |
| `Warehouse.StockGroups` | 5 | `TEMPORAL` |
| `Warehouse.StockItemHoldings` | 9 | — |
| `Warehouse.StockItemStockGroups` | 5 | — |
| `Warehouse.StockItemTransactions` | 11 | `COLUMNSTORE` |
| `Warehouse.StockItems` | 23 | `TEMPORAL` |
| `Warehouse.VehicleTemperatures` | 8 | `MEMORY_OPTIMIZED` |

**Temporal History Tables** (17 tables)

Every temporal table has a paired `<Name>_Archive` table managed by SQL Server's system-versioning. These are **read-only** from an ETL perspective — `Get<Entity>Updates` procs query them using `FOR SYSTEM_TIME` to capture changes.

#### OLTP Specialised Tables

| Table | Feature | Notes |
|---|---|---|
| `DataLoadSimulation.ColdRoomTemperatures_temp` | MEMORY_OPTIMIZED | Temp buffer for sensor data simulation |
| `Warehouse.ColdRoomTemperatures` | MEMORY_OPTIMIZED | IoT cold-room sensor readings (in-memory, no disk) |
| `Warehouse.VehicleTemperatures` | MEMORY_OPTIMIZED | IoT vehicle temperature telemetry |
| `Application.Logs` | COLUMNSTORE | Application audit log with columnstore for analytics |
| `Sales.InvoiceLines` | COLUMNSTORE | High-volume invoice detail with columnstore |
| `Sales.OrderLines` | COLUMNSTORE | High-volume order detail with columnstore |
| `Warehouse.StockItemTransactions` | COLUMNSTORE | High-volume stock movement log with columnstore |
| `Purchasing.SupplierTransactions` | PARTITIONED | Supplier financial transactions, date-partitioned |
| `Sales.CustomerTransactions` | PARTITIONED | Customer financial transactions, date-partitioned |

#### DW Dimension Tables (Silver layer target)

| Table | Columns | SCD Pattern |
|---|---|---|
| `Dimension.City` | 13 | SCD2 (`Valid From`/`Valid To`) |
| `Dimension.Customer` | 11 | SCD2 (`Valid From`/`Valid To`) |
| `Dimension.Date` | 1 | — |
| `Dimension.Employee` | 9 | SCD2 (`Valid From`/`Valid To`) |
| `Dimension.Payment` | 6 | SCD2 (`Valid From`/`Valid To`) |
| `Dimension.Stock` | 20 | SCD2 (`Valid From`/`Valid To`) |
| `Dimension.Supplier` | 11 | SCD2 (`Valid From`/`Valid To`) |
| `Dimension.Transaction` | 6 | SCD2 (`Valid From`/`Valid To`) |

#### DW Fact Tables (Gold layer target)

| Table | Columns | Storage Features |
|---|---|---|
| `Fact.Movement` | 11 | COLUMNSTORE + PARTITIONED |
| `Fact.Order` | 19 | COLUMNSTORE + PARTITIONED |
| `Fact.Purchase` | 11 | COLUMNSTORE + PARTITIONED |
| `Fact.Sale` | 21 | COLUMNSTORE + PARTITIONED |
| `Fact.Stock` | 9 | COLUMNSTORE |
| `Fact.Transaction` | 18 | COLUMNSTORE + PARTITIONED |

#### DW Staging Tables (Bronze layer target)

| Table | Columns | Load Pattern |
|---|---|---|
| `Integration.City_Staging` | 12 | Truncate-and-reload each run |
| `Integration.Customer_Staging` | 10 | Truncate-and-reload each run |
| `Integration.Employee_Staging` | 8 | Truncate-and-reload each run |
| `Integration.Movement_Staging` | 15 | Truncate-and-reload each run |
| `Integration.Order_Staging` | 25 | Truncate-and-reload each run |
| `Integration.PaymentMethod_Staging` | 5 | Truncate-and-reload each run |
| `Integration.Purchase_Staging` | 13 | Truncate-and-reload each run |
| `Integration.Sale_Staging` | 26 | Truncate-and-reload each run |
| `Integration.StockHolding_Staging` | 9 | Truncate-and-reload each run |
| `Integration.StockItem_Staging` | 19 | Truncate-and-reload each run |
| `Integration.Supplier_Staging` | 10 | Truncate-and-reload each run |
| `Integration.TransactionType_Staging` | 5 | Truncate-and-reload each run |
| `Integration.Transaction_Staging` | 23 | Truncate-and-reload each run |

### 4b. Views

> **Confidence:** 🟢 HIGH

No materialised / indexed views were detected in either project. All views are standard SQL Server views.

#### WebApi Schema Views (OLTP)

24 views provide a clean REST API surface over the OLTP tables. Named to mirror the entity: `WebApi.Customers`, `WebApi.Invoices`, etc.

| View | Likely Purpose |
|---|---|
| `WebApi.BuyingGroups` | Read surface for buyinggroups entity |
| `WebApi.Cities` | Read surface for cities entity |
| `WebApi.Colors` | Read surface for colors entity |
| `WebApi.Countries` | Read surface for countries entity |
| `WebApi.CustomerCategories` | Read surface for customercategories entity |
| `WebApi.CustomerTransactions` | Read surface for customertransactions entity |
| `WebApi.Customers` | Read surface for customers entity |
| `WebApi.DeliveryMethods` | Read surface for deliverymethods entity |
| `WebApi.Invoices` | Read surface for invoices entity |
| `WebApi.PackageTypes` | Read surface for packagetypes entity |
| `WebApi.PaymentMethods` | Read surface for paymentmethods entity |
| `WebApi.PurchaseOrderLines` | Read surface for purchaseorderlines entity |
| `WebApi.PurchaseOrders` | Read surface for purchaseorders entity |
| `WebApi.SalesOrderLines` | Read surface for salesorderlines entity |
| `WebApi.SalesOrders` | Read surface for salesorders entity |
| `WebApi.SpecialDeals` | Read surface for specialdeals entity |
| `WebApi.StateProvinces` | Read surface for stateprovinces entity |
| `WebApi.StockGroups` | Read surface for stockgroups entity |
| `WebApi.StockItems` | Read surface for stockitems entity |
| `WebApi.SupplierCategories` | Read surface for suppliercategories entity |
| `WebApi.SupplierTransactions` | Read surface for suppliertransactions entity |
| `WebApi.Suppliers` | Read surface for suppliers entity |
| `WebApi.TransactionTypes` | Read surface for transactiontypes entity |

#### Website Schema Views (OLTP)

3 views used by the internal web application:

- `Website.Customers` — customer with delivery and buying-group context
- `Website.Suppliers` — supplier contact and banking detail view
- `Website.VehicleTemperatures` — IoT telemetry view for refrigerated vehicles

#### Table-Valued Functions (inline TVFs)

| Function | Project | Type |
|---|---|---|
| `Application.DetermineCustomerAccess` | OLTP | TVF_INLINE |
| `Integration.GenerateDateDimensionColumns` | DW | TVF_INLINE |

### 4c. Stored Procedures

> **Confidence:** 🟢 HIGH

#### Integration (OLTP) — ETL extraction (13 procedures)

13 procs that extract changed rows from temporal tables into staging. 7 use CURSOR loops (SCD2 entities); 6 are simple parameterised SELECTs (fact entities).

| Procedure | Complexity | Risk | ETL Semantics |
|---|---|---|---|
| `Integration.GetCityUpdates` | HIGH | HIGH | INCREMENTAL, SCD2 |
| `Integration.GetCustomerUpdates` | HIGH | HIGH | INCREMENTAL, SCD2 |
| `Integration.GetEmployeeUpdates` | HIGH | HIGH | INCREMENTAL, SCD2 |
| `Integration.GetMovementUpdates` | LOW | NONE | INCREMENTAL |
| `Integration.GetOrderUpdates` | LOW | NONE | INCREMENTAL |
| `Integration.GetPaymentMethodUpdates` | HIGH | HIGH | INCREMENTAL, SCD2 |
| `Integration.GetPurchaseUpdates` | LOW | NONE | INCREMENTAL |
| `Integration.GetSaleUpdates` | LOW | NONE | INCREMENTAL |
| `Integration.GetStockHoldingUpdates` | LOW | NONE | — |
| `Integration.GetStockItemUpdates` | HIGH | HIGH | INCREMENTAL, SCD2 |
| `Integration.GetSupplierUpdates` | HIGH | HIGH | INCREMENTAL, SCD2 |
| `Integration.GetTransactionTypeUpdates` | HIGH | HIGH | INCREMENTAL, SCD2 |
| `Integration.GetTransactionUpdates` | LOW | NONE | INCREMENTAL |

#### Integration (DW) — ETL loading (16 procedures)

16 procs: `GetLastETLCutoffTime`, `GetLineageKey`, 13 `MigrateStaged*` procs, and `PopulateDateDimensionForYear`. The Migrate procs implement SCD2 via UPDATE (close off old rows) + INSERT (new version) pattern.

| Procedure | Complexity | Risk | ETL Semantics |
|---|---|---|---|
| `Integration.GetLastETLCutoffTime` | LOW | NONE | CUTOFF_WINDOW |
| `Integration.GetLineageKey` | LOW | NONE | — |
| `Integration.MigrateStagedCityData` | LOW | NONE | SCD2, CUTOFF_WINDOW |
| `Integration.MigrateStagedCustomerData` | LOW | NONE | SCD2, CUTOFF_WINDOW |
| `Integration.MigrateStagedEmployeeData` | LOW | NONE | SCD2, CUTOFF_WINDOW |
| `Integration.MigrateStagedMovementData` | LOW | NONE | SCD2, MERGE_PATTERN, CUTOFF_WINDOW |
| `Integration.MigrateStagedOrderData` | LOW | NONE | SCD2, CUTOFF_WINDOW |
| `Integration.MigrateStagedPaymentMethodData` | LOW | NONE | SCD2, CUTOFF_WINDOW |
| `Integration.MigrateStagedPurchaseData` | LOW | NONE | SCD2, CUTOFF_WINDOW |
| `Integration.MigrateStagedSaleData` | LOW | NONE | SCD2, CUTOFF_WINDOW |
| `Integration.MigrateStagedStockHoldingData` | LOW | NONE | SCD2, FULL_LOAD, CUTOFF_WINDOW |
| `Integration.MigrateStagedStockItemData` | LOW | NONE | SCD2, CUTOFF_WINDOW |
| `Integration.MigrateStagedSupplierData` | LOW | NONE | SCD2, CUTOFF_WINDOW |
| `Integration.MigrateStagedTransactionData` | LOW | NONE | SCD2, CUTOFF_WINDOW |
| `Integration.MigrateStagedTransactionTypeData` | LOW | NONE | SCD2, CUTOFF_WINDOW |
| `Integration.PopulateDateDimensionForYear` | LOW | NONE | — |

#### WebApi — CRUD layer (53 procedures)

53 CRUD procs providing Insert/Update/Delete for the REST API. Named `<Verb><Entity>` (e.g. `InsertCustomer`, `UpdateStockItem`). **Not in scope for DW migration — serve the application tier only.**

| Procedure | Complexity | Risk | ETL Semantics |
|---|---|---|---|
| `WebApi.DeleteBuyingGroup` | LOW | NONE | — |
| `WebApi.DeleteCity` | LOW | NONE | — |
| `WebApi.DeleteColor` | LOW | NONE | — |
| `WebApi.DeleteCountry` | LOW | NONE | — |
| `WebApi.DeleteCustomer` | LOW | NONE | — |
| `WebApi.DeleteCustomerCategory` | LOW | NONE | — |
| `WebApi.DeleteDeliveryMethod` | LOW | NONE | — |
| `WebApi.DeletePackageType` | LOW | NONE | — |
| `WebApi.DeletePaymentMethod` | LOW | NONE | — |
| `WebApi.DeleteStateProvince` | LOW | NONE | — |
| `WebApi.DeleteStockGroup` | LOW | NONE | — |
| `WebApi.DeleteStockItem` | LOW | NONE | — |
| `WebApi.DeleteSupplier` | LOW | NONE | — |
| `WebApi.DeleteSupplierCategory` | LOW | NONE | — |
| `WebApi.DeleteTransactionType` | LOW | NONE | — |
| `WebApi.InsertBuyingGroupsFromJson` | LOW | LOW | — |
| `WebApi.InsertCitiesFromJson` | LOW | LOW | — |
| `WebApi.InsertColorsFromJson` | LOW | LOW | — |
| `WebApi.InsertCountriesFromJson` | LOW | LOW | — |
| `WebApi.InsertCustomerCategoriesFromJson` | LOW | LOW | — |
*... and 33 more*

#### Website — Application operations (11 procedures)

11 procs for order placement (`InsertCustomerOrders`), invoicing (`InvoiceCustomerOrders`), IoT recording (`RecordColdRoomTemperatures`), and user management. **Application-tier only.**

| Procedure | Complexity | Risk | ETL Semantics |
|---|---|---|---|
| `Website.ActivateWebsiteLogon` | LOW | NONE | — |
| `Website.ChangePassword` | LOW | NONE | — |
| `Website.InsertCustomerOrders` | LOW | NONE | INCREMENTAL |
| `Website.InvoiceCustomerOrders` | LOW | NONE | INCREMENTAL |
| `Website.RecordColdRoomTemperatures` | LOW | NONE | — |
| `Website.RecordVehicleTemperature` | LOW | LOW | — |
| `Website.SearchForCustomers` | LOW | LOW | — |
| `Website.SearchForPeople` | LOW | LOW | — |
| `Website.SearchForStockItems` | LOW | LOW | — |
| `Website.SearchForStockItemsByTags` | LOW | LOW | — |
| `Website.SearchForSuppliers` | LOW | LOW | — |

#### DataLoadSimulation — Test harness (43 procedures)

43 procs simulating realistic workloads. Several use CURSORs (score 6–9) and MERGE. **Excluded from migration scope.**

| Procedure | Complexity | Risk | ETL Semantics |
|---|---|---|---|
| `DataLoadSimulation.ActivateWebsiteLogons` | LOW | NONE | INCREMENTAL, SCD2 |
| `DataLoadSimulation.AddCustomers` | LOW | NONE | INCREMENTAL, SCD2 |
| `DataLoadSimulation.AddSpecialDeals` | LOW | NONE | INCREMENTAL |
| `DataLoadSimulation.AddStockItems` | LOW | NONE | INCREMENTAL, SCD2 |
| `DataLoadSimulation.ChangePasswords` | LOW | NONE | INCREMENTAL, SCD2 |
| `DataLoadSimulation.CreateCustomerOrders` | LOW | NONE | INCREMENTAL |
| `DataLoadSimulation.DailyProcessToCreateHistory` | LOW | NONE | — |
| `DataLoadSimulation.DeactivateTemporalTablesBeforeDataLoad` | LOW | LOW | INCREMENTAL, SCD2 |
| `DataLoadSimulation.GetBogativePhoneNumber` | LOW | NONE | — |
| `DataLoadSimulation.GetBogativePostalCode` | LOW | NONE | INCREMENTAL, SCD2 |
| `DataLoadSimulation.GetBuyingGroupDomain` | LOW | NONE | — |
| `DataLoadSimulation.GetFicticiousName` | LOW | NONE | — |
| `DataLoadSimulation.GetRandomBuyingGroup` | LOW | NONE | INCREMENTAL, SCD2 |
| `DataLoadSimulation.GetRandomBuyingGroupNotInUse` | LOW | NONE | — |
| `DataLoadSimulation.GetRandomCity` | LOW | NONE | — |
| `DataLoadSimulation.GetRandomCustomer` | LOW | NONE | INCREMENTAL, SCD2 |
| `DataLoadSimulation.GetRandomCustomerCategory` | LOW | NONE | — |
| `DataLoadSimulation.GetRandomDeliveryMethod` | LOW | NONE | INCREMENTAL, SCD2 |
| `DataLoadSimulation.GetRandomEmployeePerson` | LOW | NONE | INCREMENTAL, SCD2 |
| `DataLoadSimulation.GetRandomPaymentDays` | LOW | NONE | — |
*... and 23 more*

#### Application — Configuration (14 procedures)

14 procs for auditing, columnstore/fulltext/partitioning setup, role management, and SQL Agent job configuration.

| Procedure | Complexity | Risk | ETL Semantics |
|---|---|---|---|
| `Application.AddRoleMemberIfNonexistent` | LOW | NONE | — |
| `Application.Configuration_ApplyAuditing` | LOW | NONE | — |
| `Application.Configuration_ApplyColumnstoreIndexing` | LOW | NONE | INCREMENTAL |
| `Application.Configuration_ApplyFullTextIndexing` | LOW | LOW | — |
| `Application.Configuration_ApplyPartitioning` | LOW | NONE | — |
| `Application.Configuration_ApplyRowLevelSecurity` | LOW | NONE | — |
| `Application.Configuration_ConfigureForEnterpriseEdition` | LOW | NONE | — |
| `Application.Configuration_DisableInMemory` | LOW | NONE | INCREMENTAL |
| `Application.Configuration_EnableInMemory` | LOW | LOW | INCREMENTAL, SCD2 |
| `Application.Configuration_PrepareForAzureStandard` | LOW | NONE | — |
| `Application.Configuration_RemoveAuditing` | LOW | NONE | — |
| `Application.Configuration_RemoveColumnstoreIndexing` | LOW | NONE | INCREMENTAL |
| `Application.Configuration_RemoveRowLevelSecurity` | LOW | NONE | — |
| `Application.CreateRoleIfNonexistent` | LOW | NONE | — |

#### Sequences — Maintenance (2 procedures)

2 procs to reseed all SEQUENCE objects. Replaced by `GENERATED ALWAYS AS IDENTITY` or Delta `AUTOINCREMENT` in the target.

| Procedure | Complexity | Risk | ETL Semantics |
|---|---|---|---|
| `Sequences.ReseedAllSequences` | LOW | NONE | — |
| `Sequences.ReseedSequenceBeyondTableValues` | LOW | NONE | — |

### 4d. Functions

> **Confidence:** 🟡 MEDIUM

Only 1 explicit scalar function and 2 inline TVFs were detected by the parser. The DataLoadSimulation schema contains ~15 helper functions that were classified as `SCALAR_FUNCTION` by DDL inspection but may include additional TVFs — the column extractor parses only the first DDL keyword.

| Function | Type | Project | Notes |
|---|---|---|---|
| `Application.DetermineCustomerAccess` | TVF_INLINE | OLTP | — |
| `DataLoadSimulation.GetAreaCode` | SCALAR_FUNCTION | OLTP | — |
| `DataLoadSimulation.GetCityLocation` | SCALAR_FUNCTION | OLTP | — |
| `DataLoadSimulation.GetCustomerCount` | SCALAR_FUNCTION | OLTP | — |
| `DataLoadSimulation.GetDeliveryMethodID` | SCALAR_FUNCTION | OLTP | INCREMENTAL, SCD2 |
| `DataLoadSimulation.GetPaymentMethodID` | SCALAR_FUNCTION | OLTP | INCREMENTAL, SCD2 |
| `DataLoadSimulation.GetPersonID` | SCALAR_FUNCTION | OLTP | INCREMENTAL, SCD2 |
| `DataLoadSimulation.GetStateProvinceID` | SCALAR_FUNCTION | OLTP | INCREMENTAL, SCD2 |
| `DataLoadSimulation.GetSupplierCategoryID` | SCALAR_FUNCTION | OLTP | INCREMENTAL, SCD2 |
| `DataLoadSimulation.GetTransactionTypeID` | SCALAR_FUNCTION | OLTP | INCREMENTAL, SCD2 |
| `Website.CalculateCustomerPrice` | SCALAR_FUNCTION | OLTP | — |
| `Integration.GenerateDateDimensionColumns` | TVF_INLINE | DW | — |

### 4e. SSIS Package

> **Confidence:** 🟢 HIGH

See Section 3 (ETL / Orchestration Overview) for the full breakdown. Summary of task type distribution:

| Task Type | Count | Target Databricks Equivalent |
|---|---|---|
| `SSIS_SEQUENCE_CONTAINER` | 13 | Databricks Workflow task group |
| `SSIS_EXECUTE_SQL` | 53 | Notebook task (SQL cell) or Workflow parameter |
| `SSIS_EXPRESSION` | 15 | Workflow parameter / `dbutils.widgets` |
| `SSIS_DATA_FLOW` | 13 | PySpark notebook task |
| `SSIS_PACKAGE` | 1 | Databricks Workflow (JSON) |

## 5. Dependency Map

> **Confidence:** 🟡 MEDIUM

The dependency graph contains **414 nodes** and **584 directed edges**. No cycles were detected — the graph is a valid DAG and a safe topological deployment order exists.

### Edge Types

| Edge Type | Count | Meaning |
|---|---|---|
| SQL_REFERENCE | 388 | FROM/JOIN reference in SQL body |
| FUNCTION_CALL | 86 | Scalar or TVF call in SQL body |
| CALLS_PROC | 40 | SSIS Execute SQL task → stored procedure |
| READS_FROM | 0 | SSIS task reads from a table |
| WRITES_TO | 0 | SSIS task writes to a table |
| DATA_FLOW | 5 | Staging table → DW target data movement |
| SSIS_CONTROL_FLOW_SUCCESS | 65 | Precedence constraint (on success) |

### Most Depended-Upon Objects (highest fan-in)

These objects are the highest-blast-radius items in the migration. Converting them incorrectly will cascade failures across many dependants.

| Object | Type | Fan-in | Layer | Risk |
|---|---|---|---|---|
| `Application.People` | TABLE | 27 | BRONZE | LOW |
| `Sales.Customers` | TABLE | 24 | BRONZE | LOW |
| `Warehouse.StockItems` | TABLE | 23 | BRONZE | LOW |
| `Application.Cities` | TABLE | 17 | BRONZE | LOW |
| `Sales.Orders` | TABLE | 16 | BRONZE | NONE |
| `Sales.OrderLines` | TABLE | 15 | BRONZE | NONE |
| `Integration.Lineage` | TABLE | 15 | BRONZE | NONE |
| `Sales.Invoices` | TABLE | 14 | BRONZE | NONE |
| `Integration.ETL` | TABLE | 14 | BRONZE | NONE |
| `Application.StateProvinces` | TABLE | 13 | BRONZE | LOW |
| `Integration.GetLastETLCutoffTime` | PROCEDURE | 13 | BRONZE | NONE |
| `Integration.GetLineageKey` | PROCEDURE | 13 | BRONZE | NONE |

### Highest Fan-Out Objects (most dependencies consumed)

| Object | Type | Fan-out | Layer |
|---|---|---|---|
| `Integration.Get Lineage Key` | SSIS_EXECUTE_SQL | 26 | BRONZE |
| `DataLoadSimulation.DailyProcessToCreateHistory` | PROCEDURE | 25 | BRONZE |
| `Application.Configuration_EnableInMemory` | PROCEDURE | 17 | BRONZE |
| `Application.Configuration_DisableInMemory` | PROCEDURE | 16 | BRONZE |
| `DataLoadSimulation.InvoicePickedOrders` | PROCEDURE | 13 | BRONZE |
| `Website.InvoiceCustomerOrders` | PROCEDURE | 12 | SILVER |
| `Integration.Get Last Movement ETL Cutoff Time` | SSIS_EXECUTE_SQL | 12 | BRONZE |
| `DataLoadSimulation.ReceivePurchaseOrders` | PROCEDURE | 9 | BRONZE |

### ETL Data Movement Lineage

The complete source-to-target data flow for each entity:

```
OLTP (temporal table)  →  Integration.Get<Entity>Updates (cursor proc)
                       →  [SSIS Data Flow: OLE DB Source → OLE DB Destination]
                       →  DW.Integration.<Entity>_Staging
                       →  Integration.MigrateStaged<Entity>Data (SCD2 proc)
                       →  Dimension.<Entity>  OR  Fact.<Entity>
```

| Entity | OLTP Source | Staging | DW Target | Load Type |
|---|---|---|---|---|
| City | `Application.Cities + archive` | `Integration.City_Staging` | `Dimension.City` | SCD2 Incremental |
| Customer | `Sales.Customers + archive` | `Integration.Customer_Staging` | `Dimension.Customer` | SCD2 Incremental |
| Employee | `Application.People + archive` | `Integration.Employee_Staging` | `Dimension.Employee` | SCD2 Incremental |
| Payment Method | `Application.PaymentMethods` | `Integration.PaymentMethod_Staging` | `Dimension.Payment Method` | SCD2 Incremental |
| Stock Item | `Warehouse.StockItems + archive` | `Integration.StockItem_Staging` | `Dimension.Stock Item` | SCD2 Incremental |
| Supplier | `Purchasing.Suppliers + archive` | `Integration.Supplier_Staging` | `Dimension.Supplier` | SCD2 Incremental |
| Transaction Type | `Application.TransactionTypes` | `Integration.TransactionType_Staging` | `Dimension.Transaction Type` | SCD2 Incremental |
| Order | `Sales.Orders + OrderLines` | `Integration.Order_Staging` | `Fact.Order` | Incremental |
| Sale | `Sales.Invoices + InvoiceLines` | `Integration.Sale_Staging` | `Fact.Sale` | Incremental |
| Purchase | `Purchasing.PurchaseOrders + Lines` | `Integration.Purchase_Staging` | `Fact.Purchase` | Incremental |
| Movement | `Warehouse.StockItemTransactions` | `Integration.Movement_Staging` | `Fact.Movement` | Full (no cutoff) |
| Transaction | `Sales + Purchasing transactions` | `Integration.Transaction_Staging` | `Fact.Transaction` | Incremental |
| Stock Holding | `Warehouse.StockItemHoldings` | `Integration.StockHolding_Staging` | `Fact.Stock Holding` | Full snapshot |
| Date | `Computed (no OLTP source)` | `Integration.—` | `Dimension.Date` | Annual extension |

## 6. Data Domains

> **Confidence:** 🟢 HIGH

| Domain | OLTP Tables | DW Targets | Description |
|---|---|---|---|
| Sales & Revenue | Sales.Customers, Sales.Orders, Sales.OrderLines, Sales.Invoices, Sales.InvoiceLines, Sales.CustomerTransactions, Sales.SpecialDeals, Sales.BuyingGroups | Fact.Sale, Fact.Order, Dimension.Customer | Order-to-cash — customer orders, pick/pack, invoicing, payment transactions |
| Purchasing & Supply | Purchasing.Suppliers, Purchasing.PurchaseOrders, Purchasing.PurchaseOrderLines, Purchasing.SupplierTransactions | Fact.Purchase, Dimension.Supplier | Procure-to-pay — supplier orders, goods receipt, supplier payments |
| Warehouse & Inventory | Warehouse.StockItems, Warehouse.StockItemHoldings, Warehouse.StockItemTransactions, Warehouse.StockItemStockGroups, Warehouse.Colors, Warehouse.PackageTypes | Fact.Movement, Fact.Stock Holding, Dimension.Stock Item | Stock management — holdings, movements, physical attributes |
| Reference / Master Data | Application.Countries, Application.Cities, Application.StateProvinces, Application.People, Application.DeliveryMethods, Application.PaymentMethods, Application.TransactionTypes | Dimension.City, Dimension.Employee, Dimension.Payment Method, Dimension.Transaction Type | Geography, people, lookup reference data — all system-versioned temporal |
| IoT / Telemetry | Warehouse.ColdRoomTemperatures, Warehouse.VehicleTemperatures, DataLoadSimulation.ColdRoomTemperatures_temp | Website.VehicleTemperatures (view only) | Sensor data from cold-chain equipment. Memory-optimised tables. No DW target — not in ETL scope. |
| Financial Transactions | Sales.CustomerTransactions, Purchasing.SupplierTransactions | Fact.Transaction | Dual-sided financial transaction ledger (customer + supplier combined in Fact.Transaction) |
| ETL Control / Audit | Integration.ETL Cutoff, Integration.Lineage | — | ETL watermark and lineage tracking. Replaced by Databricks run metadata in target. |

## 7. Load Patterns

> **Confidence:** 🟢 HIGH

Four distinct load patterns are present in the WWI ETL:

### Pattern 1 — SCD Type 2 Incremental (Dimensions)

**Entities:** City, Customer, Employee, Payment Method, Stock Item, Supplier, Transaction Type

```
1. Read LastCutoffTime from Integration.ETL Cutoff WHERE Table = '<Entity>'
2. OLTP proc Get<Entity>Updates(@LastCutoff, @TargetCutoff):
   a. CURSOR over temporal archive rows WHERE ValidFrom IN cutoff window
   b. Reconstruct point-in-time state using FOR SYSTEM_TIME AS OF
   c. Compute Valid From / Valid To for each version
   d. INSERT into #CityChanges temp table
   e. UPDATE #CityChanges.ValidTo = MIN(later ValidFrom) for same entity
   f. SELECT to SSIS data flow
3. SSIS Data Flow: OLE DB Source → OLE DB Destination (bulk insert to staging)
4. DW proc MigrateStaged<Entity>Data:
   a. UPDATE Dimension rows: Valid To = earliest staging row ValidFrom (close off)
   b. INSERT staging rows into Dimension (new SCD2 versions)
   c. UPDATE Lineage: mark complete
   d. UPDATE ETL Cutoff watermark
```

**Databricks target:** Delta MERGE INTO with SCD2 history column + `Valid From`/`Valid To`

### Pattern 2 — Incremental Append (Facts — no SCD)

**Entities:** Sale, Order, Purchase, Transaction

```
1. Get cutoff time
2. OLTP proc: SELECT new rows WHERE LastEditedWhen > @LastCutoff
3. SSIS: bulk load to staging
4. MigrateStaged*: plain INSERT from staging into Fact (no update / close-off)
5. Update watermark
```

**Databricks target:** Delta append (`df.write.mode('append')`) or MERGE on surrogate key

### Pattern 3 — Full Snapshot (Stock Holding Fact)

**Entity:** Stock Holding

```
1. No cutoff window — full extract of current Warehouse.StockItemHoldings
2. Staging bulk load
3. MigrateStaged: DELETE existing rows + INSERT (full replace each run)
```

**Databricks target:** Delta `overwrite` mode with `replaceWhere` on date partition

### Pattern 4 — Annual Extension (Date Dimension)

**Entity:** Date

```
1. EXEC Integration.PopulateDateDimensionForYear @YearNumber (at package start)
2. Uses Integration.GenerateDateDimensionColumns TVF
3. INSERT new year rows only (no update to existing dates)
```

**Databricks target:** Notebook cell — compute date range + Delta append

### Pattern Summary

| Pattern | Entities | Load Type | Complexity | Target Approach |
|---|---|---|---|---|
| SCD Type 2 | 7 dimensions | Incremental + history | HIGH | Delta MERGE INTO with SCD2 columns |
| Incremental Append | 4 facts | Append new rows | LOW | Delta APPEND or MERGE on PK |
| Full Snapshot | Stock Holding | Full replace per run | LOW | Delta OVERWRITE with replaceWhere |
| Annual Extension | Date dimension | Append new year | LOW | Notebook compute + Delta APPEND |

## 8. Operational Assumptions

> **Confidence:** 🟡 MEDIUM

The following assumptions are inferred from the code and metadata. They should be validated with the WWI operations team before migration.

| ID | Confidence | Assumption |
|---|---|---|
| SCH-01 | 🟢 HIGH | The ETL runs once per day (nightly), consistent with package name `DailyETLMain` |
| SCH-02 | 🟡 MEDIUM | The package runs with SQL Server Agent or Windows Task Scheduler — no SQL Agent XML was found |
| SCH-03 | 🟡 MEDIUM | The 5-minute cutoff buffer (`GETUTCDATE() - 5 min`) guards against long-running OLTP transactions; this cadence must be preserved in Databricks |
| DAT-01 | 🟢 HIGH | All OLTP tables use UTC timestamps (`ValidFrom`, `LastEditedWhen` are UTC); no timezone conversion required |
| DAT-02 | 🟢 HIGH | `Integration.ETL Cutoff` is the single watermark store — one row per entity; must be migrated or replaced before first Databricks run |
| DAT-03 | 🟡 MEDIUM | `Integration.Lineage` acts as the audit log; a comparable audit Delta table should be maintained in the target |
| DAT-04 | 🟢 HIGH | SCD2 `Valid To` = `'9999-12-31 23:59:59.9999999'` signals the current active row — this sentinel value is used consistently across all Migrate procs |
| INF-01 | 🟢 HIGH | Both databases are on the same SQL Server instance — SSIS uses local OLE DB connections; target uses JDBC or Unity Catalog external tables |
| INF-02 | 🔴 LOW | Integrated Security (SSPI/Windows) is used — must be replaced with Databricks secrets + SQL Server JDBC with SQL auth or Entra ID |
| SEC-01 | 🟡 MEDIUM | All Integration procs use `WITH EXECUTE AS OWNER` — privilege elevation pattern not applicable in Databricks; Unity Catalog governs access |
| SCO-01 | 🟢 HIGH | `DataLoadSimulation` schema is a test harness and should NOT be migrated to Databricks |
| SCO-02 | 🟢 HIGH | `WebApi` and `Website` schemas serve the application tier; they are not ETL objects and should NOT be replicated as-is in the DW |
| SCO-03 | 🟡 MEDIUM | IoT tables (`ColdRoomTemperatures`, `VehicleTemperatures`) have no DW staging/migration path — out of scope for this migration unless a streaming path is added |

## 9. Technical Debt / Migration Hotspots

> **Confidence:** 🟢 HIGH

### Complexity Hotspot Map

Objects scoring ≥ 5 on the complexity index require manual conversion effort:

| Object | Score | Risk | Pattern Flags | Effort Estimate |
|---|---|---|---|---|
| `Integration.GetCityUpdates` | 10 | HIGH | CURSOR, FOR\s+SYSTEM_TIME, #\w+, WHILE | 2–5 days |
| `Integration.GetCustomerUpdates` | 10 | HIGH | CURSOR, FOR\s+SYSTEM_TIME, #\w+, WHILE | 2–5 days |
| `Integration.GetEmployeeUpdates` | 10 | HIGH | CURSOR, FOR\s+SYSTEM_TIME, #\w+, WHILE | 2–5 days |
| `Integration.GetPaymentMethodUpdates` | 10 | HIGH | CURSOR, FOR\s+SYSTEM_TIME, #\w+, WHILE | 2–5 days |
| `Integration.GetStockItemUpdates` | 10 | HIGH | CURSOR, FOR\s+SYSTEM_TIME, #\w+, WHILE | 2–5 days |
| `Integration.GetSupplierUpdates` | 10 | HIGH | CURSOR, FOR\s+SYSTEM_TIME, #\w+, WHILE | 2–5 days |
| `Integration.GetTransactionTypeUpdates` | 10 | HIGH | CURSOR, FOR\s+SYSTEM_TIME, #\w+, WHILE | 2–5 days |
| `ETL.DailyETLMain` | 10 | MEDIUM |  | 2–5 days |
| `DataLoadSimulation.PickStockForCustomerOrders` | 8 | MEDIUM | CURSOR, MERGE, WHILE | 1–2 days |
| `WebApi.SearchForStockItems` | 7 | MEDIUM | FOR\s+XML, OPENJSON | 1–2 days |
| `DataLoadSimulation.InvoicePickedOrders` | 6 | MEDIUM | CURSOR, WHILE | 1–2 days |
| `DataLoadSimulation.ReceivePurchaseOrders` | 6 | MEDIUM | CURSOR, WHILE | 1–2 days |
| `DataLoadSimulation.RecordInvoiceDeliveries` | 6 | MEDIUM | CURSOR, WHILE | 1–2 days |
| `DataLoadSimulation.UpdateCustomFields` | 6 | MEDIUM | CURSOR, WHILE | 1–2 days |

### Critical Migration Issues

| ID | Issue | Description | Impact | Effort |
|---|---|---|---|---|
| CRI-01 | **`geography` data type** | Used in `Application.Cities` and `Dimension.City.[Location]`. Spark has no native spatial type. Must be stored as WKT `STRING`. If geospatial queries are needed, use Databricks H3 or Mosaic library. | HIGH | 2–3 days |
| CRI-02 | **CURSOR loops in 7 `Get<Entity>Updates` procs** | Each cursor iterates over temporal archive rows to reconstruct SCD history. Must be rewritten as PySpark temporal joins across current + archive DataFrames. Pattern is identical across all 7 — one implementation, 7 parameterisations. | HIGH | 3–5 days (shared pattern) |
| CRI-03 | **`FOR SYSTEM_TIME AS OF` temporal queries** | T-SQL temporal time-travel syntax has no direct PySpark equivalent. Delta Lake Change Data Feed (`readChangeFeed`) provides similar semantics but requires CDF to be enabled on the source Delta table. | HIGH | 1–2 days |
| CRI-04 | **`VARBINARY(MAX)` photo column in `Dimension.Employee`** | Binary large objects in dimension tables are unusual. In Databricks, store as `BINARY` or externalise to Unity Catalog Volumes. | MEDIUM | 0.5 days |
| CRI-05 | **`DECIMAL(18,2)` / `DECIMAL(18,3)` precision** | Spark `DECIMAL(18,2)` maps exactly — no data loss. Validate that no column exceeds precision 38 (Spark maximum). | LOW | 0.5 days |
| CRI-06 | **`NVARCHAR(MAX)` free-text columns** | Maps to Spark `STRING`. Collation-sensitive sorting and comparison will behave differently in Spark (no SQL Server collation). Impact is low for DW analytics use cases. | LOW | < 0.5 days |
| CRI-07 | **Memory-optimised tables (`MEMORY_OPTIMIZED = ON`)** | `Warehouse.ColdRoomTemperatures` and `Warehouse.VehicleTemperatures` use SQL Server In-Memory OLTP for IoT sensor ingestion. No DW ETL path exists. If streaming is required, use Databricks Structured Streaming from SQL Server CDC. | MEDIUM | Out of scope for batch ETL |
| CRI-08 | **Partition schemes (`PS_Date`)** | All Fact tables use a SQL Server date partition scheme. Replace with Delta Lake `PARTITIONED BY (date_key DATE)` + `OPTIMIZE ... ZORDER BY` on frequently filtered FK keys. | LOW | 1 day |
| CRI-09 | **`WITH EXECUTE AS OWNER` privilege escalation** | All Integration procs use owner-context execution. In Databricks, use Unity Catalog column/row-level security and service principals with least-privilege grants. | LOW | 0.5 days |
| CRI-10 | **SSIS `ExpressionTask` variable assignments** | 15 expression tasks set variables like `@TargetETLCutoffTime = DATEADD(...)`. Replace with Databricks Workflow job parameters and `dbutils.widgets`. | LOW | 0.5 days |

### Objects Excluded from Migration Scope

| Object/Group | Count | Reason for Exclusion |
|---|---|---|
| `DataLoadSimulation.*` | 43 procs + 4 tables | Test data generation harness — no business value in DW |
| `WebApi.*` | 24 views + 53 procs | Application CRUD layer — belongs to the application tier |
| `Website.*` | 3 views + 11 procs | Web application layer — not ETL objects |
| Temporal archive tables | 18 `*_Archive` tables | SQL Server system-managed — queried by Get* procs; not migrated directly |
| OLTP Sequences | 26 SEQUENCE objects | Replaced by Delta `GENERATED ALWAYS AS IDENTITY` or SEQUENCE objects in UC |
| Security objects | 18 role/permission scripts | Unity Catalog governs access — not migrated |
| Memory-optimised IoT tables | 3 tables | No DW ETL path — out of scope unless streaming added |
| `Integration.ETL Cutoff` table | 1 table | Replaced by Databricks Workflow state / job run metadata |
| `Integration.Lineage` table | 1 table | Replaced by Databricks job run history + optional audit Delta table |
