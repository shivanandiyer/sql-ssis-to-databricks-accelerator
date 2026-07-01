# Wide World Importers — Target-State Databricks Architecture

> **Accelerator:** WWI SQL Server → Databricks Modernisation Accelerator v0.1.0  
> **Generated:** 2026-06-30 12:34 UTC  
> **Basis:** `inventory.json`, `dependencies.json`, `object_complexity_scores.json`

---

## 0. Architecture Decision

**Chosen architecture: `medallion`** (default).

| Architecture | Fit | Reasoning |
|---|---|---|
| medallion | STRONG | Source DW already implements a 3-tier model (Integration=staging, Dimension=conformed entities, Fact=measures) with SCD2 history and a watermark-driven incremental pattern. This maps almost 1:1 onto Bronze (raw/staging), Silver (conformed/cleansed), Gold (aggregated/serving). |
| data_vault | WEAK | Data Vault (Hub/Link/Satellite) suits environments with many fast-changing source systems and a need for full historised raw integration before any business modelling. This workload has a single OLTP source and an existing, well-formed dimensional model — Data Vault would add modelling overhead (3x more tables, satellite-loading logic) without a corresponding integration benefit. |
| one_big_table | NOT SUITABLE | OBT/wide-table patterns suit single-purpose analytics marts with one dominant query pattern. This workload has 14 dimension/fact targets and a reusable conformed-dimension model serving multiple fact tables — collapsing to OBT would duplicate dimension attributes across facts and break SCD2 history reuse. |

_Override mechanism: Pass architecture_override=<'medallion'|'data_vault'|'one_big_table'> to generate_target_state_design(); recorded here regardless of which value is chosen so the decision is auditable._

---

## 1. Bronze / Silver / Gold Mapping

112 data objects (tables, views, inline TVFs) mapped. Bronze: 72, Silver: 34, Gold: 6. Full per-object mapping is in `medallion_mapping.csv`.

### Sample mapping (first 10 of each layer)

#### BRONZE

| Source | Target FQN | Rationale |
|---|---|---|
| OLTP:Application.DetermineCustomerAccess | wwi_<env>.bronze.application__determinecustomeraccess | Default mapping for OLTP.TVF_INLINE objects based on existing schema-to-layer convention. |
| OLTP:Application.Cities | wwi_<env>.bronze.application__cities | Raw OLTP entity — landed as-is in Bronze via CDC/batch ingestion; no transformation applied at landing time. |
| OLTP:Application.Cities_Archive | wwi_<env>.bronze.application__cities_archive | Raw OLTP entity — landed as-is in Bronze via CDC/batch ingestion; no transformation applied at landing time. |
| OLTP:Application.Countries | wwi_<env>.bronze.application__countries | Raw OLTP entity — landed as-is in Bronze via CDC/batch ingestion; no transformation applied at landing time. |
| OLTP:Application.Countries_Archive | wwi_<env>.bronze.application__countries_archive | Raw OLTP entity — landed as-is in Bronze via CDC/batch ingestion; no transformation applied at landing time. |
| OLTP:Application.DeliveryMethods | wwi_<env>.bronze.application__deliverymethods | Raw OLTP entity — landed as-is in Bronze via CDC/batch ingestion; no transformation applied at landing time. |
| OLTP:Application.DeliveryMethods_Archive | wwi_<env>.bronze.application__deliverymethods_archive | Raw OLTP entity — landed as-is in Bronze via CDC/batch ingestion; no transformation applied at landing time. |
| OLTP:Application.Logs | wwi_<env>.bronze.application__logs | Raw OLTP entity — landed as-is in Bronze via CDC/batch ingestion; no transformation applied at landing time. |
| OLTP:Application.PaymentMethods | wwi_<env>.bronze.application__paymentmethods | Raw OLTP entity — landed as-is in Bronze via CDC/batch ingestion; no transformation applied at landing time. |
| OLTP:Application.PaymentMethods_Archive | wwi_<env>.bronze.application__paymentmethods_archive | Raw OLTP entity — landed as-is in Bronze via CDC/batch ingestion; no transformation applied at landing time. |

#### SILVER

