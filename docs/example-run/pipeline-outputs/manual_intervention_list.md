# Manual Intervention List

> 106 objects require **manual redesign** and 63 objects require a **rewrite** (automatable in structure but not in logic). Both lists below need a human migration engineer; manual-redesign objects additionally need a design decision before any conversion work starts.

## Manual Redesign Required

These objects have no automated conversion path — a target-state design decision is needed before implementation can begin.

| Object | Type | Why | Suggested Approach | Blast Radius (transitive) |
|---|---|---|---|---|
| OLTP:Application.Cities | TABLE | geography(+5); TEMPORAL(+3) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 25 |
| OLTP:Application.StateProvinces | TABLE | geography(+5); TEMPORAL(+3) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 20 |
| OLTP:Integration.GetCityUpdates | PROCEDURE | geography(+5); row_by_row_cursor(+2); EXECUTE\s+AS\s+OWNER(+2) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 0 |
| OLTP:Purchasing.Suppliers | TABLE | geography(+5); TEMPORAL(+3) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 17 |
| OLTP:Sales.Customers | TABLE | geography(+5); TEMPORAL(+3) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 31 |
| OLTP:Application.Countries | TABLE | geography(+5); TEMPORAL(+3) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 11 |
| OLTP:Integration.GetStockItemUpdates | PROCEDURE | nvarchar\(max\)(+1); row_by_row_cursor(+2); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review — see current_state_documentation.md technical debt section | 0 |
| OLTP:Application.Configuration_EnableInMemory | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 1 |
| OLTP:Application.DeliveryMethods | TABLE | TEMPORAL(+3) | Dedicated design review required before conversion | 11 |
| OLTP:Application.People | TABLE | TEMPORAL(+3) | Dedicated design review required before conversion | 39 |
| OLTP:Application.TransactionTypes | TABLE | TEMPORAL(+3) | Dedicated design review required before conversion | 16 |
| OLTP:Integration.GetEmployeeUpdates | PROCEDURE | nvarchar\(max\)(+1); row_by_row_cursor(+2); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review — see current_state_documentation.md technical debt section | 0 |
| OLTP:Sales.BuyingGroups | TABLE | TEMPORAL(+3) | Dedicated design review required before conversion | 14 |
| OLTP:Sales.CustomerCategories | TABLE | TEMPORAL(+3) | Dedicated design review required before conversion | 13 |
| OLTP:Warehouse.PackageTypes | TABLE | TEMPORAL(+3) | Dedicated design review required before conversion | 16 |
| OLTP:Warehouse.StockItems | TABLE | TEMPORAL(+3) | Dedicated design review required before conversion | 29 |
| OLTP:Application.PaymentMethods | TABLE | TEMPORAL(+3) | Dedicated design review required before conversion | 11 |
| OLTP:DataLoadSimulation.UpdateCustomFields | PROCEDURE | nvarchar\(max\)(+1); row_by_row_cursor(+2); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 4 |
| OLTP:Integration.GetCustomerUpdates | PROCEDURE | row_by_row_cursor(+2); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review — see current_state_documentation.md technical debt section | 0 |
| OLTP:Integration.GetSupplierUpdates | PROCEDURE | row_by_row_cursor(+2); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review — see current_state_documentation.md technical debt section | 0 |
| OLTP:Purchasing.SupplierCategories | TABLE | TEMPORAL(+3) | Dedicated design review required before conversion | 6 |
| OLTP:Warehouse.ColdRoomTemperatures | TABLE | MEMORY_OPTIMIZED(+4) | Replace with standard Delta table; re-evaluate need for in-memory OLTP semantics | 10 |
| OLTP:Warehouse.Colors | TABLE | TEMPORAL(+3) | Dedicated design review required before conversion | 12 |
| OLTP:Warehouse.StockGroups | TABLE | TEMPORAL(+3) | Dedicated design review required before conversion | 9 |
| OLTP:Integration.GetPaymentMethodUpdates | PROCEDURE | row_by_row_cursor(+2); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review — see current_state_documentation.md technical debt section | 0 |
| OLTP:Integration.GetTransactionTypeUpdates | PROCEDURE | row_by_row_cursor(+2); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review — see current_state_documentation.md technical debt section | 0 |
| OLTP:Application.Configuration_DisableInMemory | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 1 |
| OLTP:DataLoadSimulation.PickStockForCustomerOrders | PROCEDURE | row_by_row_cursor(+2) | Dedicated design review required before conversion | 4 |
| OLTP:DataLoadSimulation.RecordInvoiceDeliveries | PROCEDURE | nvarchar\(max\)(+1); row_by_row_cursor(+2); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 4 |
| DW:Dimension.City | TABLE | geography(+5) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 33 |
| OLTP:Application.Configuration_ApplyRowLevelSecurity | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2); ROW\s+LEVEL\s+SECURITY(+4) | Dedicated design review required before conversion | 5 |
| OLTP:DataLoadSimulation.DailyProcessToCreateHistory | PROCEDURE | ROW\s+LEVEL\s+SECURITY(+4) | Dedicated design review required before conversion | 3 |
| OLTP:DataLoadSimulation.RecordDeliveryVanTemperatures | PROCEDURE | geometry(+5); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 4 |
| OLTP:Website.RecordVehicleTemperature | PROCEDURE | geometry(+5); nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| DW:Integration.GetLastETLCutoffTime | PROCEDURE | EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 35 |
| OLTP:DataLoadSimulation.InvoicePickedOrders | PROCEDURE | nvarchar\(max\)(+1); row_by_row_cursor(+2) | Dedicated design review required before conversion | 4 |
| OLTP:Website.RecordColdRoomTemperatures | PROCEDURE | EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| DW:Integration.City_Staging | TABLE | geography(+5) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 19 |
| OLTP:Application.Cities_Archive | TABLE | geography(+5) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 1 |
| OLTP:Application.Countries_Archive | TABLE | geography(+5) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 1 |
| OLTP:Application.StateProvinces_Archive | TABLE | geography(+5) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 1 |
| OLTP:DataLoadSimulation.ReceivePurchaseOrders | PROCEDURE | row_by_row_cursor(+2) | Dedicated design review required before conversion | 4 |
| OLTP:DataLoadSimulation.ColdRoomTemperatures_temp | TABLE | MEMORY_OPTIMIZED(+4) | Replace with standard Delta table; re-evaluate need for in-memory OLTP semantics | 6 |
| OLTP:Purchasing.Suppliers_Archive | TABLE | geography(+5) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 1 |
| OLTP:Sales.Customers_Archive | TABLE | geography(+5) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 1 |
| OLTP:Warehouse.VehicleTemperatures | TABLE | MEMORY_OPTIMIZED(+4) | Replace with standard Delta table; re-evaluate need for in-memory OLTP semantics | 9 |
| OLTP:WebApi.Customers | VIEW | geometry(+5) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.Suppliers | VIEW | geometry(+5) | Dedicated design review required before conversion | 0 |
| DW:Integration.GetLineageKey | PROCEDURE | EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 14 |
| DW:Integration.ETL | TABLE | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 75 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| SSIS:DailyETLMain:Get Lineage Key | SSIS_EXECUTE_SQL | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 13 |
| OLTP:WebApi.Cities | VIEW | geometry(+5) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.SalesOrders | VIEW | geometry(+5) | Dedicated design review required before conversion | 0 |
| OLTP:Application.Configuration_RemoveRowLevelSecurity | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2); ROW\s+LEVEL\s+SECURITY(+4) | Dedicated design review required before conversion | 5 |
| OLTP:Sales.CustomerTransactions | TABLE | PARTITIONED(+2) | Dedicated design review required before conversion | 14 |
| OLTP:Sales.InvoiceLines | TABLE | COLUMNSTORE(+2) | Dedicated design review required before conversion | 13 |
| OLTP:Sales.OrderLines | TABLE | COLUMNSTORE(+2) | Dedicated design review required before conversion | 18 |
| OLTP:WebApi.InsertBuyingGroupsFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertCitiesFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertColorsFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertCountriesFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertCustomerCategoriesFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertCustomersFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertDeliveryMethodsFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertPackageTypesFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertPaymentMethodsFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertStateProvincesFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertStockGroupsFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertStockItemsFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertSupplierCategoriesFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertSuppliersFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.InsertTransactionTypesFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.UpdateCustomerFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.UpdateCustomerTransactionFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.UpdateInvoiceFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.UpdatePurchaseOrderFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.UpdateSalesOrderFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.UpdateSpecialDealFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.UpdateStockItemFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.UpdateSupplierFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.UpdateSupplierTransactionFromJson | PROCEDURE | nvarchar\(max\)(+1); EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| OLTP:WebApi.SearchForStockItems | PROCEDURE | EXECUTE\s+AS\s+OWNER(+2) | Dedicated design review required before conversion | 0 |
| DW:Fact.Purchase | TABLE | COLUMNSTORE(+2); PARTITIONED(+2) | Dedicated design review required before conversion | 24 |
| DW:Fact.Sale | TABLE | COLUMNSTORE(+2); PARTITIONED(+2) | Dedicated design review required before conversion | 25 |
| OLTP:Application.SystemParameters | TABLE | geography(+5) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 0 |
| OLTP:DataLoadSimulation.GetCityLocation | SCALAR_FUNCTION | geography(+5) | Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona) | 0 |
| OLTP:Sales.Invoices | TABLE | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 16 |
| OLTP:Sales.Orders | TABLE | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 15 |
| OLTP:Warehouse.StockItemHoldings | TABLE | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 19 |
| OLTP:WebApi.StateProvinces | VIEW | geometry(+5) | Dedicated design review required before conversion | 0 |
| DW:Fact.Order | TABLE | COLUMNSTORE(+2); PARTITIONED(+2) | Dedicated design review required before conversion | 24 |
| DW:Integration.Lineage | TABLE | Compounding risk across multiple dimensions | Dedicated design review required before conversion | 76 |
| DW:Fact.Movement | TABLE | COLUMNSTORE(+2); PARTITIONED(+2) | Dedicated design review required before conversion | 0 |
| DW:Fact.Transaction | TABLE | COLUMNSTORE(+2); PARTITIONED(+2) | Dedicated design review required before conversion | 0 |

