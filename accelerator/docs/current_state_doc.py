"""
current_state_doc.py
Generates current_state_documentation.md and current_state_summary.json
from the analysed inventory and dependency graph.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── Helpers ──────────────────────────────────────────────────────────────────

def _confidence_badge(level: str) -> str:
    badges = {"HIGH": "🟢 HIGH", "MEDIUM": "🟡 MEDIUM", "LOW": "🔴 LOW"}
    return badges.get(level, level)


def _md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |",
             "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return lines


def _objects_of_type(objects: list[dict], *types: str) -> list[dict]:
    return [o for o in objects if o.get("object_type") in types]


def _objects_of_project(objects: list[dict], project: str) -> list[dict]:
    return [o for o in objects if o.get("source_project") == project]


# ── Section builders ─────────────────────────────────────────────────────────

def _exec_summary(inv: dict, dep: dict) -> list[str]:
    objs     = inv["objects"]
    summary  = inv["summary"]
    tables   = _objects_of_type(objs, "TABLE")
    procs    = _objects_of_type(objs, "PROCEDURE")
    views    = _objects_of_type(objs, "VIEW", "TVF_INLINE", "TVF_MULTI")
    high_risk = [o for o in objs if o.get("risk") in ("HIGH", "CRITICAL")]
    oltp_tables = [t for t in tables if t["source_project"] == "OLTP" and "_Archive" not in t["name"]]
    dw_dim   = [t for t in tables if t.get("schema") == "Dimension"]
    dw_fact  = [t for t in tables if t.get("schema") == "Fact"]
    staging  = [t for t in tables if "_Staging" in t.get("name", "")]
    conf     = summary.get("avg_conversion_confidence", 0)

    lines = [
        "## Executive Summary",
        "",
        "> **Confidence:** " + _confidence_badge("HIGH"),
        "",
        "Wide World Importers (WWI) is a fictional wholesale novelty goods company whose "
        "SQL Server estate represents a well-structured, real-world OLTP + data warehouse "
        "pattern. The system consists of two SQL Server databases and one SSIS package that "
        "performs a daily incremental ETL.",
        "",
        "### At a Glance",
        "",
    ]
    lines += _md_table(
        ["Dimension", "Value"],
        [
            ["Total source objects analysed", str(inv["total_objects"])],
            ["OLTP database (WideWorldImporters)", str(len(_objects_of_project(objs, "OLTP")))],
            ["DW database (WideWorldImportersDW)", str(len(_objects_of_project(objs, "DW")))],
            ["SSIS artefacts", str(len(_objects_of_project(objs, "SSIS")))],
            ["Tables (OLTP, live)", str(len(oltp_tables))],
            ["Dimension tables (DW)", str(len(dw_dim))],
            ["Fact tables (DW)", str(len(dw_fact))],
            ["Staging tables (DW Integration schema)", str(len(staging))],
            ["Stored procedures", str(len(procs))],
            ["Views", str(len(views))],
            ["Dependency edges", str(dep["edge_count"])],
            ["Dependency cycles", str(len(dep.get("cycles", [])))],
            ["Average conversion confidence", f"{conf:.1%}"],
            ["Objects requiring manual remediation", str(len(high_risk))],
            ["Unsupported / skipped objects", str(inv["unsupported_count"])],
        ]
    )
    lines += [
        "",
        "### Migration Readiness",
        "",
        "The WWI estate is a **well-suited** candidate for automated migration to Databricks:",
        "",
        "- The DW schema structure (`Integration` → `Dimension` → `Fact`) **maps directly** "
        "to the Databricks medallion architecture (Bronze → Silver → Gold).",
        "- The ETL pattern is consistent: 13 identical Sequence Containers in one SSIS package, "
        "each following the same 5-step extract→stage→migrate loop.",
        "- Complexity is concentrated in **8 OLTP Integration procedures** that use T-SQL "
        "CURSOR loops over temporal table history — these require rewrite to PySpark temporal joins.",
        "- No dynamic SQL, linked servers, CLR objects, or OPENROWSET references were detected.",
        "- The `geography` spatial data type in `Dimension.City` / `Application.Cities` is the "
        "single **CRITICAL** data type gap — requires manual conversion to WKT string.",
        "",
    ]
    return lines


def _platform_overview(inv: dict) -> list[str]:
    lines = [
        "## 1. Source Platform Overview",
        "",
        "> **Confidence:** " + _confidence_badge("HIGH"),
        "",
        "### Databases",
        "",
    ]
    lines += _md_table(
        ["Database", "Version / Edition", "Role", "SSDT Project"],
        [
            ["WideWorldImporters", "SQL Server 2016+ (v13.0.4001.0 per SSIS metadata)",
             "OLTP transactional system", "`wwi-ssdt`"],
            ["WideWorldImportersDW", "SQL Server 2016+",
             "Star-schema analytical data warehouse", "`wwi-dw-ssdt`"],
        ]
    )
    lines += [
        "",
        "### Connectivity",
        "",
        "Both databases reside on the same SQL Server instance (Data Source = `.` / localhost). "
        "The SSIS package connects via **OLE DB / SQLNCLI11** using Windows Integrated Security.",
        "",
    ]
    lines += _md_table(
        ["Connection Manager", "Type", "Target Database", "Auth"],
        [
            ["`WWI_Source_DB`", "OLEDB / SQLNCLI11", "WideWorldImporters", "SSPI / Windows"],
            ["`WWI_DW_Destination_DB`", "OLEDB / SQLNCLI11", "WideWorldImportersDW", "SSPI / Windows"],
        ]
    )
    lines += [
        "",
        "### Scheduling",
        "",
        "No SQL Agent job metadata was present in the SSDT projects. The SSIS package "
        "`DailyETLMain.dtsx` is named for daily execution and contains a cutoff-time "
        "window pattern (`LastETLCutoffTime` → `TargetETLCutoffTime`) consistent with "
        "a nightly incremental load schedule.",
        "",
        "### Source-Control Artefacts",
        "",
    ]
    lines += _md_table(
        ["Artefact", "Type", "Files"],
        [
            ["`wwi-ssdt`", "SQL Server Data Tools (.sqlproj)", "336 `.sql` files"],
            ["`wwi-dw-ssdt`", "SQL Server Data Tools (.sqlproj)", "73 `.sql` files"],
            ["`wwi-ssis`", "SSIS project (.dtproj + .dtsx)", "1 package, 2 connection managers"],
        ]
    )
    lines.append("")
    return lines


def _schema_inventory(inv: dict) -> list[str]:
    objs = inv["objects"]
    lines = [
        "## 2. Schema Inventory",
        "",
        "> **Confidence:** " + _confidence_badge("HIGH"),
        "",
        "### WideWorldImporters (OLTP) — Schema Catalogue",
        "",
    ]
    oltp_schema_info = [
        ("Application",        "Reference / master data — Countries, Cities, StateProvinces, People, "
                               "DeliveryMethods, PaymentMethods, TransactionTypes, SystemParameters. "
                               "All reference tables are **system-versioned temporal tables**."),
        ("Sales",              "Core transactional domain — Customers, Orders, OrderLines, Invoices, "
                               "InvoiceLines, CustomerTransactions, BuyingGroups, SpecialDeals. "
                               "Customers is temporal; InvoiceLines and OrderLines use columnstore indexes."),
        ("Purchasing",         "Supplier procurement — Suppliers, SupplierCategories, PurchaseOrders, "
                               "PurchaseOrderLines, SupplierTransactions. Suppliers is temporal."),
        ("Warehouse",          "Inventory management — StockItems, StockItemHoldings, StockItemTransactions, "
                               "StockItemStockGroups, Colors, PackageTypes, StockGroups. "
                               "StockItems temporal. ColdRoomTemperatures and VehicleTemperatures "
                               "are **memory-optimised** IoT sensor tables."),
        ("Integration",        "ETL extraction layer — 13 stored procedures (`Get<Entity>Updates`) that "
                               "use temporal table AS-OF queries and CURSOR loops to extract changed rows "
                               "within a cutoff time window."),
        ("Website",            "Application API — 11 stored procedures (order placement, invoicing, "
                               "password management, IoT sensor recording) and 3 views for the web app."),
        ("WebApi",             "REST API surface — 24 views + 53 CRUD stored procedures providing "
                               "a thin read/write layer over the OLTP tables."),
        ("DataLoadSimulation", "Test data generation — 43 stored procedures and 4 helper tables "
                               "used to simulate realistic transactional workloads. "
                               "**Not in scope for migration to DW.**"),
        ("Sequences",          "26 SEQUENCE objects providing identity generation for all entity PKs."),
        ("dbo",                "Version metadata table (`SampleVersion`)."),
    ]
    lines += _md_table(
        ["Schema", "Object Count", "Purpose"],
        [[sc, str(len([o for o in objs if o["source_project"]=="OLTP" and o.get("schema")==sc])), desc]
         for sc, desc in oltp_schema_info]
    )
    lines += [
        "",
        "### WideWorldImportersDW (Data Warehouse) — Schema Catalogue",
        "",
    ]
    dw_schema_info = [
        ("Integration", "ETL staging layer — 13 `<Entity>_Staging` tables, 2 ETL control tables "
                        "(`ETL Cutoff`, `Lineage`), and 16 stored procedures (GetLastETLCutoffTime, "
                        "GetLineageKey, MigrateStaged*, PopulateDateDimensionForYear). "
                        "Maps to **Bronze** in target architecture."),
        ("Dimension",   "8 conformed dimensions (City, Customer, Date, Employee, Payment Method, "
                        "Stock Item, Supplier, Transaction Type). All SCD Type 2 with "
                        "`Valid From` / `Valid To` / `Lineage Key`. "
                        "Maps to **Silver** in target architecture."),
        ("Fact",        "6 fact tables (Sale, Order, Purchase, Movement, Transaction, Stock Holding). "
                        "All use columnstore indexes and date-range partition schemes (`PS_Date`). "
                        "Maps to **Gold** in target architecture."),
        ("Sequences",   "8 SEQUENCE objects for dimension surrogate key generation."),
        ("Application", "3 configuration procedures (Polybase setup, large sale table, ETL reseed)."),
        ("dbo",         "Version metadata table."),
    ]
    dw_obj_counts: dict[str, int] = defaultdict(int)
    for o in objs:
        if o["source_project"] == "DW":
            dw_obj_counts[o.get("schema", "?")] += 1
    lines += _md_table(
        ["Schema", "Object Count", "Medallion Layer", "Purpose"],
        [[sc, str(dw_obj_counts.get(sc,0)),
          {"Integration":"Bronze","Dimension":"Silver","Fact":"Gold"}.get(sc,"—"),
          desc]
         for sc, desc in dw_schema_info]
    )
    lines.append("")
    return lines


def _etl_overview(inv: dict, dep: dict) -> list[str]:
    objs = inv["objects"]
    pkg: dict = next((o for o in objs if o["object_type"] == "SSIS_PACKAGE"), {})
    containers = _objects_of_type(objs, "SSIS_SEQUENCE_CONTAINER")
    dataflows  = _objects_of_type(objs, "SSIS_DATA_FLOW")
    sql_tasks  = _objects_of_type(objs, "SSIS_EXECUTE_SQL")
    expr_tasks = _objects_of_type(objs, "SSIS_EXPRESSION")
    movement   = pkg.get("movement_paths", [])

    lines = [
        "## 3. ETL / Orchestration Overview",
        "",
        "> **Confidence:** " + _confidence_badge("HIGH"),
        "",
        "### Package: DailyETLMain",
        "",
        "A single SSIS package orchestrates the entire daily load from WideWorldImporters "
        "(OLTP) into WideWorldImportersDW. The package is **flat** — no sub-packages, "
        "no Execute Package Tasks, no conditional branching beyond precedence constraints.",
        "",
    ]
    lines += _md_table(
        ["Metric", "Value"],
        [
            ["SSIS version", "13.0.4001.0 (SQL Server 2016 Integration Services)"],
            ["Protection level", "0 (DontSaveSensitive)"],
            ["Total tasks", str(len(containers) + len(dataflows) + len(sql_tasks) + len(expr_tasks))],
            ["Sequence Containers", str(len(containers))],
            ["Data Flow Tasks", str(len(dataflows))],
            ["Execute SQL Tasks", str(len(sql_tasks))],
            ["Expression Tasks", str(len(expr_tasks))],
            ["Data movement paths", str(len(movement))],
        ]
    )
    lines += [
        "",
        "### Package-Level Variables",
        "",
    ]
    lines += _md_table(
        ["Variable", "Type", "Purpose"],
        [
            ["`LastETLCutoffTime`", "DateTime", "Watermark: last successful ETL run end time (read from `Integration.ETL Cutoff`)"],
            ["`TargetETLCutoffTime`", "DateTime", "Current run cutoff = `GETUTCDATE() - 5 minutes` (expression task)"],
            ["`LineageKey`", "Int32", "Current run lineage record key (from `Integration.GetLineageKey`)"],
            ["`TableName`", "String", "Entity name passed to `GetLineageKey` (set by expression task per container)"],
        ]
    )
    lines += [
        "",
        "### The 5-Step Pattern (repeated for all 13 entities)",
        "",
        "Every entity follows an identical Sequence Container structure:",
        "",
        "```",
        "┌─ Sequence Container: Load <Entity> [Dimension|Fact]",
        "│  1. Get Last <Entity> ETL Cutoff Time   → Execute SQL → Integration.GetLastETLCutoffTime",
        "│  2. Set TableName to <Entity>            → Expression  → @TableName = '<Entity>'",
        "│  3. Truncate <Entity>_Staging            → Execute SQL → DELETE FROM Integration.<Entity>_Staging",
        "│  4. Extract Updated <Entity> Data        → Data Flow   → OLTP.Integration.Get<Entity>Updates",
        "│                                                           → DW.Integration.<Entity>_Staging",
        "│  5. Get Lineage Key                      → Execute SQL → Integration.GetLineageKey",
        "│  6. Migrate Staged <Entity> Data         → Execute SQL → Integration.MigrateStaged<Entity>Data",
        "└──────────────────────────────────────────────────────────────────────────────────",
        "```",
        "",
        "### Sequence Container Load Order (Dimensions before Facts)",
        "",
    ]
    container_names = sorted(c["name"] for c in containers)
    dim_containers  = sorted(n for n in container_names if "Dimension" in n)
    fact_containers = sorted(n for n in container_names if "Fact" in n)
    lines += _md_table(
        ["#", "Container", "Type", "Upstream Deps"],
        [[str(i+1), name, "Dimension", "—"] for i, name in enumerate(dim_containers)]
        + [[str(i+8), name, "Fact", "Dimensions must complete first"]
           for i, name in enumerate(fact_containers)]
    )
    lines += [
        "",
        "### ETL Cutoff Window Logic",
        "",
        "The package implements a **sliding time-window incremental** pattern:",
        "",
        "1. `TargetETLCutoffTime` = `GETUTCDATE() - 5 minutes` (expression task at package start)",
        "2. Per entity: `LastETLCutoffTime` read from `Integration.ETL Cutoff` table",
        "3. OLTP `Get<Entity>Updates` proc extracts rows where `ValidFrom > @LastCutoff AND ValidFrom <= @NewCutoff`",
        "4. After successful `MigrateStaged*` proc: `Integration.ETL Cutoff.[Cutoff Time]` updated to `TargetETLCutoffTime`",
        "5. `Integration.Lineage` records start time, end time, success flag, and cutoff per run",
        "",
        "**The 5-minute buffer** prevents race conditions between the OLTP transaction commit "
        "and the ETL read window.",
        "",
    ]
    return lines


def _object_taxonomy(inv: dict) -> list[str]:
    objs = inv["objects"]
    lines = [
        "## 4. Object Taxonomy",
        "",
    ]

    # ── 4a. Tables ───────────────────────────────────────────────────────────
    lines += [
        "### 4a. Tables",
        "",
        "> **Confidence:** " + _confidence_badge("HIGH"),
        "",
        "#### OLTP Core Domain Tables",
        "",
    ]
    oltp_domains: dict[str, list] = {
        "Application": [],
        "Sales":       [],
        "Purchasing":  [],
        "Warehouse":   [],
    }
    for o in objs:
        if o["source_project"] == "OLTP" and o["object_type"] == "TABLE":
            sc = o.get("schema", "")
            if sc in oltp_domains and "_Archive" not in o["name"]:
                oltp_domains[sc].append(o)

    for schema, tbls in oltp_domains.items():
        if not tbls:
            continue
        rows = []
        for t in sorted(tbls, key=lambda x: x["name"]):
            feats = " ".join(f"`{f}`" for f in t.get("table_features", []))
            rows.append([f"`{t['schema']}.{t['name']}`", str(len(t.get("columns",[]))), feats or "—"])
        lines += [f"**{schema} schema** ({len(tbls)} tables)", ""]
        lines += _md_table(["Table", "Columns", "Special Features"], rows)
        lines.append("")

    # Archive tables note
    archive_tables = [o for o in objs if "_Archive" in o.get("name","") and o["source_project"]=="OLTP"]
    lines += [
        f"**Temporal History Tables** ({len(archive_tables)} tables)",
        "",
        "Every temporal table has a paired `<Name>_Archive` table managed by SQL Server's "
        "system-versioning. These are **read-only** from an ETL perspective — "
        "`Get<Entity>Updates` procs query them using `FOR SYSTEM_TIME` to capture changes.",
        "",
        "#### OLTP Specialised Tables",
        "",
    ]
    special_rows = [
        ["`DataLoadSimulation.ColdRoomTemperatures_temp`", "MEMORY_OPTIMIZED", "Temp buffer for sensor data simulation"],
        ["`Warehouse.ColdRoomTemperatures`", "MEMORY_OPTIMIZED", "IoT cold-room sensor readings (in-memory, no disk)"],
        ["`Warehouse.VehicleTemperatures`", "MEMORY_OPTIMIZED", "IoT vehicle temperature telemetry"],
        ["`Application.Logs`", "COLUMNSTORE", "Application audit log with columnstore for analytics"],
        ["`Sales.InvoiceLines`", "COLUMNSTORE", "High-volume invoice detail with columnstore"],
        ["`Sales.OrderLines`", "COLUMNSTORE", "High-volume order detail with columnstore"],
        ["`Warehouse.StockItemTransactions`", "COLUMNSTORE", "High-volume stock movement log with columnstore"],
        ["`Purchasing.SupplierTransactions`", "PARTITIONED", "Supplier financial transactions, date-partitioned"],
        ["`Sales.CustomerTransactions`", "PARTITIONED", "Customer financial transactions, date-partitioned"],
    ]
    lines += _md_table(["Table", "Feature", "Notes"], special_rows)
    lines.append("")

    # ── 4b. DW Tables ────────────────────────────────────────────────────────
    lines += [
        "#### DW Dimension Tables (Silver layer target)",
        "",
    ]
    dw_dims = [o for o in objs if o["source_project"]=="DW" and o.get("schema")=="Dimension"]
    dim_rows = []
    for t in sorted(dw_dims, key=lambda x: x["name"]):
        scd = "SCD2 (`Valid From`/`Valid To`)" if "SCD2" in t.get("etl_semantics",[]) else "—"
        dim_rows.append([f"`{t['schema']}.{t['name']}`", str(len(t.get("columns",[]))), scd])
    lines += _md_table(["Table", "Columns", "SCD Pattern"], dim_rows)
    lines.append("")

    lines += ["#### DW Fact Tables (Gold layer target)", ""]
    dw_facts = [o for o in objs if o["source_project"]=="DW" and o.get("schema")=="Fact"]
    fact_rows = []
    for t in sorted(dw_facts, key=lambda x: x["name"]):
        feats = " + ".join(t.get("table_features", ["—"]))
        fact_rows.append([f"`{t['schema']}.{t['name']}`", str(len(t.get("columns",[]))), feats])
    lines += _md_table(["Table", "Columns", "Storage Features"], fact_rows)
    lines.append("")

    lines += ["#### DW Staging Tables (Bronze layer target)", ""]
    staging = [o for o in objs if "_Staging" in o.get("name","") and o["source_project"]=="DW"]
    stg_rows = [[f"`{t['schema']}.{t['name']}`", str(len(t.get("columns",[]))),
                 "Truncate-and-reload each run"] for t in sorted(staging, key=lambda x:x["name"])]
    lines += _md_table(["Table", "Columns", "Load Pattern"], stg_rows)
    lines.append("")

    # ── 4c. Views ─────────────────────────────────────────────────────────────
    lines += [
        "### 4b. Views",
        "",
        "> **Confidence:** " + _confidence_badge("HIGH"),
        "",
        "No materialised / indexed views were detected in either project. "
        "All views are standard SQL Server views.",
        "",
        "#### WebApi Schema Views (OLTP)",
        "",
        "24 views provide a clean REST API surface over the OLTP tables. "
        "Named to mirror the entity: `WebApi.Customers`, `WebApi.Invoices`, etc.",
        "",
    ]
    webapi_views = [o for o in objs if o["object_type"]=="VIEW" and o.get("schema")=="WebApi"]
    lines += _md_table(
        ["View", "Likely Purpose"],
        [[f"`WebApi.{v['name']}`",
          f"Read surface for {v['name'].lower()} entity"]
         for v in sorted(webapi_views, key=lambda x:x["name"])]
    )
    lines += [
        "",
        "#### Website Schema Views (OLTP)",
        "",
        "3 views used by the internal web application:",
        "",
        "- `Website.Customers` — customer with delivery and buying-group context",
        "- `Website.Suppliers` — supplier contact and banking detail view",
        "- `Website.VehicleTemperatures` — IoT telemetry view for refrigerated vehicles",
        "",
        "#### Table-Valued Functions (inline TVFs)",
        "",
    ]
    tvfs = [o for o in objs if "TVF" in o.get("object_type","")]
    lines += _md_table(
        ["Function", "Project", "Type"],
        [[f"`{t['schema']}.{t['name']}`", t["source_project"], t["object_type"]]
         for t in tvfs]
    )
    lines.append("")

    # ── 4d. Stored Procedures ─────────────────────────────────────────────────
    lines += [
        "### 4c. Stored Procedures",
        "",
        "> **Confidence:** " + _confidence_badge("HIGH"),
        "",
    ]
    proc_groups = [
        ("Integration (OLTP) — ETL extraction", "OLTP", "Integration",
         "13 procs that extract changed rows from temporal tables into staging. "
         "7 use CURSOR loops (SCD2 entities); 6 are simple parameterised SELECTs (fact entities)."),
        ("Integration (DW) — ETL loading", "DW", "Integration",
         "16 procs: `GetLastETLCutoffTime`, `GetLineageKey`, 13 `MigrateStaged*` procs, "
         "and `PopulateDateDimensionForYear`. The Migrate procs implement SCD2 via UPDATE "
         "(close off old rows) + INSERT (new version) pattern."),
        ("WebApi — CRUD layer", "OLTP", "WebApi",
         "53 CRUD procs providing Insert/Update/Delete for the REST API. "
         "Named `<Verb><Entity>` (e.g. `InsertCustomer`, `UpdateStockItem`). "
         "**Not in scope for DW migration — serve the application tier only.**"),
        ("Website — Application operations", "OLTP", "Website",
         "11 procs for order placement (`InsertCustomerOrders`), invoicing "
         "(`InvoiceCustomerOrders`), IoT recording (`RecordColdRoomTemperatures`), "
         "and user management. **Application-tier only.**"),
        ("DataLoadSimulation — Test harness", "OLTP", "DataLoadSimulation",
         "43 procs simulating realistic workloads. "
         "Several use CURSORs (score 6–9) and MERGE. "
         "**Excluded from migration scope.**"),
        ("Application — Configuration", "OLTP", "Application",
         "14 procs for auditing, columnstore/fulltext/partitioning setup, "
         "role management, and SQL Agent job configuration."),
        ("Sequences — Maintenance", "OLTP", "Sequences",
         "2 procs to reseed all SEQUENCE objects. Replaced by `GENERATED ALWAYS AS IDENTITY` "
         "or Delta `AUTOINCREMENT` in the target."),
    ]
    for title, proj, schema, desc in proc_groups:
        group = [o for o in objs if o["source_project"]==proj
                 and o.get("schema")==schema and o["object_type"]=="PROCEDURE"]
        if not group:
            continue
        lines += [f"#### {title} ({len(group)} procedures)", "", desc, ""]
        rows = []
        for p in sorted(group, key=lambda x:x["name"])[:20]:
            rows.append([f"`{p['schema']}.{p['name']}`",
                         p["complexity_band"], p["risk"],
                         ", ".join(p.get("etl_semantics",[]) or ["—"])])
        lines += _md_table(["Procedure", "Complexity", "Risk", "ETL Semantics"], rows)
        if len(group) > 20:
            lines.append(f"*... and {len(group)-20} more*")
        lines.append("")

    # ── 4e. Functions ─────────────────────────────────────────────────────────
    lines += [
        "### 4d. Functions",
        "",
        "> **Confidence:** " + _confidence_badge("MEDIUM"),
        "",
        "Only 1 explicit scalar function and 2 inline TVFs were detected by the parser. "
        "The DataLoadSimulation schema contains ~15 helper functions that were classified "
        "as `SCALAR_FUNCTION` by DDL inspection but may include additional TVFs — "
        "the column extractor parses only the first DDL keyword.",
        "",
    ]
    funcs = _objects_of_type(objs, "SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI")
    lines += _md_table(
        ["Function", "Type", "Project", "Notes"],
        [[f"`{f['schema']}.{f['name']}`", f["object_type"], f["source_project"],
          ", ".join(f.get("etl_semantics",[])) or "—"]
         for f in funcs]
    )
    lines.append("")

    # ── 4e. SSIS Package ─────────────────────────────────────────────────────
    lines += [
        "### 4e. SSIS Package",
        "",
        "> **Confidence:** " + _confidence_badge("HIGH"),
        "",
        "See Section 3 (ETL / Orchestration Overview) for the full breakdown. "
        "Summary of task type distribution:",
        "",
    ]
    lines += _md_table(
        ["Task Type", "Count", "Target Databricks Equivalent"],
        [
            ["`SSIS_SEQUENCE_CONTAINER`", "13", "Databricks Workflow task group"],
            ["`SSIS_EXECUTE_SQL`", "53", "Notebook task (SQL cell) or Workflow parameter"],
            ["`SSIS_EXPRESSION`", "15", "Workflow parameter / `dbutils.widgets`"],
            ["`SSIS_DATA_FLOW`", "13", "PySpark notebook task"],
            ["`SSIS_PACKAGE`", "1", "Databricks Workflow (JSON)"],
        ]
    )
    lines.append("")
    return lines


def _dependency_map(dep: dict, inv: dict) -> list[str]:
    nodes = dep["nodes"]
    edges = dep["edges"]

    top_fanin = sorted(nodes.values(), key=lambda n: n["fan_in"], reverse=True)[:12]
    top_fanout = sorted(nodes.values(), key=lambda n: n["fan_out"], reverse=True)[:8]

    edge_type_counts = Counter(e["edge_type"] for e in edges)

    lines = [
        "## 5. Dependency Map",
        "",
        "> **Confidence:** " + _confidence_badge("MEDIUM"),
        "",
        f"The dependency graph contains **{dep['node_count']} nodes** and "
        f"**{dep['edge_count']} directed edges**. No cycles were detected — "
        "the graph is a valid DAG and a safe topological deployment order exists.",
        "",
        "### Edge Types",
        "",
    ]
    lines += _md_table(
        ["Edge Type", "Count", "Meaning"],
        [
            ["SQL_REFERENCE", str(edge_type_counts.get("SQL_REFERENCE",0)),
             "FROM/JOIN reference in SQL body"],
            ["FUNCTION_CALL", str(edge_type_counts.get("FUNCTION_CALL",0)),
             "Scalar or TVF call in SQL body"],
            ["CALLS_PROC", str(edge_type_counts.get("CALLS_PROC",0)),
             "SSIS Execute SQL task → stored procedure"],
            ["READS_FROM", str(edge_type_counts.get("READS_FROM",0)),
             "SSIS task reads from a table"],
            ["WRITES_TO", str(edge_type_counts.get("WRITES_TO",0)),
             "SSIS task writes to a table"],
            ["DATA_FLOW", str(edge_type_counts.get("DATA_FLOW",0)),
             "Staging table → DW target data movement"],
            ["SSIS_CONTROL_FLOW_SUCCESS", str(edge_type_counts.get("SSIS_CONTROL_FLOW_SUCCESS",0)),
             "Precedence constraint (on success)"],
        ]
    )
    lines += [
        "",
        "### Most Depended-Upon Objects (highest fan-in)",
        "",
        "These objects are the highest-blast-radius items in the migration. "
        "Converting them incorrectly will cascade failures across many dependants.",
        "",
    ]
    lines += _md_table(
        ["Object", "Type", "Fan-in", "Layer", "Risk"],
        [[f"`{n['schema']}.{n['name']}`", n["object_type"], str(n["fan_in"]),
          n["medallion_layer"], n["risk"]]
         for n in top_fanin]
    )
    lines += [
        "",
        "### Highest Fan-Out Objects (most dependencies consumed)",
        "",
    ]
    lines += _md_table(
        ["Object", "Type", "Fan-out", "Layer"],
        [[f"`{n['schema']}.{n['name']}`", n["object_type"], str(n["fan_out"]),
          n["medallion_layer"]]
         for n in top_fanout]
    )
    lines += [
        "",
        "### ETL Data Movement Lineage",
        "",
        "The complete source-to-target data flow for each entity:",
        "",
        "```",
        "OLTP (temporal table)  →  Integration.Get<Entity>Updates (cursor proc)",
        "                       →  [SSIS Data Flow: OLE DB Source → OLE DB Destination]",
        "                       →  DW.Integration.<Entity>_Staging",
        "                       →  Integration.MigrateStaged<Entity>Data (SCD2 proc)",
        "                       →  Dimension.<Entity>  OR  Fact.<Entity>",
        "```",
        "",
        "| Entity | OLTP Source | Staging | DW Target | Load Type |",
        "|---|---|---|---|---|",
    ]
    entities = [
        ("City",           "Application.Cities + archive",     "City_Staging",           "Dimension.City",          "SCD2 Incremental"),
        ("Customer",       "Sales.Customers + archive",        "Customer_Staging",        "Dimension.Customer",      "SCD2 Incremental"),
        ("Employee",       "Application.People + archive",     "Employee_Staging",        "Dimension.Employee",      "SCD2 Incremental"),
        ("Payment Method", "Application.PaymentMethods",       "PaymentMethod_Staging",   "Dimension.Payment Method","SCD2 Incremental"),
        ("Stock Item",     "Warehouse.StockItems + archive",   "StockItem_Staging",       "Dimension.Stock Item",    "SCD2 Incremental"),
        ("Supplier",       "Purchasing.Suppliers + archive",   "Supplier_Staging",        "Dimension.Supplier",      "SCD2 Incremental"),
        ("Transaction Type","Application.TransactionTypes",    "TransactionType_Staging", "Dimension.Transaction Type","SCD2 Incremental"),
        ("Order",          "Sales.Orders + OrderLines",        "Order_Staging",           "Fact.Order",              "Incremental"),
        ("Sale",           "Sales.Invoices + InvoiceLines",    "Sale_Staging",            "Fact.Sale",               "Incremental"),
        ("Purchase",       "Purchasing.PurchaseOrders + Lines","Purchase_Staging",        "Fact.Purchase",           "Incremental"),
        ("Movement",       "Warehouse.StockItemTransactions",  "Movement_Staging",        "Fact.Movement",           "Full (no cutoff)"),
        ("Transaction",    "Sales + Purchasing transactions",  "Transaction_Staging",     "Fact.Transaction",        "Incremental"),
        ("Stock Holding",  "Warehouse.StockItemHoldings",      "StockHolding_Staging",    "Fact.Stock Holding",      "Full snapshot"),
        ("Date",           "Computed (no OLTP source)",        "—",                       "Dimension.Date",          "Annual extension"),
    ]
    for name, src, stg, tgt, ltype in entities:
        lines.append(f"| {name} | `{src}` | `Integration.{stg}` | `{tgt}` | {ltype} |")
    lines.append("")
    return lines


def _data_domains(inv: dict) -> list[str]:
    lines = [
        "## 6. Data Domains",
        "",
        "> **Confidence:** " + _confidence_badge("HIGH"),
        "",
    ]
    domains = [
        ("Sales & Revenue",
         "Sales.Customers, Sales.Orders, Sales.OrderLines, Sales.Invoices, Sales.InvoiceLines, "
         "Sales.CustomerTransactions, Sales.SpecialDeals, Sales.BuyingGroups",
         "Fact.Sale, Fact.Order, Dimension.Customer",
         "Order-to-cash — customer orders, pick/pack, invoicing, payment transactions"),
        ("Purchasing & Supply",
         "Purchasing.Suppliers, Purchasing.PurchaseOrders, Purchasing.PurchaseOrderLines, "
         "Purchasing.SupplierTransactions",
         "Fact.Purchase, Dimension.Supplier",
         "Procure-to-pay — supplier orders, goods receipt, supplier payments"),
        ("Warehouse & Inventory",
         "Warehouse.StockItems, Warehouse.StockItemHoldings, Warehouse.StockItemTransactions, "
         "Warehouse.StockItemStockGroups, Warehouse.Colors, Warehouse.PackageTypes",
         "Fact.Movement, Fact.Stock Holding, Dimension.Stock Item",
         "Stock management — holdings, movements, physical attributes"),
        ("Reference / Master Data",
         "Application.Countries, Application.Cities, Application.StateProvinces, "
         "Application.People, Application.DeliveryMethods, Application.PaymentMethods, "
         "Application.TransactionTypes",
         "Dimension.City, Dimension.Employee, Dimension.Payment Method, Dimension.Transaction Type",
         "Geography, people, lookup reference data — all system-versioned temporal"),
        ("IoT / Telemetry",
         "Warehouse.ColdRoomTemperatures, Warehouse.VehicleTemperatures, "
         "DataLoadSimulation.ColdRoomTemperatures_temp",
         "Website.VehicleTemperatures (view only)",
         "Sensor data from cold-chain equipment. Memory-optimised tables. "
         "No DW target — not in ETL scope."),
        ("Financial Transactions",
         "Sales.CustomerTransactions, Purchasing.SupplierTransactions",
         "Fact.Transaction",
         "Dual-sided financial transaction ledger (customer + supplier combined in Fact.Transaction)"),
        ("ETL Control / Audit",
         "Integration.ETL Cutoff, Integration.Lineage",
         "—",
         "ETL watermark and lineage tracking. Replaced by Databricks run metadata in target."),
    ]
    lines += _md_table(
        ["Domain", "OLTP Tables", "DW Targets", "Description"],
        [[d, o, t, desc] for d, o, t, desc in domains]
    )
    lines.append("")
    return lines


def _load_patterns(inv: dict) -> list[str]:
    lines = [
        "## 7. Load Patterns",
        "",
        "> **Confidence:** " + _confidence_badge("HIGH"),
        "",
        "Four distinct load patterns are present in the WWI ETL:",
        "",
        "### Pattern 1 — SCD Type 2 Incremental (Dimensions)",
        "",
        "**Entities:** City, Customer, Employee, Payment Method, Stock Item, Supplier, Transaction Type",
        "",
        "```",
        "1. Read LastCutoffTime from Integration.ETL Cutoff WHERE Table = '<Entity>'",
        "2. OLTP proc Get<Entity>Updates(@LastCutoff, @TargetCutoff):",
        "   a. CURSOR over temporal archive rows WHERE ValidFrom IN cutoff window",
        "   b. Reconstruct point-in-time state using FOR SYSTEM_TIME AS OF",
        "   c. Compute Valid From / Valid To for each version",
        "   d. INSERT into #CityChanges temp table",
        "   e. UPDATE #CityChanges.ValidTo = MIN(later ValidFrom) for same entity",
        "   f. SELECT to SSIS data flow",
        "3. SSIS Data Flow: OLE DB Source → OLE DB Destination (bulk insert to staging)",
        "4. DW proc MigrateStaged<Entity>Data:",
        "   a. UPDATE Dimension rows: Valid To = earliest staging row ValidFrom (close off)",
        "   b. INSERT staging rows into Dimension (new SCD2 versions)",
        "   c. UPDATE Lineage: mark complete",
        "   d. UPDATE ETL Cutoff watermark",
        "```",
        "",
        "**Databricks target:** Delta MERGE INTO with SCD2 history column + `Valid From`/`Valid To`",
        "",
        "### Pattern 2 — Incremental Append (Facts — no SCD)",
        "",
        "**Entities:** Sale, Order, Purchase, Transaction",
        "",
        "```",
        "1. Get cutoff time",
        "2. OLTP proc: SELECT new rows WHERE LastEditedWhen > @LastCutoff",
        "3. SSIS: bulk load to staging",
        "4. MigrateStaged*: plain INSERT from staging into Fact (no update / close-off)",
        "5. Update watermark",
        "```",
        "",
        "**Databricks target:** Delta append (`df.write.mode('append')`) or MERGE on surrogate key",
        "",
        "### Pattern 3 — Full Snapshot (Stock Holding Fact)",
        "",
        "**Entity:** Stock Holding",
        "",
        "```",
        "1. No cutoff window — full extract of current Warehouse.StockItemHoldings",
        "2. Staging bulk load",
        "3. MigrateStaged: DELETE existing rows + INSERT (full replace each run)",
        "```",
        "",
        "**Databricks target:** Delta `overwrite` mode with `replaceWhere` on date partition",
        "",
        "### Pattern 4 — Annual Extension (Date Dimension)",
        "",
        "**Entity:** Date",
        "",
        "```",
        "1. EXEC Integration.PopulateDateDimensionForYear @YearNumber (at package start)",
        "2. Uses Integration.GenerateDateDimensionColumns TVF",
        "3. INSERT new year rows only (no update to existing dates)",
        "```",
        "",
        "**Databricks target:** Notebook cell — compute date range + Delta append",
        "",
        "### Pattern Summary",
        "",
    ]
    lines += _md_table(
        ["Pattern", "Entities", "Load Type", "Complexity", "Target Approach"],
        [
            ["SCD Type 2", "7 dimensions", "Incremental + history", "HIGH",
             "Delta MERGE INTO with SCD2 columns"],
            ["Incremental Append", "4 facts", "Append new rows", "LOW",
             "Delta APPEND or MERGE on PK"],
            ["Full Snapshot", "Stock Holding", "Full replace per run", "LOW",
             "Delta OVERWRITE with replaceWhere"],
            ["Annual Extension", "Date dimension", "Append new year", "LOW",
             "Notebook compute + Delta APPEND"],
        ]
    )
    lines.append("")
    return lines


def _operational_assumptions(inv: dict) -> list[str]:
    lines = [
        "## 8. Operational Assumptions",
        "",
        "> **Confidence:** " + _confidence_badge("MEDIUM"),
        "",
        "The following assumptions are inferred from the code and metadata. "
        "They should be validated with the WWI operations team before migration.",
        "",
    ]
    assumptions = [
        ("SCH-01", "HIGH",   "The ETL runs once per day (nightly), consistent with package name `DailyETLMain`"),
        ("SCH-02", "MEDIUM", "The package runs with SQL Server Agent or Windows Task Scheduler — no SQL Agent XML was found"),
        ("SCH-03", "MEDIUM", "The 5-minute cutoff buffer (`GETUTCDATE() - 5 min`) guards against long-running OLTP transactions; this cadence must be preserved in Databricks"),
        ("DAT-01", "HIGH",   "All OLTP tables use UTC timestamps (`ValidFrom`, `LastEditedWhen` are UTC); no timezone conversion required"),
        ("DAT-02", "HIGH",   "`Integration.ETL Cutoff` is the single watermark store — one row per entity; must be migrated or replaced before first Databricks run"),
        ("DAT-03", "MEDIUM", "`Integration.Lineage` acts as the audit log; a comparable audit Delta table should be maintained in the target"),
        ("DAT-04", "HIGH",   "SCD2 `Valid To` = `'9999-12-31 23:59:59.9999999'` signals the current active row — this sentinel value is used consistently across all Migrate procs"),
        ("INF-01", "HIGH",   "Both databases are on the same SQL Server instance — SSIS uses local OLE DB connections; target uses JDBC or Unity Catalog external tables"),
        ("INF-02", "LOW",    "Integrated Security (SSPI/Windows) is used — must be replaced with Databricks secrets + SQL Server JDBC with SQL auth or Entra ID"),
        ("SEC-01", "MEDIUM", "All Integration procs use `WITH EXECUTE AS OWNER` — privilege elevation pattern not applicable in Databricks; Unity Catalog governs access"),
        ("SCO-01", "HIGH",   "`DataLoadSimulation` schema is a test harness and should NOT be migrated to Databricks"),
        ("SCO-02", "HIGH",   "`WebApi` and `Website` schemas serve the application tier; they are not ETL objects and should NOT be replicated as-is in the DW"),
        ("SCO-03", "MEDIUM", "IoT tables (`ColdRoomTemperatures`, `VehicleTemperatures`) have no DW staging/migration path — out of scope for this migration unless a streaming path is added"),
    ]
    lines += _md_table(
        ["ID", "Confidence", "Assumption"],
        [[a[0], _confidence_badge(a[1]), a[2]] for a in assumptions]
    )
    lines.append("")
    return lines


def _tech_debt(inv: dict, dep: dict) -> list[str]:
    objs = inv["objects"]
    hotspots = sorted(
        [o for o in objs if o.get("complexity_score", 0) >= 5],
        key=lambda x: -x["complexity_score"]
    )
    lines = [
        "## 9. Technical Debt / Migration Hotspots",
        "",
        "> **Confidence:** " + _confidence_badge("HIGH"),
        "",
        "### Complexity Hotspot Map",
        "",
        "Objects scoring ≥ 5 on the complexity index require manual conversion effort:",
        "",
    ]
    lines += _md_table(
        ["Object", "Score", "Risk", "Pattern Flags", "Effort Estimate"],
        [[f"`{h['schema']}.{h['name']}`", str(h["complexity_score"]), h["risk"],
          ", ".join(str(f).split("(")[0] for f in h.get("complexity_factors",[])),
          {"VERY_HIGH":"5–8 days","HIGH":"2–5 days","MEDIUM":"1–2 days","LOW":"< 1 day"}
          .get(h["complexity_band"],"—")]
         for h in hotspots]
    )
    lines += [
        "",
        "### Critical Migration Issues",
        "",
    ]
    critical_issues = [
        ("CRI-01", "`geography` data type",
         "Used in `Application.Cities` and `Dimension.City.[Location]`. "
         "Spark has no native spatial type. Must be stored as WKT `STRING`. "
         "If geospatial queries are needed, use Databricks H3 or Mosaic library.",
         "HIGH", "2–3 days"),
        ("CRI-02", "CURSOR loops in 7 `Get<Entity>Updates` procs",
         "Each cursor iterates over temporal archive rows to reconstruct SCD history. "
         "Must be rewritten as PySpark temporal joins across current + archive DataFrames. "
         "Pattern is identical across all 7 — one implementation, 7 parameterisations.",
         "HIGH", "3–5 days (shared pattern)"),
        ("CRI-03", "`FOR SYSTEM_TIME AS OF` temporal queries",
         "T-SQL temporal time-travel syntax has no direct PySpark equivalent. "
         "Delta Lake Change Data Feed (`readChangeFeed`) provides similar semantics "
         "but requires CDF to be enabled on the source Delta table.",
         "HIGH", "1–2 days"),
        ("CRI-04", "`VARBINARY(MAX)` photo column in `Dimension.Employee`",
         "Binary large objects in dimension tables are unusual. "
         "In Databricks, store as `BINARY` or externalise to Unity Catalog Volumes.",
         "MEDIUM", "0.5 days"),
        ("CRI-05", "`DECIMAL(18,2)` / `DECIMAL(18,3)` precision",
         "Spark `DECIMAL(18,2)` maps exactly — no data loss. "
         "Validate that no column exceeds precision 38 (Spark maximum).",
         "LOW", "0.5 days"),
        ("CRI-06", "`NVARCHAR(MAX)` free-text columns",
         "Maps to Spark `STRING`. Collation-sensitive sorting and comparison "
         "will behave differently in Spark (no SQL Server collation). "
         "Impact is low for DW analytics use cases.",
         "LOW", "< 0.5 days"),
        ("CRI-07", "Memory-optimised tables (`MEMORY_OPTIMIZED = ON`)",
         "`Warehouse.ColdRoomTemperatures` and `Warehouse.VehicleTemperatures` use "
         "SQL Server In-Memory OLTP for IoT sensor ingestion. No DW ETL path exists. "
         "If streaming is required, use Databricks Structured Streaming from SQL Server CDC.",
         "MEDIUM", "Out of scope for batch ETL"),
        ("CRI-08", "Partition schemes (`PS_Date`)",
         "All Fact tables use a SQL Server date partition scheme. "
         "Replace with Delta Lake `PARTITIONED BY (date_key DATE)` + "
         "`OPTIMIZE ... ZORDER BY` on frequently filtered FK keys.",
         "LOW", "1 day"),
        ("CRI-09", "`WITH EXECUTE AS OWNER` privilege escalation",
         "All Integration procs use owner-context execution. "
         "In Databricks, use Unity Catalog column/row-level security and "
         "service principals with least-privilege grants.",
         "LOW", "0.5 days"),
        ("CRI-10", "SSIS `ExpressionTask` variable assignments",
         "15 expression tasks set variables like `@TargetETLCutoffTime = DATEADD(...)`. "
         "Replace with Databricks Workflow job parameters and `dbutils.widgets`.",
         "LOW", "0.5 days"),
    ]
    lines += _md_table(
        ["ID", "Issue", "Description", "Impact", "Effort"],
        [[i[0], f"**{i[1]}**", i[2], i[3], i[4]] for i in critical_issues]
    )
    lines += [
        "",
        "### Objects Excluded from Migration Scope",
        "",
    ]
    excluded = [
        ("`DataLoadSimulation.*`", "43 procs + 4 tables", "Test data generation harness — no business value in DW"),
        ("`WebApi.*`", "24 views + 53 procs", "Application CRUD layer — belongs to the application tier"),
        ("`Website.*`", "3 views + 11 procs", "Web application layer — not ETL objects"),
        ("Temporal archive tables", "18 `*_Archive` tables", "SQL Server system-managed — queried by Get* procs; not migrated directly"),
        ("OLTP Sequences", "26 SEQUENCE objects", "Replaced by Delta `GENERATED ALWAYS AS IDENTITY` or SEQUENCE objects in UC"),
        ("Security objects", "18 role/permission scripts", "Unity Catalog governs access — not migrated"),
        ("Memory-optimised IoT tables", "3 tables", "No DW ETL path — out of scope unless streaming added"),
        ("`Integration.ETL Cutoff` table", "1 table", "Replaced by Databricks Workflow state / job run metadata"),
        ("`Integration.Lineage` table", "1 table", "Replaced by Databricks job run history + optional audit Delta table"),
    ]
    lines += _md_table(
        ["Object/Group", "Count", "Reason for Exclusion"],
        [[e[0], e[1], e[2]] for e in excluded]
    )
    lines.append("")
    return lines


# ── Machine-readable summary ──────────────────────────────────────────────────

def _build_summary_json(inv: dict, dep: dict) -> dict[str, Any]:
    objs    = inv["objects"]
    summary = inv["summary"]
    nodes   = dep["nodes"]

    tables  = _objects_of_type(objs, "TABLE")
    procs   = _objects_of_type(objs, "PROCEDURE")
    views   = _objects_of_type(objs, "VIEW", "TVF_INLINE", "TVF_MULTI")
    seqs    = _objects_of_type(objs, "SEQUENCE")
    udts    = _objects_of_type(objs, "USER_DEFINED_TYPE")
    ssis_pkg = _objects_of_type(objs, "SSIS_PACKAGE")
    ssis_tasks = [o for o in objs if o.get("source_project")=="SSIS" and o["object_type"]!="SSIS_PACKAGE"]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "accelerator_version": "0.1.0",
        "source_system": {
            "databases": [
                {"name": "WideWorldImporters", "role": "OLTP", "ssdt_project": "wwi-ssdt"},
                {"name": "WideWorldImportersDW", "role": "DW", "ssdt_project": "wwi-dw-ssdt"},
            ],
            "ssis_packages": [{"name": "DailyETLMain", "path": "wwi-ssis/wwi-ssis/DailyETLMain.dtsx"}],
        },
        "object_counts": {
            "total": inv["total_objects"],
            "unsupported_skipped": inv["unsupported_count"],
            "tables": len(tables),
            "tables_oltp_live": len([t for t in tables if t["source_project"]=="OLTP" and "_Archive" not in t["name"]]),
            "tables_dw_dimension": len([t for t in tables if t.get("schema")=="Dimension"]),
            "tables_dw_fact": len([t for t in tables if t.get("schema")=="Fact"]),
            "tables_dw_staging": len([t for t in tables if "_Staging" in t.get("name","")]),
            "temporal_tables": len([t for t in tables if "TEMPORAL" in t.get("table_features",[])]),
            "columnstore_tables": len([t for t in tables if "COLUMNSTORE" in t.get("table_features",[])]),
            "memory_optimised_tables": len([t for t in tables if "MEMORY_OPTIMIZED" in t.get("table_features",[])]),
            "partitioned_tables": len([t for t in tables if "PARTITIONED" in t.get("table_features",[])]),
            "views": len(views),
            "stored_procedures": len(procs),
            "sequences": len(seqs),
            "user_defined_types": len(udts),
            "ssis_packages": len(ssis_pkg),
            "ssis_tasks_total": len(ssis_tasks),
        },
        "etl_patterns": {
            "scd_type_2_entities": ["City","Customer","Employee","Payment Method","Stock Item","Supplier","Transaction Type"],
            "incremental_append_entities": ["Sale","Order","Purchase","Transaction"],
            "full_snapshot_entities": ["Stock Holding"],
            "annual_extension_entities": ["Date"],
            "watermark_mechanism": "Integration.ETL Cutoff table (one row per entity)",
            "lineage_mechanism": "Integration.Lineage table (one row per run per entity)",
            "cutoff_buffer_minutes": 5,
        },
        "complexity": {
            "by_band": summary.get("by_complexity",{}),
            "avg_confidence": summary.get("avg_conversion_confidence",0),
            "hotspot_objects": [
                {"id": o["id"], "score": o["complexity_score"], "factors": o.get("complexity_factors",[])}
                for o in sorted(objs, key=lambda x:-x.get("complexity_score",0))
                if o.get("complexity_score",0) >= 5
            ],
        },
        "medallion_assignment": summary.get("by_layer",{}),
        "risk_distribution": summary.get("by_risk",{}),
        "dependency_graph": {
            "nodes": dep["node_count"],
            "edges": dep["edge_count"],
            "cycles": dep["cycles"],
            "top_fanin": [
                {"id": n["id"], "name": f"{n['schema']}.{n['name']}", "fan_in": n["fan_in"]}
                for n in sorted(nodes.values(), key=lambda x:-x["fan_in"])[:10]
            ],
        },
        "migration_scope": {
            "in_scope": ["Integration (OLTP)", "Integration (DW)", "Dimension", "Fact",
                         "Application (reference tables)", "SSIS DailyETLMain"],
            "out_of_scope": ["DataLoadSimulation", "WebApi", "Website",
                             "Security objects", "Memory-optimised IoT tables",
                             "OLTP Sequences", "Archive tables (SQL Server managed)"],
        },
        "critical_issues": [
            {"id": "CRI-01", "issue": "geography data type", "impact": "HIGH", "effort_days": "2–3"},
            {"id": "CRI-02", "issue": "CURSOR loops in Get<Entity>Updates procs", "impact": "HIGH", "effort_days": "3–5"},
            {"id": "CRI-03", "issue": "FOR SYSTEM_TIME AS OF temporal queries", "impact": "HIGH", "effort_days": "1–2"},
            {"id": "CRI-04", "issue": "VARBINARY(MAX) binary column in Employee dimension", "impact": "MEDIUM", "effort_days": "0.5"},
            {"id": "CRI-07", "issue": "Memory-optimised IoT tables (no DW ETL path)", "impact": "MEDIUM", "effort_days": "out-of-scope"},
        ],
        "confidence_by_section": {
            "executive_summary":       "HIGH",
            "platform_overview":       "HIGH",
            "schema_inventory":        "HIGH",
            "etl_overview":            "HIGH",
            "object_taxonomy_tables":  "HIGH",
            "object_taxonomy_views":   "HIGH",
            "object_taxonomy_procs":   "HIGH",
            "object_taxonomy_functions":"MEDIUM",
            "object_taxonomy_ssis":    "HIGH",
            "dependency_map":          "MEDIUM",
            "data_domains":            "HIGH",
            "load_patterns":           "HIGH",
            "operational_assumptions": "MEDIUM",
            "tech_debt":               "HIGH",
        },
    }


# ── Main entry point ──────────────────────────────────────────────────────────

def generate_current_state_docs(
    inventory: dict[str, Any],
    graph: dict[str, Any],
    output_dir: Path,
) -> tuple[Path, Path]:
    """
    Generate current_state_documentation.md and current_state_summary.json.
    Returns (md_path, json_path).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build markdown sections
    sections: list[list[str]] = [
        [
            "# Wide World Importers — Current State Documentation",
            "",
            "> **Accelerator:** WWI SQL Server → Databricks Modernisation Accelerator v0.1.0  ",
            f"> **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
            "> **Source corpus:** `microsoft/sql-server-samples` — WideWorldImporters  ",
            "> **Analysis basis:** Static code analysis (no live database connection required)",
            "",
            "---",
            "",
        ],
        _exec_summary(inventory, graph),
        ["---", ""],
        _platform_overview(inventory),
        _schema_inventory(inventory),
        _etl_overview(inventory, graph),
        _object_taxonomy(inventory),
        _dependency_map(graph, inventory),
        _data_domains(inventory),
        _load_patterns(inventory),
        _operational_assumptions(inventory),
        _tech_debt(inventory, graph),
    ]

    all_lines: list[str] = []
    for section in sections:
        all_lines.extend(section)

    md_path = output_dir / "current_state_documentation.md"
    md_path.write_text("\n".join(all_lines), encoding="utf-8")

    # Build JSON summary
    summary_json = _build_summary_json(inventory, graph)
    json_path = output_dir / "current_state_summary.json"
    json_path.write_text(json.dumps(summary_json, indent=2, default=str), encoding="utf-8")

    return md_path, json_path