| Source | Target FQN | Rationale |
|---|---|---|
| OLTP:WebApi.BuyingGroups | wwi_<env>.silver.webapi__buyinggroups | Derived/application-facing view over OLTP tables — becomes a Silver view once source tables are landed and conformed. |
| OLTP:WebApi.Cities | wwi_<env>.silver.webapi__cities | Derived/application-facing view over OLTP tables — becomes a Silver view once source tables are landed and conformed. |
| OLTP:WebApi.Colors | wwi_<env>.silver.webapi__colors | Derived/application-facing view over OLTP tables — becomes a Silver view once source tables are landed and conformed. |
| OLTP:WebApi.Countries | wwi_<env>.silver.webapi__countries | Derived/application-facing view over OLTP tables — becomes a Silver view once source tables are landed and conformed. |
| OLTP:WebApi.CustomerCategories | wwi_<env>.silver.webapi__customercategories | Derived/application-facing view over OLTP tables — becomes a Silver view once source tables are landed and conformed. |
| OLTP:WebApi.CustomerTransactions | wwi_<env>.silver.webapi__customertransactions | Derived/application-facing view over OLTP tables — becomes a Silver view once source tables are landed and conformed. |
| OLTP:WebApi.Customers | wwi_<env>.silver.webapi__customers | Derived/application-facing view over OLTP tables — becomes a Silver view once source tables are landed and conformed. |
| OLTP:WebApi.DeliveryMethods | wwi_<env>.silver.webapi__deliverymethods | Derived/application-facing view over OLTP tables — becomes a Silver view once source tables are landed and conformed. |
| OLTP:WebApi.Invoices | wwi_<env>.silver.webapi__invoices | Derived/application-facing view over OLTP tables — becomes a Silver view once source tables are landed and conformed. |
| OLTP:WebApi.PackageTypes | wwi_<env>.silver.webapi__packagetypes | Derived/application-facing view over OLTP tables — becomes a Silver view once source tables are landed and conformed. |

#### GOLD

| Source | Target FQN | Rationale |
|---|---|---|
| DW:Fact.Movement | wwi_<env>.gold.movement | Aggregated/measure-grained table joined against conformed dimensions — Gold serving layer. |
| DW:Fact.Order | wwi_<env>.gold.order | Aggregated/measure-grained table joined against conformed dimensions — Gold serving layer. |
| DW:Fact.Purchase | wwi_<env>.gold.purchase | Aggregated/measure-grained table joined against conformed dimensions — Gold serving layer. |
| DW:Fact.Sale | wwi_<env>.gold.sale | Aggregated/measure-grained table joined against conformed dimensions — Gold serving layer. |
| DW:Fact.Stock | wwi_<env>.gold.stock | Aggregated/measure-grained table joined against conformed dimensions — Gold serving layer. |
| DW:Fact.Transaction | wwi_<env>.gold.transaction | Aggregated/measure-grained table joined against conformed dimensions — Gold serving layer. |

---

## 2. Separation of Concerns

| Concern | Layer / Mechanism | Notes |
|---|---|---|
| Ingestion | Bronze schema, Auto Loader / Lakeflow Connect jobs | One ingestion job per OLTP source table or per SSIS Data Flow equivalent; append-only, partitioned by ingestion_date. |
| Transformation | Silver schema, Delta MERGE (SCD2) + Databricks SQL/PySpark | Conforms, deduplicates, applies SCD2; the only layer where business rules execute. |
| Serving | Gold schema, Delta tables + Databricks SQL views | Fact tables and any pre-aggregated marts; BI/reporting tools connect here only. |
| Orchestration | Databricks Workflows | Owns scheduling, retries, alerting, and task dependency graph — no business logic lives in the orchestration layer itself. |

This mirrors the source's existing Integration/Dimension/Fact separation but makes the ingestion vs transformation boundary explicit, whereas in SSIS both concerns were interleaved within the same package/sequence container.

---

## 3. Unity Catalog Structure

### Catalog Strategy

**Pattern:** One catalog per environment: wwi_dev, wwi_test, wwi_prod