## Rewrite Required

Structurally convertible, but procedural/control-flow logic must be hand-translated rather than pattern-matched.

| Object | Type | Why | Blast Radius (transitive) |
|---|---|---|---|
| DW:Integration.MigrateStagedMovementData | PROCEDURE | MERGE(+3); TOP\s*\((+1) | 23 |
| OLTP:DataLoadSimulation.AddCustomers | PROCEDURE | WHILE(+3); RAISERROR(+1); TOP\s*\((+1) | 4 |
| OLTP:DataLoadSimulation.ActivateWebsiteLogons | PROCEDURE | WHILE(+3); RAISERROR(+1); TOP\s*\((+1) | 4 |
| OLTP:DataLoadSimulation.ChangePasswords | PROCEDURE | WHILE(+3); RAISERROR(+1); TOP\s*\((+1) | 4 |
| OLTP:DataLoadSimulation.RecordColdRoomTemperatures | PROCEDURE | WHILE(+3); RAISERROR(+1); OUTPUT\s+INSERTED(+2) | 4 |
| OLTP:DataLoadSimulation.DeactivateTemporalTablesBeforeDataLoad | PROCEDURE | RAISERROR(+1); FOR\s+SYSTEM_TIME(+4) | 4 |
| OLTP:DataLoadSimulation.MakeTemporalChanges | PROCEDURE | WHILE(+3); RAISERROR(+1); TOP\s*\((+1) | 4 |
| OLTP:DataLoadSimulation.PopulateColdRoomTemperatures_temp | PROCEDURE | WHILE(+3); ISNULL\s*\((+1) | 5 |
| OLTP:DataLoadSimulation.CreateCustomerOrders | PROCEDURE | WHILE(+3); TOP\s*\((+1) | 4 |
| OLTP:DataLoadSimulation.GetRandomEmployeePerson | PROCEDURE | TOP\s*\((+1) | 10 |
| OLTP:DataLoadSimulation.ReactivateTemporalTablesAfterDataLoad | PROCEDURE | FOR\s+SYSTEM_TIME(+4) | 4 |
| DW:Integration.PopulateDateDimensionForYear | PROCEDURE | WHILE(+3); RAISERROR(+1) | 2 |
| DW:Application.Configuration_PopulateLargeSaleTable | PROCEDURE | WHILE(+3); RAISERROR(+1); TOP\s*\((+1) | 0 |
| DW:Dimension.Customer | TABLE | Elevated complexity score | 39 |
| DW:Dimension.Employee | TABLE | Elevated complexity score | 33 |
| DW:Dimension.Stock | TABLE | Elevated complexity score | 41 |
| DW:Dimension.Supplier | TABLE | Elevated complexity score | 35 |
| OLTP:Purchasing.SupplierTransactions | TABLE | Elevated complexity score | 10 |
| OLTP:Warehouse.StockItemTransactions | TABLE | Elevated complexity score | 13 |
| OLTP:WebApi.UpdateBuyingGroupFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:WebApi.UpdateCityFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:WebApi.UpdateColorFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:WebApi.UpdateCountryFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:WebApi.UpdateCustomerCategoryFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:WebApi.UpdateDeliveryMethodFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:WebApi.UpdatePackageTypeFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:WebApi.UpdatePaymentMethodFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:WebApi.UpdateStateProvinceFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:WebApi.UpdateStockGroupFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:WebApi.UpdateSupplierCategoryFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:WebApi.UpdateTransactionTypeFromJson | PROCEDURE | OPENJSON(+4) | 0 |
| OLTP:Website.CalculateCustomerPrice | SCALAR_FUNCTION | Elevated complexity score | 10 |
| OLTP:Application.CreateRoleIfNonexistent | PROCEDURE | RAISERROR(+1) | 0 |
| OLTP:DataLoadSimulation.PerformStocktake | PROCEDURE | WHILE(+3); TOP\s*\((+1) | 4 |
| OLTP:Website.SearchForCustomers | PROCEDURE | FOR\s+XML(+3); TOP\s*\((+1) | 0 |
| OLTP:Website.SearchForStockItems | PROCEDURE | FOR\s+XML(+3); TOP\s*\((+1) | 0 |
| OLTP:Website.SearchForStockItemsByTags | PROCEDURE | FOR\s+XML(+3); TOP\s*\((+1) | 0 |
| SSIS:DailyETLMain:Calculate ETL Cutoff Time backup | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| OLTP:DataLoadSimulation.GetRandomBuyingGroupNotInUse | PROCEDURE | WHILE(+3) | 5 |
| OLTP:DataLoadSimulation.GetRandomCity | PROCEDURE | WHILE(+3) | 6 |
| OLTP:DataLoadSimulation.GetRandomSecondaryAddress | PROCEDURE | WHILE(+3) | 5 |
| OLTP:DataLoadSimulation.GetRandomStreet | PROCEDURE | WHILE(+3) | 5 |
| OLTP:DataLoadSimulation.GetRandomStreetName | PROCEDURE | WHILE(+3) | 6 |
| OLTP:DataLoadSimulation.GetRandomStreetSuffix | PROCEDURE | WHILE(+3) | 6 |
| OLTP:Purchasing.PurchaseOrderLines | TABLE | Elevated complexity score | 8 |
| OLTP:Purchasing.PurchaseOrders | TABLE | Elevated complexity score | 9 |
| OLTP:Warehouse.StockItemStockGroups | TABLE | Elevated complexity score | 14 |
| OLTP:Website.SearchForPeople | PROCEDURE | FOR\s+XML(+3); TOP\s*\((+1) | 0 |
| OLTP:Website.SearchForSuppliers | PROCEDURE | FOR\s+XML(+3); TOP\s*\((+1) | 0 |
| SSIS:DailyETLMain:Set TableName to City | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Customer | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Employee | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Movement | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Order | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Payment Method | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Purchase | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Sale | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Stock Holding | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Stock Item | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Supplier | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Transaction | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Set TableName to Transaction Type | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |
| SSIS:DailyETLMain:Trim Any Milliseconds | SSIS_EXPRESSION | SSIS_expression_requires_manual_translation(+2) | 0 |

## Sign-off Checklist (per manual-redesign object)

- [ ] Target data type / pattern decided and documented in target-state design
- [ ] Spike/prototype validated against a representative data sample
- [ ] Reconciliation test written and passing against source system
- [ ] Performance validated at production data volume
- [ ] Rollback procedure documented and rehearsed
- [ ] Sign-off obtained from data owner / business stakeholder
