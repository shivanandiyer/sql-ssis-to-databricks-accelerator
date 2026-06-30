"""
inventory_builder.py
Aggregates all parser outputs into a single unified inventory,
assigns medallion layers, derives conversion confidence, and flags unsupported objects.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Medallion layer assignment rules
# ---------------------------------------------------------------------------

# Schema → layer mapping (DW project)
_DW_SCHEMA_LAYER: dict[str, str] = {
    "Dimension":   "SILVER",
    "Fact":        "GOLD",
    "Integration": "BRONZE",   # staging tables and ETL procs
    "dbo":         "BRONZE",
    "Application": "SILVER",
    "Sequences":   "BRONZE",
    "Storage":     "BRONZE",
}

# Schema → layer mapping (OLTP project)
_OLTP_SCHEMA_LAYER: dict[str, str] = {
    "Sales":               "BRONZE",
    "Purchasing":          "BRONZE",
    "Warehouse":           "BRONZE",
    "Application":         "BRONZE",
    "Integration":         "BRONZE",
    "DataLoadSimulation":  "BRONZE",
    "Website":             "SILVER",
    "WebApi":              "SILVER",
    "dbo":                 "BRONZE",
}

# Object types never converted (security/config/infra objects)
_SKIP_TYPES = {"SECURITY", "FILEGROUP", "PARTITION_FUNCTION", "PARTITION_SCHEME",
               "EXTENDED_PROPERTY", "SCRIPT", "UNKNOWN", "UNREADABLE"}

# Confidence scoring: base per object_type, then deducted per risk factor
_BASE_CONFIDENCE: dict[str, float] = {
    "TABLE":            0.95,
    "VIEW":             0.90,
    "SEQUENCE":         0.80,
    "SCALAR_FUNCTION":  0.75,
    "TVF_INLINE":       0.70,
    "TVF_MULTI":        0.55,
    "PROCEDURE":        0.65,
    "TRIGGER":          0.30,
    "USER_DEFINED_TYPE":0.60,
    "SSIS_PACKAGE":     0.70,
    "SSIS_TASK":        0.65,
    "CONNECTION_MANAGER":0.90,
}
_DEDUCTIONS: dict[str, float] = {
    "CURSOR":           0.25,
    "DYNAMIC_SQL":      0.30,
    "FOR_XML":          0.20,
    "FOR_JSON":         0.15,
    "OPENROWSET":       0.35,
    "LINKED_SERVER":    0.40,
    "FUZZY_LOOKUP":     0.50,
    "SCRIPT_COMPONENT": 0.45,
    "MEMORY_OPTIMIZED": 0.20,
    "TEMPORAL":         0.15,
}

# Risk level thresholds (based on complexity_score)
_RISK_MAP = [(0, "NONE"), (3, "LOW"), (6, "MEDIUM"), (10, "HIGH"), (15, "CRITICAL")]


def _assign_layer(obj: dict[str, Any]) -> str:
    # Infrastructure objects (surrogate-key generators, type definitions) have
    # no medallion data lifecycle at all — defaulting them to BRONZE (found by
    # adversarial review) silently inflates the apparent Bronze migration
    # scope and is actively misleading next to the code-mapping guidance that
    # recommends replacing SEQUENCE objects with GENERATED ALWAYS AS IDENTITY
    # rather than porting them as data objects.
    if obj.get("object_type") in ("SEQUENCE", "USER_DEFINED_TYPE"):
        return "INFRASTRUCTURE"

    project = obj.get("source_project", "")
    schema  = obj.get("schema", "")
    if project == "DW":
        return _DW_SCHEMA_LAYER.get(schema, "BRONZE")
    if project == "OLTP":
        return _OLTP_SCHEMA_LAYER.get(schema, "BRONZE")
    if project == "SSIS":
        return "BRONZE"
    return "BRONZE"


def _assign_risk(obj: dict[str, Any]) -> str:
    score = obj.get("complexity_score", 0)
    risk  = "NONE"
    for threshold, label in _RISK_MAP:
        if score >= threshold:
            risk = label
    # Elevate for specific unsupported features
    unsupported = obj.get("unsupported") or obj.get("complexity_factors") or []
    for item in unsupported:
        if any(k in str(item) for k in ("OPENROWSET", "LINKED_SERVER", "FUZZY")):
            risk = "CRITICAL"
            break
        if "CURSOR" in str(item) and risk in ("NONE", "LOW"):
            risk = "MEDIUM"
    return risk


def _assign_confidence(obj: dict[str, Any]) -> float:
    base = _BASE_CONFIDENCE.get(obj.get("object_type", ""), 0.50)
    factors = obj.get("complexity_factors") or []
    unsupported = obj.get("unsupported") or []
    deduction = 0.0
    for key, penalty in _DEDUCTIONS.items():
        if any(key in str(f) for f in factors + unsupported):
            deduction += penalty
    return max(0.0, round(base - deduction, 2))


def _is_unsupported(obj: dict[str, Any]) -> bool:
    if obj.get("object_type") in _SKIP_TYPES:
        return True
    if obj.get("error"):
        return True
    return False


_SERVING_PASSTHROUGH_SCHEMAS = {"Website", "WebApi"}


def _layer_subcategory(obj: dict[str, Any]) -> str | None:
    """Distinguish true conformed-Silver objects (e.g. SCD2 dimensions) from
    thin CRUD pass-through objects (WebApi/Website) that happen to also map
    to the Silver schema. Found by adversarial review: both were previously
    labeled identically as "Silver", which conflates two different categories
    of migration effort (real conformance work vs. a serving-layer view) when
    estimating scope from medallion_mapping.csv alone."""
    if obj.get("source_project") == "OLTP" and obj.get("schema") in _SERVING_PASSTHROUGH_SCHEMAS:
        return "serving_passthrough"
    if obj.get("medallion_layer") == "SILVER":
        return "conformed"
    return None


def _normalise_sql_object(obj: dict[str, Any]) -> dict[str, Any]:
    """Add derived fields to a SQL parser output dict."""
    obj["medallion_layer"]      = _assign_layer(obj)
    obj["layer_subcategory"]    = _layer_subcategory(obj)
    obj["risk"]                 = _assign_risk(obj)
    obj["conversion_confidence"]= _assign_confidence(obj)
    obj["is_unsupported"]       = _is_unsupported(obj)

    # Manual remediation flags
    manual: list[str] = []
    triggers        = obj.get("object_type") == "TRIGGER"
    if triggers:
        manual.append("Triggers have no direct equivalent in Databricks — review and convert to Delta constraints or Workflow pre/post hooks")
    if "CURSOR" in str(obj.get("complexity_factors", [])):
        manual.append("CURSOR-based row-by-row logic must be rewritten as set-based PySpark operations")
    if "DYNAMIC_SQL" in str(obj.get("complexity_factors", [])):
        manual.append("Dynamic SQL cannot be auto-converted — manual PySpark parameterisation required")
    if "OPENROWSET" in str(obj.get("complexity_factors", [])):
        manual.append("OPENROWSET/linked-server references require replacement with Unity Catalog external tables or JDBC sources")
    if "OPENJSON" in str(obj.get("complexity_factors", [])):
        manual.append("OPENJSON has no Spark SQL equivalent — rewrite as PySpark from_json()/explode() against an explicit schema")
    if obj.get("duplicate_definition_files"):
        manual.append(
            "Object definition found in more than one source file — only the first "
            f"({obj.get('source_file')}) was used to build this inventory entry; the following "
            f"file(s) were NOT incorporated and may contain schema changes (e.g. an ALTER script): "
            f"{', '.join(obj['duplicate_definition_files'])}"
        )
    obj["manual_steps"] = manual

    return obj


def _normalise_ssis_task(task: dict[str, Any], pkg_name: str) -> dict[str, Any]:
    """Flatten an SSIS task dict into a canonical inventory item."""
    task_id = f"SSIS:{pkg_name}:{task['name']}"
    unsupported = list(task.get("unsupported") or [])

    score = 0
    if task.get("manual_flag"):
        score += 8
    if task.get("data_flow") and task["data_flow"].get("unsupported"):
        score += 6
    if task.get("task_category") in ("FOR_LOOP", "FOREACH_LOOP"):
        score += 3

    band = "LOW"
    for threshold, label in [(0, "LOW"), (3, "MEDIUM"), (6, "HIGH"), (10, "VERY_HIGH")]:
        if score >= threshold:
            band = label

    confidence = 0.65
    if task.get("manual_flag"):
        confidence -= 0.30
    if unsupported:
        confidence -= 0.20
    confidence = max(0.0, round(confidence, 2))

    return {
        "id":                    task_id,
        "name":                  task["name"],
        "schema":                "Integration",
        "object_type":           f"SSIS_{task['task_category']}",
        "source_project":        "SSIS",
        "source_file":           None,
        "raw_ddl":               None,
        "sql_body":              task.get("sql_body"),
        "expression":            task.get("expression"),
        "data_flow":             task.get("data_flow"),
        "references":            {"tables": [], "procedures": [], "functions": []},
        "etl_semantics":         _infer_ssis_etl_semantics(task),
        "complexity_band":       band,
        "complexity_score":      score,
        "complexity_factors":    [],
        "medallion_layer":       "BRONZE",
        "risk":                  "HIGH" if task.get("manual_flag") else "MEDIUM" if unsupported else "LOW",
        "conversion_confidence": confidence,
        "is_unsupported":        task.get("manual_flag", False),
        "unsupported":           unsupported,
        "manual_steps":          [f"Manual rewrite required: {u}" for u in unsupported],
        "depth":                 task.get("depth", 1),
        "parent_package":        pkg_name,
        "connections":           task.get("connections", []),
        "constraints":           task.get("constraints", []),
    }


def _infer_ssis_etl_semantics(task: dict[str, Any]) -> list[str]:
    semantics: list[str] = []
    name = task.get("name", "").lower()
    sql  = task.get("sql_body", "") or ""

    if "truncate" in name:
        semantics.append("FULL_LOAD")
    if "cutoff" in name or "cutoff" in sql.lower():
        semantics.append("CUTOFF_WINDOW")
    if "staging" in name or "staging" in sql.lower():
        semantics.append("INCREMENTAL")
    if "migrate" in name or "Migrate" in sql:
        semantics.append("STAGING_TO_DW")
    if "dimension" in name.lower():
        semantics.append("DIMENSION_LOAD")
    if "fact" in name.lower():
        semantics.append("FACT_LOAD")
    if "lineage" in name.lower() or "lineagekey" in sql.lower():
        semantics.append("LINEAGE_TRACKING")
    return semantics


def build_inventory(
    sql_objects: list[dict[str, Any]],
    ssis_packages: list[dict[str, Any]],
    output_dir: Path,
) -> dict[str, Any]:
    """
    Merge sql_objects and SSIS packages into a single inventory,
    derive all metadata fields, and write inventory.json.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    items: list[dict[str, Any]] = []
    unsupported_items: list[dict[str, Any]] = []

    # ── SQL objects ──────────────────────────────────────────────────────────
    for obj in sql_objects:
        norm = _normalise_sql_object(obj)
        if norm["is_unsupported"]:
            unsupported_items.append({
                "id":           norm["id"],
                "object_type":  norm["object_type"],
                "source_file":  norm.get("source_file"),
                "reason":       norm.get("error", "Skipped object type"),
                "manual_steps": norm.get("manual_steps", []),
            })
        else:
            items.append(norm)

    # ── SSIS packages + tasks ────────────────────────────────────────────────
    for pkg in ssis_packages:
        pkg_item = {
            "id":                    pkg["id"],
            "name":                  pkg["name"],
            "schema":                "ETL",
            "object_type":           "SSIS_PACKAGE",
            "source_project":        "SSIS",
            "source_file":           pkg.get("source_file"),
            "raw_ddl":               None,
            "references":            {"tables": [], "procedures": [], "functions": []},
            "etl_semantics":         ["ORCHESTRATION"],
            "complexity_band":       "HIGH",
            "complexity_score":      10,
            "complexity_factors":    [],
            "medallion_layer":       "BRONZE",
            "risk":                  "MEDIUM",
            "conversion_confidence": 0.70,
            "is_unsupported":        False,
            "unsupported":           pkg.get("unsupported", []),
            "manual_steps":          [],
            "movement_paths":        pkg.get("movement_paths", []),
            "variables":             pkg.get("variables", []),
            "connection_managers":   list(pkg.get("connection_managers", {}).values()),
        }
        items.append(pkg_item)

        for task in pkg.get("all_tasks_flat", []):
            norm_task = _normalise_ssis_task(task, pkg["name"])
            if norm_task["is_unsupported"]:
                unsupported_items.append({
                    "id":           norm_task["id"],
                    "object_type":  norm_task["object_type"],
                    "source_file":  None,
                    "reason":       f"Manual-only task type: {task['task_category']}",
                    "manual_steps": norm_task["manual_steps"],
                })
            items.append(norm_task)  # include even unsupported tasks in main inventory

    # ── Summary stats ────────────────────────────────────────────────────────
    by_type: dict[str, int] = defaultdict(int)
    by_project: dict[str, int] = defaultdict(int)
    by_layer: dict[str, int] = defaultdict(int)
    by_risk: dict[str, int] = defaultdict(int)
    by_band: dict[str, int] = defaultdict(int)

    for item in items:
        by_type[item["object_type"]] += 1
        by_project[item["source_project"]] += 1
        by_layer[item["medallion_layer"]] += 1
        by_risk[item["risk"]] += 1
        by_band[item["complexity_band"]] += 1

    avg_confidence = (
        round(sum(i["conversion_confidence"] for i in items) / len(items), 3)
        if items else 0.0
    )

    inventory = {
        "version":     "0.1.0",
        "total_objects": len(items),
        "unsupported_count": len(unsupported_items),
        "summary": {
            "by_type":       dict(sorted(by_type.items())),
            "by_project":    dict(sorted(by_project.items())),
            "by_layer":      dict(sorted(by_layer.items())),
            "by_risk":       dict(sorted(by_risk.items())),
            "by_complexity": dict(sorted(by_band.items())),
            "avg_conversion_confidence": avg_confidence,
        },
        "objects": items,
    }

    # Write outputs
    (output_dir / "inventory.json").write_text(
        json.dumps(inventory, indent=2, default=str), encoding="utf-8"
    )
    (output_dir / "unsupported_objects.json").write_text(
        json.dumps({"unsupported": unsupported_items}, indent=2, default=str),
        encoding="utf-8",
    )

    return inventory
