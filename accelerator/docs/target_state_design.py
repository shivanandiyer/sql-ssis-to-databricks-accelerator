"""
target_state_design.py
Proposes a target-state Databricks design for the WWI workload.

Consumes:
    outputs/inventory.json
    outputs/dependencies.json
    outputs/object_complexity_scores.json

Produces:
    target_state_architecture.md
    target_state_mappings.json
    medallion_mapping.csv
    orchestration_design.md

Default architecture: medallion (Bronze/Silver/Gold). Callers may pass
architecture_override="medallion" (default) to force/confirm the choice;
the module always documents why an alternative was or wasn't chosen.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ENV_NAMES = ["dev", "test", "prod"]


def _slug(text: str) -> str:
    text = re.sub(r"[^\w]+", "_", text.strip())
    text = re.sub(r"_+", "_", text).strip("_")
    return text.lower()


def _md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return lines


# ---------------------------------------------------------------------------
# 0. Architecture decision
# ---------------------------------------------------------------------------

def decide_architecture(inventory: dict[str, Any], override: str | None) -> dict[str, Any]:
    objects = inventory.get("objects", [])
    has_scd2 = any("SCD2" in o.get("etl_semantics", []) for o in objects)
    has_facts_dims = any(o.get("medallion_layer") == "GOLD" for o in objects) and \
                      any(o.get("medallion_layer") == "SILVER" for o in objects)
    has_clear_staging = any("STAGING_TO_DW" in o.get("etl_semantics", []) for o in objects)

    evaluated = {
        "medallion": {
            "fit": "STRONG",
            "reason": "Source DW already implements a 3-tier model (Integration=staging, "
                      "Dimension=conformed entities, Fact=measures) with SCD2 history and a "
                      "watermark-driven incremental pattern. This maps almost 1:1 onto "
                      "Bronze (raw/staging), Silver (conformed/cleansed), Gold (aggregated/serving).",
        },
        "data_vault": {
            "fit": "WEAK",
            "reason": "Data Vault (Hub/Link/Satellite) suits environments with many fast-changing "
                      "source systems and a need for full historised raw integration before any "
                      "business modelling. This workload has a single OLTP source and an existing, "
                      "well-formed dimensional model — Data Vault would add modelling overhead "
                      "(3x more tables, satellite-loading logic) without a corresponding integration benefit.",
        },
        "one_big_table": {
            "fit": "NOT SUITABLE",
            "reason": "OBT/wide-table patterns suit single-purpose analytics marts with one dominant "
                      "query pattern. This workload has 14 dimension/fact targets and a reusable "
                      "conformed-dimension model serving multiple fact tables — collapsing to OBT "
                      "would duplicate dimension attributes across facts and break SCD2 history reuse.",
        },
    }

    chosen = override or "medallion"
    decision = {
        "chosen_architecture": chosen,
        "is_default": chosen == "medallion",
        "evaluated_alternatives": evaluated,
        "signals_observed": {
            "has_scd2_dimensions": has_scd2,
            "has_conformed_dimension_fact_model": has_facts_dims,
            "has_staging_layer": has_clear_staging,
        },
        "override_mechanism": "Pass architecture_override=<'medallion'|'data_vault'|'one_big_table'> "
                               "to generate_target_state_design(); recorded here regardless of which "
                               "value is chosen so the decision is auditable.",
    }
    return decision


# ---------------------------------------------------------------------------
# 1. Medallion / layer mapping
# ---------------------------------------------------------------------------

_LAYER_RATIONALE: dict[tuple[Any, ...], str] = {
    ("OLTP", "TABLE"): "Raw OLTP entity — landed as-is in Bronze via CDC/batch ingestion; no transformation applied at landing time.",
    ("DW", "TABLE", "Integration"): "Existing staging table — Bronze landing zone for the per-entity incremental extract, truncate-and-load preserved as overwrite-mode Delta write.",
    ("DW", "TABLE", "Dimension"): "Conformed, deduplicated, SCD2-tracked business entity — Silver layer by definition.",
    ("DW", "TABLE", "Fact"): "Aggregated/measure-grained table joined against conformed dimensions — Gold serving layer.",
    ("OLTP", "VIEW"): "Derived/application-facing view over OLTP tables — becomes a Silver view once source tables are landed and conformed.",
    ("DW", "VIEW"): "Derived view over DW objects — Gold (serving) since it composes already-conformed Silver/Gold tables.",
}


def _layer_for(obj: dict[str, Any]) -> str:
    layer = obj.get("medallion_layer")
    return layer if layer in ("BRONZE", "SILVER", "GOLD") else "BRONZE"


def _rationale_for(obj: dict[str, Any]) -> str:
    proj = obj.get("source_project")
    otype = obj.get("object_type")
    schema = obj.get("schema", "")
    key3 = (proj, otype, schema)
    if key3 in _LAYER_RATIONALE:
        return _LAYER_RATIONALE[key3]
    key2 = (proj, otype)
    if key2 in _LAYER_RATIONALE:
        return _LAYER_RATIONALE[key2]
    return f"Default mapping for {proj}.{otype} objects based on existing schema-to-layer convention."


def _target_table_name(obj: dict[str, Any]) -> str:
    schema_slug = _slug(obj.get("schema", "default"))
    name_slug = _slug(obj.get("name", "unknown"))
    proj = obj.get("source_project", "")
    if proj == "OLTP":
        return f"{schema_slug}__{name_slug}"
    return name_slug


def build_medallion_mapping(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    objects = inventory.get("objects", [])
    rows: list[dict[str, Any]] = []
    for obj in objects:
        if obj.get("object_type") not in ("TABLE", "VIEW", "TVF_INLINE", "TVF_MULTI"):
            continue
        layer = _layer_for(obj)
        schema_name = layer.lower()
        table_name = _target_table_name(obj)
        rows.append({
            "source_id": obj["id"],
            "source_project": obj.get("source_project"),
            "source_schema": obj.get("schema"),
            "source_object_type": obj.get("object_type"),
            "target_catalog": "wwi_<env>",
            "target_schema": schema_name,
            "target_table": table_name,
            "target_fqn": f"wwi_<env>.{schema_name}.{table_name}",
            "layer": layer,
            "layer_subcategory": obj.get("layer_subcategory"),
            "rationale": _rationale_for(obj),
            "table_features": obj.get("table_features", []),
            "etl_semantics": obj.get("etl_semantics", []),
        })

    # Hard collision guard: the naming convention (DW objects drop their
    # schema prefix, OLTP objects keep it) is only collision-free as long as
    # no two source objects ever resolve to the same target_fqn. Found by
    # adversarial review to be unguarded — verified no active collision
    # exists today, but a silent merge of two unrelated objects into one
    # target table on a future regeneration would be a serious, hard-to-spot
    # data-correctness bug. Fail loudly instead.
    seen_fqn: dict[str, str] = {}
    collisions: list[tuple[str, str, str]] = []
    for row in rows:
        fqn = row["target_fqn"]
        if fqn in seen_fqn:
            collisions.append((fqn, seen_fqn[fqn], row["source_id"]))
        else:
            seen_fqn[fqn] = row["source_id"]
    if collisions:
        details = "; ".join(f"{fqn}: {a} vs {b}" for fqn, a, b in collisions)
        raise ValueError(
            f"Unity Catalog naming collision(s) detected in medallion mapping — two or more source "
            f"objects would resolve to the same target_fqn, which would silently merge unrelated "
            f"objects into one target table: {details}"
        )
    return rows


# ---------------------------------------------------------------------------
# 2. Unity Catalog structure
# ---------------------------------------------------------------------------

def build_unity_catalog_design() -> dict[str, Any]:
    return {
        "catalog_strategy": {
            "pattern": "One catalog per environment: wwi_dev, wwi_test, wwi_prod",
            "rationale": "Unity Catalog catalogs are the natural environment-isolation boundary — "
                         "permissions, lineage, and audit logs are catalog-scoped, and promoting a "
                         "table between environments is a deliberate cross-catalog operation rather "
                         "than a config-flag toggle that could leak dev data into prod.",
            "tradeoffs": "Requires duplicating schema/table DDL (via CI/CD, see section 8) across "
                         "catalogs rather than relying on a single shared catalog with environment "
                         "tagging; mitigated by Databricks Asset Bundles templating.",
            "assumptions": "One Databricks workspace per environment is in scope; if all environments "
                           "share one workspace, catalogs still provide adequate isolation.",
        },
        "schema_strategy": {
            "pattern": "One schema per medallion layer within each catalog: bronze, silver, gold, "
                       "plus a non-data schema `ops` for audit/lineage/quality-check metadata tables.",
            "rationale": "Schema-per-layer keeps access control simple (e.g. analysts get SELECT on "
                         "gold only) and matches the mental model already used by the source DW "
                         "(Integration/Dimension/Fact). It avoids the alternative — schema-per-domain "
                         "with layer as a table prefix — which would require every consumer role to "
                         "be granted per-domain rather than per-layer.",
            "tradeoffs": "Domain ownership (e.g. 'who owns Sales tables') is less visible at the "
                         "schema level and must be tracked via table-level tags/comments instead.",
            "assumptions": "No regulatory requirement forces physical separation of domains into "
                           "separate schemas (e.g. PII isolation) — see security note in section 7 "
                           "if this assumption changes for Sales.Customers / Purchasing.Suppliers.",
        },
        "naming_convention": {
            "pattern": "<catalog>.<layer_schema>.<source_schema>__<entity> for OLTP-origin tables; "
                       "<catalog>.<layer_schema>.<entity> for DW-origin tables (DW schema is implied "
                       "by the target layer schema, so it is dropped to avoid redundancy, e.g. "
                       "Dimension.City -> wwi_prod.silver.city, not silver.dimension__city).",
            "rationale": "OLTP tables retain their source schema prefix (e.g. sales__orders) because "
                         "multiple OLTP schemas can land in the same Bronze schema and name collisions "
                         "are possible (e.g. Sales vs Purchasing both could have an 'Orders'-like table); "
                         "DW tables don't need this since Dimension/Fact schemas map 1:1 onto Silver/Gold.",
            "tradeoffs": "Asymmetric naming (prefixed vs not) requires a documented rule rather than "
                         "one universal pattern — mitigated by encoding the rule in this design doc and "
                         "in the accelerator's conversion templates so it's applied consistently, not "
                         "left to manual judgement.",
            "assumptions": "snake_case is acceptable for all consumers (BI tools, notebooks); if a "
                           "downstream tool requires the original PascalCase names, expose them via a "
                           "view layer rather than renaming the managed tables.",
        },
        "environments": ENV_NAMES,
    }


# ---------------------------------------------------------------------------
# 3. File layout / Delta strategy
# ---------------------------------------------------------------------------

def build_file_layout_recommendations(inventory: dict[str, Any]) -> list[dict[str, Any]]:
    objects = inventory.get("objects", [])
    recs: list[dict[str, Any]] = []

    fact_tables = [o for o in objects if o.get("medallion_layer") == "GOLD" and o.get("object_type") == "TABLE"]
    dim_tables = [o for o in objects if o.get("medallion_layer") == "SILVER" and o.get("object_type") == "TABLE"]
    staging_tables = [o for o in objects if "Staging" in (o.get("name") or "") or "STAGING_TO_DW" in o.get("etl_semantics", [])]

    recs.append({
        "target_class": "Gold fact tables",
        "objects": [o["id"] for o in fact_tables],
        "file_format": "Delta",
        "partitioning": "PARTITIONED BY (date_key) where a date/period dimension key exists "
                         "(mirrors the source PS_Date partition scheme)",
        "clustering": "Liquid clustering on the high-cardinality foreign keys used in fact-dimension "
                       "joins (e.g. City Key, Customer Key, Stock Item Key) instead of legacy "
                       "Z-ORDER, since fact tables receive ongoing incremental writes and liquid "
                       "clustering avoids full-table OPTIMIZE rewrites.",
        "rationale": "Matches existing date-partitioned access pattern; liquid clustering is "
                     "justified here because fact tables are both write-heavy (daily incremental) "
                     "and read with selective dimension-key filters.",
        "tradeoffs": "Liquid clustering requires Databricks Runtime 13.3+ and is a newer feature "
                     "with less operational history than Z-ORDER; fallback is Z-ORDER on the same keys.",
        "assumptions": "Fact table growth is append-mostly (matches FACT_LOAD/INCREMENTAL semantics "
                       "observed in source); if late-arriving updates to historical facts are common, "
                       "re-validate partition pruning effectiveness.",
    })
    recs.append({
        "target_class": "Silver dimension tables (SCD2)",
        "objects": [o["id"] for o in dim_tables],
        "file_format": "Delta",
        "partitioning": "Not partitioned — dimension tables are small relative to facts (low row "
                         "counts) and partitioning would create excessive small files.",
        "clustering": "Liquid clustering on the natural/business key (e.g. WWI City ID) to keep "
                       "MERGE-based SCD2 upserts efficient as the surrogate-key lookup path.",
        "rationale": "SCD2 logic is implemented via MERGE; clustering on the natural key (not the "
                      "surrogate key) optimises the join condition used to find the 'current' row "
                      "before inserting a new version.",
        "tradeoffs": "None significant at this table size (~thousands to low millions of rows).",
        "assumptions": "Dimension row counts remain in the thousands-to-low-millions range typical "
                       "of WWI; if a dimension grows to billions of rows, revisit partitioning by a "
                       "coarse natural-key hash.",
    })
    recs.append({
        "target_class": "Bronze staging / landing tables",
        "objects": [o["id"] for o in staging_tables][:20],
        "file_format": "Delta",
        "partitioning": "Not partitioned (or partitioned by ingestion_date if retained beyond a "
                         "single run) — staging tables are truncate-and-load (overwrite) each cycle, "
                         "matching the source's truncate-then-load pattern.",
        "clustering": "None — transient data, optimised for full-table overwrite write throughput "
                       "rather than selective read.",
        "rationale": "Preserves the source's deliberate full-refresh-per-cycle semantics; adding "
                     "partitioning/clustering to a table that's truncated every run adds write "
                     "overhead with no read-time benefit.",
        "tradeoffs": "If staging tables are later repurposed for audit/replay (keeping history "
                     "instead of overwriting), partitioning by ingestion_date should be revisited.",
        "assumptions": "Staging tables are not relied upon as a system-of-record after the "
                       "downstream Silver/Gold write succeeds.",
    })
    recs.append({
        "target_class": "Bronze raw OLTP landing tables",
        "objects": "all OLTP-origin TABLE objects not already covered above",
        "file_format": "Delta, ingested via Auto Loader (cloudFiles) or Lakeflow Connect/JDBC batch read",
        "partitioning": "PARTITIONED BY (ingestion_date) to support efficient time-bounded "
                         "reprocessing and to bound small-file growth from incremental ingestion.",
        "clustering": "None by default; add liquid clustering on the natural key only for tables "
                       "feeding the geography-bearing dimensions (see manual_intervention_list.md) "
                       "where downstream joins are frequent.",
        "rationale": "Bronze should be an immutable, append-only history of what was received, "
                     "partitioned for incremental processing rather than business-key access.",
        "tradeoffs": "Date partitioning on Bronze plus natural-key clustering downstream in Silver "
                     "means the same data is laid out two different ways across layers — by design, "
                     "since Bronze and Silver serve different access patterns.",
        "assumptions": "Source system can supply a reliable last-modified or CDC timestamp; if not, "
                       "ingestion_date defaults to job run date, which weakens point-in-time reprocessing.",
    })
    return recs


# ---------------------------------------------------------------------------
# 4. Orchestration mapping (SSIS -> Databricks Workflows)
# ---------------------------------------------------------------------------

def build_orchestration_mapping(inventory: dict[str, Any]) -> dict[str, Any]:
    objects = inventory.get("objects", [])
    packages = [o for o in objects if o.get("object_type") == "SSIS_PACKAGE"]
    containers = [o for o in objects if o.get("object_type") == "SSIS_SEQUENCE_CONTAINER"]
    exec_sql = [o for o in objects if o.get("object_type") == "SSIS_EXECUTE_SQL"]
    data_flows = [o for o in objects if o.get("object_type") == "SSIS_DATA_FLOW"]
    expressions = [o for o in objects if o.get("object_type") == "SSIS_EXPRESSION"]

    container_tasks: list[dict[str, Any]] = []
    for c in sorted(containers, key=lambda o: o.get("name", "")):
        entity = re.sub(r"^Load\s+|\s+(Dimension|Fact)$", "", c.get("name", ""), flags=re.IGNORECASE)
        children = [
            o for o in objects
            if o.get("parent_package") == c.get("parent_package")
            and o.get("object_type") in ("SSIS_EXECUTE_SQL", "SSIS_DATA_FLOW")
            and entity.lower() in (o.get("name") or "").lower()
        ]
        container_tasks.append({
            "source_container": c["id"],
            "entity": entity,
            "target_databricks_workflow_job": f"wwi_load_{_slug(entity)}",
            "step_count": len(children),
            "steps": [ch.get("name") for ch in children],
        })

    return {
        "package_to_job": {
            "rule": "Each SSIS package becomes one Databricks Workflow (multi-task job).",
            "example": f"{packages[0]['name'] if packages else 'DailyETLMain'} -> Workflow job `wwi_daily_etl_main`",
            "rationale": "Preserves the existing single-pipeline mental model and keeps the job's "
                         "run history, alerting, and SLA configuration in one place.",
        },
        "sequence_container_to_task_group": {
            "rule": "Each Sequence Container becomes either a Workflow task group (if-all-success "
                    "dependency chain) or, preferably, its own job-as-task referenced from the parent "
                    "job — one per entity (City, Customer, Date, Employee, Payment, StockItem, "
                    "Supplier, Transaction, Movement, Order, Purchase, Sale, Stock).",
            "rationale": "Per-entity isolation means a failure loading one dimension doesn't block "
                         "unrelated dimensions from completing, and lets entity loads run in parallel "
                         "where the dependency graph allows it (see ordering note below) instead of "
                         "SSIS's single-threaded sequential container execution.",
            "tradeoffs": "Increases the number of Workflow task definitions to maintain (13 vs 1); "
                         "mitigated by generating them from a single parameterised job template "
                         "(entity name as a job parameter) rather than hand-authoring 13 jobs.",
            "mapped_entities": container_tasks,
        },
        "five_step_pattern_to_tasks": {
            "rule": "The recurring 5-step pattern (Get Cutoff -> Truncate Staging -> Extract -> Get "
                    "Lineage Key -> Migrate) becomes 3 Workflow tasks, not 5: (1) a PySpark/SQL task "
                    "that reads the watermark and extracts incrementally in one step (Auto Loader or "
                    "a parameterised SQL read replaces the separate truncate+extract steps because "
                    "Delta overwrite mode makes the explicit TRUNCATE redundant), (2) a MERGE task "
                    "that applies SCD2 logic and lineage-key assignment together, (3) a watermark-"
                    "update task that advances the cutoff only after step 2 succeeds.",
            "rationale": "Several SSIS steps exist to work around SQL Server's lack of atomic "
                         "upsert-with-history; Delta's MERGE INTO with SCD2 expressions collapses "
                         "those steps. Fewer tasks means fewer points of partial failure to reason "
                         "about during cutover.",
            "tradeoffs": "Less granular task-level retry (a failure anywhere in the combined extract "
                         "step reprocesses the whole step) — acceptable because the step is now "
                         "idempotent (Delta overwrite/MERGE), unlike the original truncate-then-load "
                         "sequence which was not safe to blindly retry mid-sequence.",
            "watermark_design": "Replace the `Integration.ETL Cutoff` SQL table with a small Delta "
                                 "table `wwi_<env>.ops.etl_watermark(entity, last_cutoff_ts)`, read "
                                 "and updated via the same MERGE transaction pattern as the data load "
                                 "to guarantee watermark advancement is atomic with the data write.",
        },
        "precedence_constraints_to_dependencies": {
            "rule": "SSIS precedence constraints (Success/Failure/Completion) map directly to "
                    "Databricks Workflow task `depends_on` with `run_if` conditions "
                    "(ALL_SUCCESS / ALL_FAILED / ALL_DONE).",
            "rationale": "1:1 semantic equivalent exists in Workflows — no redesign needed here.",
        },
        "expressions_to_parameters": {
            "rule": "The 15 SSIS Expressions (dynamic SQL strings interpolating "
                    "TableName/LastETLCutoffTime/TargetETLCutoffTime variables) become Workflow "
                    "task parameters / job-level base parameters consumed by Python tasks, or Jinja-"
                    "style templating in Databricks Asset Bundle job definitions.",
            "rationale": "SSIS's expression language has no Databricks equivalent; parameterised "
                         "notebooks/Python tasks are the direct replacement for runtime string "
                         "construction.",
            "count_affected": len(expressions),
        },
        "scheduling": {
            "rule": "Replace the SQL Server Agent daily job with a Databricks Workflow schedule "
                    "(cron) on the top-level job, with email/Slack alerting on failure configured "
                    "via Workflow notification settings.",
            "rationale": "Native Workflow scheduling avoids depending on an external scheduler and "
                         "keeps schedule, task graph, and alerting in one definition.",
        },
        "summary_counts": {
            "packages": len(packages),
            "sequence_containers": len(containers),
            "execute_sql_tasks": len(exec_sql),
            "data_flow_tasks": len(data_flows),
            "expressions": len(expressions),
        },
    }


# ---------------------------------------------------------------------------
# 5. Code mapping (T-SQL -> Databricks SQL / PySpark)
# ---------------------------------------------------------------------------

def build_code_mapping(complexity_scores: dict[str, Any]) -> dict[str, Any]:
    objs = complexity_scores.get("objects", [])

    def target_for(o: dict[str, Any]) -> str:
        otype = o.get("object_type") or ""
        cls = o.get("classification")
        if otype in ("VIEW", "TVF_INLINE", "TVF_MULTI"):
            return "Databricks SQL (view / CTAS)"
        if otype == "SEQUENCE":
            return "Delta identity column (GENERATED ALWAYS AS IDENTITY) or a small counter table"
        if otype in ("TABLE",):
            return "Delta DDL (Databricks SQL)"
        if otype in ("PROCEDURE", "SCALAR_FUNCTION"):
            if cls in ("LIFT_AND_SHIFT", "PARTIAL_AUTOMATION"):
                return "Databricks SQL (stored procedure / SQL UDF, DBR 14.1+) or a parameterised SQL task"
            return "PySpark (notebook / Python task) — procedural logic exceeds SQL-only conversion"
        if otype == "SSIS_DATA_FLOW":
            return "PySpark (Auto Loader / DataFrame transform / Delta write)"
        if otype.startswith("SSIS_"):
            return "Databricks Workflows task definition (orchestration, not data-processing code)"
        return "Case-by-case review"

    mapping_counts: dict[str, int] = {}
    examples: dict[str, list[str]] = {}
    for o in objs:
        target = target_for(o)
        mapping_counts[target] = mapping_counts.get(target, 0) + 1
        examples.setdefault(target, [])
        if len(examples[target]) < 5:
            examples[target].append(o["id"])

    return {
        "rule": "Target language follows object type first, then conversion classification: "
                "set-based, declarative objects (tables, views, simple procs/functions) target "
                "Databricks SQL; objects whose source logic is row-by-row, dynamic, or otherwise "
                "procedural (cursors, dynamic SQL, SSIS data flows) target PySpark.",
        "rationale": "Databricks SQL gives the shortest path to a maintainable, SQL-literate-"
                     "friendly target for anything that was already declarative T-SQL, preserving "
                     "the skill set of the existing SQL-focused team. PySpark is reserved for cases "
                     "where T-SQL's procedural escape hatches (CURSOR, sp_executesql, WHILE loops) "
                     "have no direct SQL equivalent and must become explicit DataFrame/Python logic.",
        "tradeoffs": "Splitting the codebase across two languages means two skill sets are needed "
                     "on the migration team; mitigated by keeping the PySpark surface area as small "
                     "as possible (only the ~49 rewrite-required + 81 manual-redesign objects from "
                     "the impact analysis, not the full 419).",
        "assumptions": "Databricks SQL stored procedures (DBR 14.1+) are available in the target "
                       "workspace; if running on an older runtime, all PROCEDURE objects default to "
                       "PySpark/Python tasks instead.",
        "distribution": mapping_counts,
        "examples": examples,
    }


# ---------------------------------------------------------------------------
# 6. Observability
# ---------------------------------------------------------------------------

def build_observability_design(inventory: dict[str, Any]) -> dict[str, Any]:
    objects = inventory.get("objects", [])
    scd2_count = sum(1 for o in objects if "SCD2" in o.get("etl_semantics", []))
    incremental_count = sum(1 for o in objects if "INCREMENTAL" in o.get("etl_semantics", []))

    return {
        "audit_logging": {
            "recommendation": "Enable Unity Catalog audit logging (system.access.audit) for all "
                               "catalogs; replace the source `Integration.Lineage` table with the "
                               "native Workflow job-run history plus a thin `ops.load_audit` Delta "
                               "table recording entity, watermark range, row counts in/out, and "
                               "job run ID for each load.",
            "rationale": "Unity Catalog audit logs cover who-accessed-what; they don't capture "
                         "business-level load metadata (rows processed, watermark advanced), so a "
                         "purpose-built audit table is still needed alongside the platform's logs.",
            "tradeoffs": "One more table to maintain, but far lighter weight than the source "
                         "`Integration.Lineage` table since job-run ID and timestamps are populated "
                         "automatically by the Workflow runtime via task parameters.",
        },
        "lineage": {
            "recommendation": "Rely on Unity Catalog's automatic column- and table-level lineage "
                               "(captured for any read/write through Spark/Databricks SQL) rather "
                               "than hand-building a lineage system; surface it via the Catalog "
                               "Explorer lineage graph for impact analysis on future schema changes.",
            "rationale": "Automatic lineage requires zero additional code and directly answers the "
                         "kind of dependency questions this accelerator currently answers via static "
                         "analysis (dependencies.json) — once migrated, that capability is native.",
            "tradeoffs": "Automatic lineage only covers Databricks-native reads/writes; any external "
                         "tool reading Delta tables directly (e.g. via JDBC from a BI tool) won't "
                         "appear unless it goes through Unity Catalog's audited path.",
        },
        "data_quality": {
            "recommendation": "Implement quality checks as Delta Live Tables expectations or "
                               "Lakehouse Monitoring profiles on Silver/Gold tables: not-null and "
                               "uniqueness checks on natural/surrogate keys, referential checks that "
                               "every fact's dimension keys resolve, and freshness checks against "
                               "the watermark table.",
            "rationale": f"{scd2_count} SCD2 dimensions and {incremental_count} incrementally-loaded "
                         "objects are exactly the cases where a silent join failure or stale "
                         "watermark would otherwise go unnoticed until a downstream report looks wrong.",
            "tradeoffs": "DLT expectations require adopting the DLT framework for at least the "
                         "tables they protect; if the team prefers plain Workflows + notebooks, "
                         "Lakehouse Monitoring or a custom Great Expectations suite achieves the same "
                         "checks with more setup code.",
        },
    }


# ---------------------------------------------------------------------------
# 7. CI/CD and environment promotion
# ---------------------------------------------------------------------------

def build_cicd_design() -> dict[str, Any]:
    return {
        "tooling": "Databricks Asset Bundles (DAB) for all Workflow job definitions, DDL, and "
                   "notebook/Python source; standard git-based CI (GitHub Actions or Azure DevOps, "
                   "matching whichever the team already uses for the SSDT projects today).",
        "rationale": "DAB gives a single declarative artifact (databricks.yml) covering jobs, "
                     "schemas, and permissions per environment — directly analogous to how the "
                     ".sqlproj/.dtproj files already declare this solution's structure today, so "
                     "the team's existing 'infrastructure as project file' mental model carries over.",
        "environment_promotion": {
            "pattern": "dev -> test -> prod, one DAB target per environment mapping to the "
                       "corresponding wwi_dev / wwi_test / wwi_prod catalog.",
            "promotion_gate": "Merge to main triggers deploy to test; a tagged release triggers "
                               "deploy to prod after the test pack (see Step 7 of this accelerator) "
                               "passes against the test catalog.",
        },
        "branching": "Trunk-based development with short-lived feature branches per object/entity "
                     "conversion, mirroring the per-entity scoping already visible in the source "
                     "SSIS sequence containers.",
        "rollback": "Because all schema/job definitions are declarative (DAB) and data writes are "
                    "Delta (versioned), rollback is two-part: redeploy the previous DAB bundle "
                    "version, and use Delta `RESTORE TABLE ... TO VERSION AS OF` for any table whose "
                    "data must also revert.",
        "tradeoffs": "DAB is the Databricks-native choice but ties CI/CD tooling to the Databricks "
                     "CLI; teams already standardised on Terraform for all cloud resources may "
                     "prefer the Databricks Terraform provider instead for consistency, at the cost "
                     "of slightly more verbose job/schema definitions.",
        "assumptions": "A separate test pack (Step 7 of this accelerator) will provide the "
                       "automated validation gate referenced above; until that exists, promotion "
                       "to prod should remain a manual approval step.",
    }


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def _write_medallion_csv(rows: list[dict[str, Any]], output_dir: Path) -> Path:
    path = output_dir / "medallion_mapping.csv"
    headers = ["source_id", "source_project", "source_schema", "source_object_type",
               "target_catalog", "target_schema", "target_table", "target_fqn",
               "layer", "layer_subcategory", "rationale"]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in rows:
            writer.writerow([r[h] for h in headers])
    return path


def _write_mappings_json(
    architecture_decision: dict[str, Any],
    medallion_rows: list[dict[str, Any]],
    uc_design: dict[str, Any],
    file_layout: list[dict[str, Any]],
    orchestration: dict[str, Any],
    code_mapping: dict[str, Any],
    observability: dict[str, Any],
    cicd: dict[str, Any],
    output_dir: Path,
) -> Path:
    path = output_dir / "target_state_mappings.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "architecture_decision": architecture_decision,
        "medallion_mapping_count": len(medallion_rows),
        "medallion_layer_distribution": {
            layer: sum(1 for r in medallion_rows if r["layer"] == layer)
            for layer in ("BRONZE", "SILVER", "GOLD")
        },
        "unity_catalog_design": uc_design,
        "file_layout_recommendations": file_layout,
        "orchestration_mapping": orchestration,
        "code_mapping": code_mapping,
        "observability": observability,
        "cicd": cicd,
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def _write_architecture_md(
    architecture_decision: dict[str, Any],
    medallion_rows: list[dict[str, Any]],
    uc_design: dict[str, Any],
    file_layout: list[dict[str, Any]],
    code_mapping: dict[str, Any],
    observability: dict[str, Any],
    cicd: dict[str, Any],
    output_dir: Path,
) -> Path:
    path = output_dir / "target_state_architecture.md"
    layer_dist = {layer: sum(1 for r in medallion_rows if r["layer"] == layer)
                  for layer in ("BRONZE", "SILVER", "GOLD")}

    lines: list[str] = [
        "# Wide World Importers — Target-State Databricks Architecture",
        "",
        "> **Accelerator:** WWI SQL Server → Databricks Modernisation Accelerator v0.1.0  ",
        f"> **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
        "> **Basis:** `inventory.json`, `dependencies.json`, `object_complexity_scores.json`",
        "",
        "---",
        "",
        "## 0. Architecture Decision",
        "",
        f"**Chosen architecture: `{architecture_decision['chosen_architecture']}`** "
        f"({'default' if architecture_decision['is_default'] else 'override applied'}).",
        "",
        "| Architecture | Fit | Reasoning |",
        "|---|---|---|",
    ]
    for arch, detail in architecture_decision["evaluated_alternatives"].items():
        lines.append(f"| {arch} | {detail['fit']} | {detail['reason']} |")
    lines += [
        "",
        f"_Override mechanism: {architecture_decision['override_mechanism']}_",
        "",
        "---",
        "",
        "## 1. Bronze / Silver / Gold Mapping",
        "",
        f"{len(medallion_rows)} data objects (tables, views, inline TVFs) mapped. "
        f"Bronze: {layer_dist['BRONZE']}, Silver: {layer_dist['SILVER']}, Gold: {layer_dist['GOLD']}. "
        "Full per-object mapping is in `medallion_mapping.csv`.",
        "",
        "### Sample mapping (first 10 of each layer)",
        "",
    ]
    for layer in ("BRONZE", "SILVER", "GOLD"):
        sample = [r for r in medallion_rows if r["layer"] == layer][:10]
        lines += [f"#### {layer}", ""]
        lines += _md_table(["Source", "Target FQN", "Rationale"],
                            [[r["source_id"], r["target_fqn"], r["rationale"]] for r in sample])
        lines.append("")

    lines += [
        "---", "",
        "## 2. Separation of Concerns",
        "",
        "| Concern | Layer / Mechanism | Notes |",
        "|---|---|---|",
        "| Ingestion | Bronze schema, Auto Loader / Lakeflow Connect jobs | One ingestion job per OLTP source table or per SSIS Data Flow equivalent; append-only, partitioned by ingestion_date. |",
        "| Transformation | Silver schema, Delta MERGE (SCD2) + Databricks SQL/PySpark | Conforms, deduplicates, applies SCD2; the only layer where business rules execute. |",
        "| Serving | Gold schema, Delta tables + Databricks SQL views | Fact tables and any pre-aggregated marts; BI/reporting tools connect here only. |",
        "| Orchestration | Databricks Workflows | Owns scheduling, retries, alerting, and task dependency graph — no business logic lives in the orchestration layer itself. |",
        "",
        "This mirrors the source's existing Integration/Dimension/Fact separation but makes the "
        "ingestion vs transformation boundary explicit, whereas in SSIS both concerns were "
        "interleaved within the same package/sequence container.",
        "",
        "---", "",
        "## 3. Unity Catalog Structure",
        "",
    ]
    for key, detail in uc_design.items():
        if key == "environments":
            continue
        lines += [f"### {key.replace('_', ' ').title()}", "",
                  f"**Pattern:** {detail['pattern']}", "",
                  f"**Rationale:** {detail['rationale']}", "",
                  f"**Tradeoffs:** {detail['tradeoffs']}", "",
                  f"**Assumptions:** {detail['assumptions']}", ""]

    lines += ["---", "", "## 4. File / Layout Strategy", ""]
    for rec in file_layout:
        obj_note = rec["objects"] if isinstance(rec["objects"], str) else f"{len(rec['objects'])} objects"
        lines += [
            f"### {rec['target_class']}", "",
            f"- **Scope:** {obj_note}",
            f"- **Format:** {rec['file_format']}",
            f"- **Partitioning:** {rec['partitioning']}",
            f"- **Clustering:** {rec['clustering']}",
            f"- **Rationale:** {rec['rationale']}",
            f"- **Tradeoffs:** {rec['tradeoffs']}",
            f"- **Assumptions:** {rec['assumptions']}",
            "",
        ]

    lines += ["---", "", "## 5. Orchestration Mapping", "",
              "Full detail in `orchestration_design.md`. Summary:", ""]
    lines += ["- Each SSIS package -> one Databricks Workflow job",
              "- Each Sequence Container (13 total) -> one parameterised per-entity job/task group",
              "- The 5-step per-entity pattern collapses to 3 Workflow tasks (extract, MERGE+lineage, watermark advance)",
              "- Precedence constraints -> Workflow `depends_on` / `run_if`",
              "- SSIS Expressions -> Workflow task parameters", ""]

    lines += ["---", "", "## 6. Code Mapping (T-SQL -> Databricks SQL / PySpark)", "",
              f"**Rule:** {code_mapping['rule']}", "",
              f"**Rationale:** {code_mapping['rationale']}", "",
              f"**Tradeoffs:** {code_mapping['tradeoffs']}", "",
              f"**Assumptions:** {code_mapping['assumptions']}", "",
              "### Distribution", ""]
    lines += _md_table(["Target", "Object Count"],
                        [[k, v] for k, v in sorted(code_mapping["distribution"].items(), key=lambda kv: -kv[1])])

    lines += ["", "---", "", "## 7. Observability", ""]
    for key, detail in observability.items():
        lines += [f"### {key.replace('_', ' ').title()}", "",
                  f"**Recommendation:** {detail['recommendation']}", "",
                  f"**Rationale:** {detail['rationale']}", "",
                  f"**Tradeoffs:** {detail['tradeoffs']}", ""]

    lines += ["---", "", "## 8. CI/CD & Environment Promotion", "",
              f"**Tooling:** {cicd['tooling']}", "",
              f"**Rationale:** {cicd['rationale']}", "",
              f"**Promotion pattern:** {cicd['environment_promotion']['pattern']}", "",
              f"**Promotion gate:** {cicd['environment_promotion']['promotion_gate']}", "",
              f"**Branching:** {cicd['branching']}", "",
              f"**Rollback:** {cicd['rollback']}", "",
              f"**Tradeoffs:** {cicd['tradeoffs']}", "",
              f"**Assumptions:** {cicd['assumptions']}", "",
              "---", "",
              "_This document proposes design only — no code or deployable assets are generated "
              "yet. See Step 6 (conversion) for implementation._",
              ]

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_orchestration_md(orchestration: dict[str, Any], output_dir: Path) -> Path:
    path = output_dir / "orchestration_design.md"
    lines: list[str] = [
        "# Orchestration Design — SSIS Control Flow -> Databricks Workflows",
        "",
        f"> **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "## Mapping Rules", "",
    ]
    for key in ("package_to_job", "sequence_container_to_task_group", "five_step_pattern_to_tasks",
                "precedence_constraints_to_dependencies", "expressions_to_parameters", "scheduling"):
        detail = orchestration[key]
        lines += [f"### {key.replace('_', ' ').title()}", "",
                  f"**Rule:** {detail['rule']}", "",
                  f"**Rationale:** {detail['rationale']}", ""]
        if "tradeoffs" in detail:
            lines += [f"**Tradeoffs:** {detail['tradeoffs']}", ""]
        if "watermark_design" in detail:
            lines += [f"**Watermark design:** {detail['watermark_design']}", ""]
        if "count_affected" in detail:
            lines += [f"**Objects affected:** {detail['count_affected']}", ""]

    lines += ["---", "", "## Per-Entity Job Mapping (Sequence Containers)", ""]
    mapped = orchestration["sequence_container_to_task_group"]["mapped_entities"]
    lines += ["| Source Container | Entity | Target Workflow Job | Step Count |",
              "|---|---|---|---|"]
    for m in mapped:
        lines.append(f"| {m['source_container']} | {m['entity']} | `{m['target_databricks_workflow_job']}` | {m['step_count']} |")

    lines += ["", "---", "", "## Summary Counts", ""]
    sc = orchestration["summary_counts"]
    lines += ["| Source SSIS Construct | Count | Target |",
              "|---|---|---|",
              f"| Package | {sc['packages']} | Workflow job |",
              f"| Sequence Container | {sc['sequence_containers']} | Per-entity task group / sub-job |",
              f"| Execute SQL Task | {sc['execute_sql_tasks']} | SQL task or folded into MERGE task |",
              f"| Data Flow Task | {sc['data_flow_tasks']} | PySpark extract task |",
              f"| Expression | {sc['expressions']} | Workflow task parameter |",
              ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Orchestration entry point
# ---------------------------------------------------------------------------

def generate_target_state_design(
    inventory: dict[str, Any],
    graph: dict[str, Any],
    complexity_scores: dict[str, Any],
    output_dir: Path,
    architecture_override: str | None = None,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    architecture_decision = decide_architecture(inventory, architecture_override)
    medallion_rows = build_medallion_mapping(inventory)
    uc_design = build_unity_catalog_design()
    file_layout = build_file_layout_recommendations(inventory)
    orchestration = build_orchestration_mapping(inventory)
    code_mapping = build_code_mapping(complexity_scores)
    observability = build_observability_design(inventory)
    cicd = build_cicd_design()

    paths = {
        "medallion_mapping_csv": _write_medallion_csv(medallion_rows, output_dir),
        "target_state_mappings_json": _write_mappings_json(
            architecture_decision, medallion_rows, uc_design, file_layout,
            orchestration, code_mapping, observability, cicd, output_dir,
        ),
        "target_state_architecture_md": _write_architecture_md(
            architecture_decision, medallion_rows, uc_design, file_layout,
            code_mapping, observability, cicd, output_dir,
        ),
        "orchestration_design_md": _write_orchestration_md(orchestration, output_dir),
    }
    return paths