**Rationale:** Unity Catalog catalogs are the natural environment-isolation boundary — permissions, lineage, and audit logs are catalog-scoped, and promoting a table between environments is a deliberate cross-catalog operation rather than a config-flag toggle that could leak dev data into prod.

**Tradeoffs:** Requires duplicating schema/table DDL (via CI/CD, see section 8) across catalogs rather than relying on a single shared catalog with environment tagging; mitigated by Databricks Asset Bundles templating.

**Assumptions:** One Databricks workspace per environment is in scope; if all environments share one workspace, catalogs still provide adequate isolation.

### Schema Strategy

**Pattern:** One schema per medallion layer within each catalog: bronze, silver, gold, plus a non-data schema `ops` for audit/lineage/quality-check metadata tables.

**Rationale:** Schema-per-layer keeps access control simple (e.g. analysts get SELECT on gold only) and matches the mental model already used by the source DW (Integration/Dimension/Fact). It avoids the alternative — schema-per-domain with layer as a table prefix — which would require every consumer role to be granted per-domain rather than per-layer.

**Tradeoffs:** Domain ownership (e.g. 'who owns Sales tables') is less visible at the schema level and must be tracked via table-level tags/comments instead.

**Assumptions:** No regulatory requirement forces physical separation of domains into separate schemas (e.g. PII isolation) — see security note in section 7 if this assumption changes for Sales.Customers / Purchasing.Suppliers.

### Naming Convention

**Pattern:** <catalog>.<layer_schema>.<source_schema>__<entity> for OLTP-origin tables; <catalog>.<layer_schema>.<entity> for DW-origin tables (DW schema is implied by the target layer schema, so it is dropped to avoid redundancy, e.g. Dimension.City -> wwi_prod.silver.city, not silver.dimension__city).

**Rationale:** OLTP tables retain their source schema prefix (e.g. sales__orders) because multiple OLTP schemas can land in the same Bronze schema and name collisions are possible (e.g. Sales vs Purchasing both could have an 'Orders'-like table); DW tables don't need this since Dimension/Fact schemas map 1:1 onto Silver/Gold.

**Tradeoffs:** Asymmetric naming (prefixed vs not) requires a documented rule rather than one universal pattern — mitigated by encoding the rule in this design doc and in the accelerator's conversion templates so it's applied consistently, not left to manual judgement.

**Assumptions:** snake_case is acceptable for all consumers (BI tools, notebooks); if a downstream tool requires the original PascalCase names, expose them via a view layer rather than renaming the managed tables.

---

## 4. File / Layout Strategy

### Gold fact tables

- **Scope:** 6 objects
- **Format:** Delta
- **Partitioning:** PARTITIONED BY (date_key) where a date/period dimension key exists (mirrors the source PS_Date partition scheme)
- **Clustering:** Liquid clustering on the high-cardinality foreign keys used in fact-dimension joins (e.g. City Key, Customer Key, Stock Item Key) instead of legacy Z-ORDER, since fact tables receive ongoing incremental writes and liquid clustering avoids full-table OPTIMIZE rewrites.
- **Rationale:** Matches existing date-partitioned access pattern; liquid clustering is justified here because fact tables are both write-heavy (daily incremental) and read with selective dimension-key filters.
- **Tradeoffs:** Liquid clustering requires Databricks Runtime 13.3+ and is a newer feature with less operational history than Z-ORDER; fallback is Z-ORDER on the same keys.
- **Assumptions:** Fact table growth is append-mostly (matches FACT_LOAD/INCREMENTAL semantics observed in source); if late-arriving updates to historical facts are common, re-validate partition pruning effectiveness.

### Silver dimension tables (SCD2)

- **Scope:** 8 objects
- **Format:** Delta
- **Partitioning:** Not partitioned — dimension tables are small relative to facts (low row counts) and partitioning would create excessive small files.
- **Clustering:** Liquid clustering on the natural/business key (e.g. WWI City ID) to keep MERGE-based SCD2 upserts efficient as the surrogate-key lookup path.
- **Rationale:** SCD2 logic is implemented via MERGE; clustering on the natural key (not the surrogate key) optimises the join condition used to find the 'current' row before inserting a new version.
- **Tradeoffs:** None significant at this table size (~thousands to low millions of rows).
- **Assumptions:** Dimension row counts remain in the thousands-to-low-millions range typical of WWI; if a dimension grows to billions of rows, revisit partitioning by a coarse natural-key hash.

