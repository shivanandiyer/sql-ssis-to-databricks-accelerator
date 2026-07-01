# Orchestration Design — SSIS Control Flow -> Databricks Workflows

> **Generated:** 2026-06-30 12:34 UTC

## Mapping Rules

### Package To Job

**Rule:** Each SSIS package becomes one Databricks Workflow (multi-task job).

**Rationale:** Preserves the existing single-pipeline mental model and keeps the job's run history, alerting, and SLA configuration in one place.

### Sequence Container To Task Group

**Rule:** Each Sequence Container becomes either a Workflow task group (if-all-success dependency chain) or, preferably, its own job-as-task referenced from the parent job — one per entity (City, Customer, Date, Employee, Payment, StockItem, Supplier, Transaction, Movement, Order, Purchase, Sale, Stock).

**Rationale:** Per-entity isolation means a failure loading one dimension doesn't block unrelated dimensions from completing, and lets entity loads run in parallel where the dependency graph allows it (see ordering note below) instead of SSIS's single-threaded sequential container execution.

**Tradeoffs:** Increases the number of Workflow task definitions to maintain (13 vs 1); mitigated by generating them from a single parameterised job template (entity name as a job parameter) rather than hand-authoring 13 jobs.

### Five Step Pattern To Tasks

**Rule:** The recurring 5-step pattern (Get Cutoff -> Truncate Staging -> Extract -> Get Lineage Key -> Migrate) becomes 3 Workflow tasks, not 5: (1) a PySpark/SQL task that reads the watermark and extracts incrementally in one step (Auto Loader or a parameterised SQL read replaces the separate truncate+extract steps because Delta overwrite mode makes the explicit TRUNCATE redundant), (2) a MERGE task that applies SCD2 logic and lineage-key assignment together, (3) a watermark-update task that advances the cutoff only after step 2 succeeds.

**Rationale:** Several SSIS steps exist to work around SQL Server's lack of atomic upsert-with-history; Delta's MERGE INTO with SCD2 expressions collapses those steps. Fewer tasks means fewer points of partial failure to reason about during cutover.

**Tradeoffs:** Less granular task-level retry (a failure anywhere in the combined extract step reprocesses the whole step) — acceptable because the step is now idempotent (Delta overwrite/MERGE), unlike the original truncate-then-load sequence which was not safe to blindly retry mid-sequence.

**Watermark design:** Replace the `Integration.ETL Cutoff` SQL table with a small Delta table `wwi_<env>.ops.etl_watermark(entity, last_cutoff_ts)`, read and updated via the same MERGE transaction pattern as the data load to guarantee watermark advancement is atomic with the data write.

### Precedence Constraints To Dependencies

**Rule:** SSIS precedence constraints (Success/Failure/Completion) map directly to Databricks Workflow task `depends_on` with `run_if` conditions (ALL_SUCCESS / ALL_FAILED / ALL_DONE).

**Rationale:** 1:1 semantic equivalent exists in Workflows — no redesign needed here.

### Expressions To Parameters

**Rule:** The 15 SSIS Expressions (dynamic SQL strings interpolating TableName/LastETLCutoffTime/TargetETLCutoffTime variables) become Workflow task parameters / job-level base parameters consumed by Python tasks, or Jinja-style templating in Databricks Asset Bundle job definitions.

**Rationale:** SSIS's expression language has no Databricks equivalent; parameterised notebooks/Python tasks are the direct replacement for runtime string construction.

**Objects affected:** 15

### Scheduling

**Rule:** Replace the SQL Server Agent daily job with a Databricks Workflow schedule (cron) on the top-level job, with email/Slack alerting on failure configured via Workflow notification settings.

**Rationale:** Native Workflow scheduling avoids depending on an external scheduler and keeps schedule, task graph, and alerting in one definition.

---

## Per-Entity Job Mapping (Sequence Containers)

| Source Container | Entity | Target Workflow Job | Step Count |
|---|---|---|---|
| SSIS:DailyETLMain:Load City Dimension | City | `wwi_load_city` | 4 |
| SSIS:DailyETLMain:Load Customer Dimension | Customer | `wwi_load_customer` | 4 |
| SSIS:DailyETLMain:Load Employee Dimension | Employee | `wwi_load_employee` | 4 |
| SSIS:DailyETLMain:Load Movement Fact | Movement | `wwi_load_movement` | 9 |
| SSIS:DailyETLMain:Load Order Fact | Order | `wwi_load_order` | 3 |
| SSIS:DailyETLMain:Load Payment Method Dimension | Payment Method | `wwi_load_payment_method` | 3 |
| SSIS:DailyETLMain:Load Purchase Fact | Purchase | `wwi_load_purchase` | 3 |
| SSIS:DailyETLMain:Load Sale Fact | Sale | `wwi_load_sale` | 3 |
| SSIS:DailyETLMain:Load Stock Holding Fact | Stock Holding | `wwi_load_stock_holding` | 2 |
| SSIS:DailyETLMain:Load Stock Item Dimension | Stock Item | `wwi_load_stock_item` | 3 |
| SSIS:DailyETLMain:Load Supplier Dimension | Supplier | `wwi_load_supplier` | 4 |
| SSIS:DailyETLMain:Load Transaction Fact | Transaction | `wwi_load_transaction` | 7 |
| SSIS:DailyETLMain:Load Transaction Type Dimension | Transaction Type | `wwi_load_transaction_type` | 3 |

---

## Summary Counts

| Source SSIS Construct | Count | Target |
|---|---|---|
| Package | 1 | Workflow job |
| Sequence Container | 13 | Per-entity task group / sub-job |
| Execute SQL Task | 53 | SQL task or folded into MERGE task |
| Data Flow Task | 13 | PySpark extract task |
| Expression | 15 | Workflow task parameter |