### Bronze staging / landing tables

- **Scope:** 20 objects
- **Format:** Delta
- **Partitioning:** Not partitioned (or partitioned by ingestion_date if retained beyond a single run) — staging tables are truncate-and-load (overwrite) each cycle, matching the source's truncate-then-load pattern.
- **Clustering:** None — transient data, optimised for full-table overwrite write throughput rather than selective read.
- **Rationale:** Preserves the source's deliberate full-refresh-per-cycle semantics; adding partitioning/clustering to a table that's truncated every run adds write overhead with no read-time benefit.
- **Tradeoffs:** If staging tables are later repurposed for audit/replay (keeping history instead of overwriting), partitioning by ingestion_date should be revisited.
- **Assumptions:** Staging tables are not relied upon as a system-of-record after the downstream Silver/Gold write succeeds.

### Bronze raw OLTP landing tables

- **Scope:** all OLTP-origin TABLE objects not already covered above
- **Format:** Delta, ingested via Auto Loader (cloudFiles) or Lakeflow Connect/JDBC batch read
- **Partitioning:** PARTITIONED BY (ingestion_date) to support efficient time-bounded reprocessing and to bound small-file growth from incremental ingestion.
- **Clustering:** None by default; add liquid clustering on the natural key only for tables feeding the geography-bearing dimensions (see manual_intervention_list.md) where downstream joins are frequent.
- **Rationale:** Bronze should be an immutable, append-only history of what was received, partitioned for incremental processing rather than business-key access.
- **Tradeoffs:** Date partitioning on Bronze plus natural-key clustering downstream in Silver means the same data is laid out two different ways across layers — by design, since Bronze and Silver serve different access patterns.
- **Assumptions:** Source system can supply a reliable last-modified or CDC timestamp; if not, ingestion_date defaults to job run date, which weakens point-in-time reprocessing.

---

## 5. Orchestration Mapping

Full detail in `orchestration_design.md`. Summary:

- Each SSIS package -> one Databricks Workflow job
- Each Sequence Container (13 total) -> one parameterised per-entity job/task group
- The 5-step per-entity pattern collapses to 3 Workflow tasks (extract, MERGE+lineage, watermark advance)
- Precedence constraints -> Workflow `depends_on` / `run_if`
- SSIS Expressions -> Workflow task parameters

---

## 6. Code Mapping (T-SQL -> Databricks SQL / PySpark)

**Rule:** Target language follows object type first, then conversion classification: set-based, declarative objects (tables, views, simple procs/functions) target Databricks SQL; objects whose source logic is row-by-row, dynamic, or otherwise procedural (cursors, dynamic SQL, SSIS data flows) target PySpark.

**Rationale:** Databricks SQL gives the shortest path to a maintainable, SQL-literate-friendly target for anything that was already declarative T-SQL, preserving the skill set of the existing SQL-focused team. PySpark is reserved for cases where T-SQL's procedural escape hatches (CURSOR, sp_executesql, WHILE loops) have no direct SQL equivalent and must become explicit DataFrame/Python logic.

**Tradeoffs:** Splitting the codebase across two languages means two skill sets are needed on the migration team; mitigated by keeping the PySpark surface area as small as possible (only the ~49 rewrite-required + 81 manual-redesign objects from the impact analysis, not the full 419).

**Assumptions:** Databricks SQL stored procedures (DBR 14.1+) are available in the target workspace; if running on an older runtime, all PROCEDURE objects default to PySpark/Python tasks instead.

### Distribution

| Target | Object Count |
|---|---|
| PySpark (notebook / Python task) — procedural logic exceeds SQL-only conversion | 87 |
| Delta DDL (Databricks SQL) | 84 |
| Databricks Workflows task definition (orchestration, not data-processing code) | 82 |
| Databricks SQL (stored procedure / SQL UDF, DBR 14.1+) or a parameterised SQL task | 80 |
| Delta identity column (GENERATED ALWAYS AS IDENTITY) or a small counter table | 34 |
| Databricks SQL (view / CTAS) | 28 |
| Case-by-case review | 23 |
| PySpark (Auto Loader / DataFrame transform / Delta write) | 13 |

---

## 7. Observability

### Audit Logging

**Recommendation:** Enable Unity Catalog audit logging (system.access.audit) for all catalogs; replace the source `Integration.Lineage` table with the native Workflow job-run history plus a thin `ops.load_audit` Delta table recording entity, watermark range, row counts in/out, and job run ID for each load.

**Rationale:** Unity Catalog audit logs cover who-accessed-what; they don't capture business-level load metadata (rows processed, watermark advanced), so a purpose-built audit table is still needed alongside the platform's logs.

**Tradeoffs:** One more table to maintain, but far lighter weight than the source `Integration.Lineage` table since job-run ID and timestamps are populated automatically by the Workflow runtime via task parameters.

### Lineage

**Recommendation:** Rely on Unity Catalog's automatic column- and table-level lineage (captured for any read/write through Spark/Databricks SQL) rather than hand-building a lineage system; surface it via the Catalog Explorer lineage graph for impact analysis on future schema changes.

**Rationale:** Automatic lineage requires zero additional code and directly answers the kind of dependency questions this accelerator currently answers via static analysis (dependencies.json) — once migrated, that capability is native.

**Tradeoffs:** Automatic lineage only covers Databricks-native reads/writes; any external tool reading Delta tables directly (e.g. via JDBC from a BI tool) won't appear unless it goes through Unity Catalog's audited path.

### Data Quality

**Recommendation:** Implement quality checks as Delta Live Tables expectations or Lakehouse Monitoring profiles on Silver/Gold tables: not-null and uniqueness checks on natural/surrogate keys, referential checks that every fact's dimension keys resolve, and freshness checks against the watermark table.

**Rationale:** 93 SCD2 dimensions and 124 incrementally-loaded objects are exactly the cases where a silent join failure or stale watermark would otherwise go unnoticed until a downstream report looks wrong.

**Tradeoffs:** DLT expectations require adopting the DLT framework for at least the tables they protect; if the team prefers plain Workflows + notebooks, Lakehouse Monitoring or a custom Great Expectations suite achieves the same checks with more setup code.

---

## 8. CI/CD & Environment Promotion

**Tooling:** Databricks Asset Bundles (DAB) for all Workflow job definitions, DDL, and notebook/Python source; standard git-based CI (GitHub Actions or Azure DevOps, matching whichever the team already uses for the SSDT projects today).

**Rationale:** DAB gives a single declarative artifact (databricks.yml) covering jobs, schemas, and permissions per environment — directly analogous to how the .sqlproj/.dtproj files already declare this solution's structure today, so the team's existing 'infrastructure as project file' mental model carries over.

**Promotion pattern:** dev -> test -> prod, one DAB target per environment mapping to the corresponding wwi_dev / wwi_test / wwi_prod catalog.

**Promotion gate:** Merge to main triggers deploy to test; a tagged release triggers deploy to prod after the test pack (see Step 7 of this accelerator) passes against the test catalog.

**Branching:** Trunk-based development with short-lived feature branches per object/entity conversion, mirroring the per-entity scoping already visible in the source SSIS sequence containers.

**Rollback:** Because all schema/job definitions are declarative (DAB) and data writes are Delta (versioned), rollback is two-part: redeploy the previous DAB bundle version, and use Delta `RESTORE TABLE ... TO VERSION AS OF` for any table whose data must also revert.

**Tradeoffs:** DAB is the Databricks-native choice but ties CI/CD tooling to the Databricks CLI; teams already standardised on Terraform for all cloud resources may prefer the Databricks Terraform provider instead for consistency, at the cost of slightly more verbose job/schema definitions.

**Assumptions:** A separate test pack (Step 7 of this accelerator) will provide the automated validation gate referenced above; until that exists, promotion to prod should remain a manual approval step.

---

_This document proposes design only — no code or deployable assets are generated yet. See Step 6 (conversion) for implementation._