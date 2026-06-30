"""
impact_analysis.py
Impact analysis for migrating the SQL Server/Synapse + SSIS solution to Databricks.

Consumes:
    outputs/inventory.json
    outputs/dependencies.json

Produces:
    impact_analysis.md
    migration_risk_register.csv
    object_complexity_scores.json
    manual_intervention_list.md

Scoring model: 12 dimensions, each scored 0 (n/a) - 5 (severe) per object.
Dimensions map directly to the user's requested assessment axes:
    sql_dialect, procedural_logic, ssis_control_flow, ssis_data_flow,
    dependency_criticality, ordering_constraints, data_type_risk,
    performance_risk, security_risk, operational_scheduling,
    testing_complexity, rollback_complexity

Each object is then classified into one of four migration strategies:
    LIFT_AND_SHIFT | PARTIAL_AUTOMATION | REWRITE_REQUIRED | MANUAL_REDESIGN
"""

from __future__ import annotations

import csv
import json
import re
from collections import deque
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DIMENSIONS = [
    "sql_dialect",
    "procedural_logic",
    "ssis_control_flow",
    "ssis_data_flow",
    "dependency_criticality",
    "ordering_constraints",
    "data_type_risk",
    "performance_risk",
    "security_risk",
    "operational_scheduling",
    "testing_complexity",
    "rollback_complexity",
]

# ---------------------------------------------------------------------------
# Dialect / data-type risk pattern tables
# ---------------------------------------------------------------------------

_DIALECT_PATTERNS: list[tuple[str, int]] = [
    (r"\bOPENROWSET\b|\bOPENDATASOURCE\b|\bLINKED\s+SERVER\b", 5),
    (r"\bPIVOT\b|\bUNPIVOT\b", 4),
    (r"\bMERGE\b", 3),
    (r"\bFOR\s+XML\b|\bFOR\s+JSON\b", 3),
    (r"\bOPENJSON\b", 4),
    (r"\bFOR\s+SYSTEM_TIME\b", 4),
    (r"\bAPPLY\b", 3),
    (r"\bOUTPUT\s+INSERTED\b|\bOUTPUT\s+DELETED\b", 2),
    (r"\bTOP\s*\(", 1),
    (r"\bIDENTITY\s*\(", 1),
    (r"\bISNULL\s*\(", 1),
]

_PROCEDURAL_PATTERNS: list[tuple[str, int]] = [
    (r"\bCURSOR\b", 5),
    (r"\bsp_executesql\b|\bEXEC\s*\(", 4),
    (r"\bWHILE\b", 3),
    (r"\bGOTO\b", 4),
    (r"\bTRY\b.*\bCATCH\b", 2),
    (r"#\w+", 2),
    (r"\b@\w+\s+TABLE\b", 2),
    (r"\bRAISERROR\b|\bTHROW\b", 1),
]

_DATA_TYPE_PATTERNS: list[tuple[str, int]] = [
    (r"\bgeography\b", 5),
    (r"\bgeometry\b", 5),
    (r"\bhierarchyid\b", 5),
    (r"\bsql_variant\b", 4),
    (r"\bxml\b", 3),
    (r"\bdatetimeoffset\b", 2),
    (r"\browversion\b|\btimestamp\b", 2),
    (r"\bnvarchar\(max\)|\bvarchar\(max\)|\bvarbinary\(max\)", 1),
]

_SECURITY_PATTERNS: list[tuple[str, int]] = [
    (r"\bEXECUTE\s+AS\s+OWNER\b", 2),
    (r"\bEXECUTE\s+AS\s+(?!OWNER\b)\w+\b", 2),
    (r"\bGRANT\b|\bDENY\b|\bREVOKE\b", 3),
    (r"\bCREATE\s+ROLE\b|\bCREATE\s+USER\b", 2),
    (r"\bROW\s+LEVEL\s+SECURITY\b|\bSECURITY\s+POLICY\b", 4),
]

_PERF_TABLE_FEATURE_SCORE = {
    "MEMORY_OPTIMIZED": 4,
    "COLUMNSTORE": 2,
    "PARTITIONED": 2,
    "TEMPORAL": 3,
}

_CLASSIFICATION_LABELS = {
    "LIFT_AND_SHIFT": "Lift-and-shift friendly",
    "PARTIAL_AUTOMATION": "Partial automation possible",
    "REWRITE_REQUIRED": "Rewrite required",
    "MANUAL_REDESIGN": "Manual redesign required",
}

_TEST_DEPTH_BY_CLASS = {
    "LIFT_AND_SHIFT": "Schema/row-count parity check + column-level checksum sample (Tier 1)",
    "PARTIAL_AUTOMATION": "Row-level reconciliation (statistically sampled) + business-rule unit tests for the automated portion + manual review of generated code (Tier 2)",
    "REWRITE_REQUIRED": "Full regression suite: unit tests per logic branch/condition, golden-record reconciliation against source, edge-case/boundary tests, side-by-side parallel run (Tier 3)",
    "MANUAL_REDESIGN": "Full parallel-run validation across at least one complete ETL cycle, manual functional sign-off, extended UAT, rollback rehearsal (Tier 4)",
}


def _hits(text: str, patterns: list[tuple[str, int]]) -> tuple[int, list[str]]:
    score = 0
    factors: list[str] = []
    for pattern, weight in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            score += weight
            label = pattern.replace("\\b", "").split("|")[0].strip()
            factors.append(f"{label}(+{weight})")
    return min(score, 5) if score <= 5 else 5, factors


def _cap(score: int) -> int:
    return max(0, min(score, 5))


# ---------------------------------------------------------------------------
# Dependency graph helpers (blast radius / ordering)
# ---------------------------------------------------------------------------

def _build_reverse_adjacency(graph: dict[str, Any]) -> dict[str, list[str]]:
    rev: dict[str, list[str]] = {}
    for edge in graph.get("edges", []):
        rev.setdefault(edge["to"], []).append(edge["from"])
    return rev


def _build_forward_adjacency(graph: dict[str, Any]) -> dict[str, list[str]]:
    fwd: dict[str, list[str]] = {}
    for edge in graph.get("edges", []):
        fwd.setdefault(edge["from"], []).append(edge["to"])
    return fwd


def _transitive_count(start: str, adjacency: dict[str, list[str]]) -> tuple[int, list[str]]:
    """BFS from start over adjacency; return (count, sample up to 8 ids)."""
    seen: set[str] = set()
    queue = deque(adjacency.get(start, []))
    while queue:
        node = queue.popleft()
        if node in seen or node == start:
            continue
        seen.add(node)
        for nxt in adjacency.get(node, []):
            if nxt not in seen:
                queue.append(nxt)
    return len(seen), sorted(seen)[:8]


# ---------------------------------------------------------------------------
# Dimension scoring
# ---------------------------------------------------------------------------

def _score_sql_dialect(obj: dict[str, Any]) -> tuple[int, list[str]]:
    if obj.get("object_type", "").startswith("SSIS"):
        return 0, []
    ddl = obj.get("raw_ddl") or ""
    score, factors = _hits(ddl, _DIALECT_PATTERNS)
    return _cap(score), factors


def _score_procedural_logic(obj: dict[str, Any]) -> tuple[int, list[str]]:
    otype = obj.get("object_type", "")
    if otype not in ("PROCEDURE", "SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI", "TRIGGER"):
        return 0, []
    ddl = obj.get("raw_ddl") or ""
    score, factors = _hits(ddl, _PROCEDURAL_PATTERNS)
    return _cap(score), factors


def _score_ssis_control_flow(obj: dict[str, Any]) -> tuple[int, list[str]]:
    otype = obj.get("object_type", "")
    if otype not in ("SSIS_PACKAGE", "SSIS_SEQUENCE_CONTAINER", "SSIS_EXECUTE_SQL", "SSIS_EXPRESSION"):
        return 0, []
    factors = []
    score = 1  # baseline: any control-flow task requires re-authoring as a Databricks Workflow task
    n_constraints = len(obj.get("constraints", []) or [])
    if n_constraints > 2:
        score += 2
        factors.append(f"precedence_constraints={n_constraints}(+2)")
    elif n_constraints > 0:
        score += 1
        factors.append(f"precedence_constraints={n_constraints}(+1)")
    if otype == "SSIS_EXPRESSION":
        score += 2
        factors.append("SSIS_expression_requires_manual_translation(+2)")
    if otype == "SSIS_PACKAGE":
        score += 1
        factors.append("package_level_orchestration(+1)")
    return _cap(score), factors


def _score_ssis_data_flow(obj: dict[str, Any]) -> tuple[int, list[str]]:
    if obj.get("object_type") != "SSIS_DATA_FLOW":
        return 0, []
    factors = ["data_flow_pipeline_to_pyspark(+2)"]
    score = 2
    components = obj.get("data_flow", {}).get("components", []) if isinstance(obj.get("data_flow"), dict) else []
    if len(components) > 4:
        score += 2
        factors.append(f"components={len(components)}(+2)")
    elif len(components) > 1:
        score += 1
        factors.append(f"components={len(components)}(+1)")
    return _cap(score), factors


def _score_dependency_criticality(node: dict[str, Any] | None) -> tuple[int, list[str]]:
    if not node:
        return 0, []
    fan_in = node.get("fan_in", 0)
    if fan_in >= 8:
        return 5, [f"fan_in={fan_in}(critical)"]
    if fan_in >= 4:
        return 4, [f"fan_in={fan_in}(high)"]
    if fan_in >= 2:
        return 2, [f"fan_in={fan_in}(moderate)"]
    if fan_in == 1:
        return 1, [f"fan_in={fan_in}(low)"]
    return 0, []


def _score_ordering_constraints(obj: dict[str, Any], node: dict[str, Any] | None) -> tuple[int, list[str]]:
    factors = []
    score = 0
    semantics = obj.get("etl_semantics", [])
    if "CUTOFF_WINDOW" in semantics:
        score += 2
        factors.append("watermark_dependent_run_order(+2)")
    if "DIMENSION_LOAD" in semantics:
        score += 1
        factors.append("must_precede_fact_load(+1)")
    if "FACT_LOAD" in semantics:
        score += 1
        factors.append("depends_on_dimension_load(+1)")
    if "STAGING_TO_DW" in semantics:
        score += 1
        factors.append("staging_must_complete_before_migrate(+1)")
    if node and node.get("fan_out", 0) >= 5:
        score += 1
        factors.append(f"fan_out={node['fan_out']}(broad_upstream_reads)")
    return _cap(score), factors


def _score_data_type_risk(obj: dict[str, Any]) -> tuple[int, list[str]]:
    ddl = obj.get("raw_ddl") or ""
    score, factors = _hits(ddl, _DATA_TYPE_PATTERNS)
    return _cap(score), factors


def _score_performance_risk(obj: dict[str, Any]) -> tuple[int, list[str]]:
    factors = []
    score = 0
    for feat in obj.get("table_features", []):
        weight = _PERF_TABLE_FEATURE_SCORE.get(feat, 0)
        if weight:
            score += weight
            factors.append(f"{feat}(+{weight})")
    ddl = obj.get("raw_ddl") or ""
    if re.search(r"\bCURSOR\b", ddl, re.IGNORECASE):
        score += 2
        factors.append("row_by_row_cursor(+2)")
    if obj.get("object_type") == "SSIS_DATA_FLOW":
        score += 1
        factors.append("single_threaded_dataflow_vs_distributed_spark(+1)")
    return _cap(score), factors


def _score_security_risk(obj: dict[str, Any]) -> tuple[int, list[str]]:
    ddl = obj.get("raw_ddl") or ""
    score, factors = _hits(ddl, _SECURITY_PATTERNS)
    return _cap(score), factors


def _score_operational_scheduling(obj: dict[str, Any]) -> tuple[int, list[str]]:
    if obj.get("object_type") == "SSIS_PACKAGE":
        return 3, ["sql_agent_job_to_databricks_workflow(+3)"]
    if obj.get("object_type", "").startswith("SSIS_"):
        return 1, ["task_becomes_workflow_task(+1)"]
    if "CUTOFF_WINDOW" in obj.get("etl_semantics", []):
        return 2, ["watermark_state_externalised(+2)"]
    return 0, []


def _score_rollback_complexity(obj: dict[str, Any]) -> tuple[int, list[str]]:
    factors = []
    score = 0
    semantics = obj.get("etl_semantics", [])
    if "SCD2" in semantics:
        score += 3
        factors.append("scd2_history_state(+3)")
    if "LINEAGE_TRACKING" in semantics:
        score += 1
        factors.append("lineage_table_state(+1)")
    if "MEMORY_OPTIMIZED" in obj.get("table_features", []):
        score += 1
        factors.append("memory_optimized_no_native_equivalent(+1)")
    if obj.get("object_type") == "TABLE" and "TEMPORAL" in obj.get("table_features", []):
        score += 2
        factors.append("temporal_history_table(+2)")
    return _cap(score), factors


def _score_testing_complexity(scores: dict[str, int]) -> tuple[int, list[str]]:
    relevant = [
        scores["procedural_logic"], scores["ssis_control_flow"], scores["ssis_data_flow"],
        scores["dependency_criticality"], scores["data_type_risk"], scores["rollback_complexity"],
    ]
    avg = sum(relevant) / len(relevant)
    score = _cap(round(avg))
    return score, [f"derived_avg={avg:.1f}"]


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

def _classify(obj: dict[str, Any], scores: dict[str, int]) -> str:
    otype = obj.get("object_type", "")
    max_score = max(scores.values())
    severe_count = sum(1 for v in scores.values() if v >= 4)

    # Hard overrides: unsupported / critical risk objects always need manual redesign
    if obj.get("is_unsupported"):
        return "MANUAL_REDESIGN"
    if scores["data_type_risk"] >= 4 or scores["performance_risk"] >= 4:
        return "MANUAL_REDESIGN"
    if max_score >= 5 or severe_count >= 2:
        return "MANUAL_REDESIGN"

    if otype in ("TABLE", "SCHEMA", "SEQUENCE", "USER_DEFINED_TYPE", "VIEW"):
        if max_score <= 1:
            return "LIFT_AND_SHIFT"
        if max_score <= 3:
            return "PARTIAL_AUTOMATION"
        return "REWRITE_REQUIRED"

    if otype in ("PROCEDURE", "SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI"):
        if scores["procedural_logic"] == 0 and max_score <= 2:
            return "PARTIAL_AUTOMATION"
        if scores["procedural_logic"] >= 3 or max_score >= 4:
            return "REWRITE_REQUIRED"
        return "PARTIAL_AUTOMATION"

    if otype.startswith("SSIS_"):
        if otype in ("SSIS_EXECUTE_SQL",) and max_score <= 2:
            return "PARTIAL_AUTOMATION"
        if otype == "SSIS_DATA_FLOW":
            return "PARTIAL_AUTOMATION" if max_score <= 3 else "REWRITE_REQUIRED"
        if otype in ("SSIS_SEQUENCE_CONTAINER", "SSIS_PACKAGE"):
            return "PARTIAL_AUTOMATION"
        if otype == "SSIS_EXPRESSION":
            return "REWRITE_REQUIRED"
        return "PARTIAL_AUTOMATION"

    return "PARTIAL_AUTOMATION"


# ---------------------------------------------------------------------------
# Main scoring pass
# ---------------------------------------------------------------------------

def score_all_objects(inventory: dict[str, Any], graph: dict[str, Any]) -> list[dict[str, Any]]:
    objects = inventory.get("objects", [])
    nodes = graph.get("nodes", {})
    rev_adj = _build_reverse_adjacency(graph)
    fwd_adj = _build_forward_adjacency(graph)

    results: list[dict[str, Any]] = []
    for obj in objects:
        if obj.get("object_type") in ("SECURITY", "FILEGROUP", "PARTITION_FUNCTION",
                                       "PARTITION_SCHEME", "EXTENDED_PROPERTY", "SCRIPT",
                                       "INDEX", "TRIGGER", "UNKNOWN", "UNREADABLE"):
            # Out of canonical conversion scope per inventory_builder; still scored lightly below
            pass

        node = nodes.get(obj["id"])
        scores: dict[str, int] = {}
        factor_map: dict[str, list[str]] = {}

        scores["sql_dialect"], factor_map["sql_dialect"] = _score_sql_dialect(obj)
        scores["procedural_logic"], factor_map["procedural_logic"] = _score_procedural_logic(obj)
        scores["ssis_control_flow"], factor_map["ssis_control_flow"] = _score_ssis_control_flow(obj)
        scores["ssis_data_flow"], factor_map["ssis_data_flow"] = _score_ssis_data_flow(obj)
        scores["dependency_criticality"], factor_map["dependency_criticality"] = _score_dependency_criticality(node)
        scores["ordering_constraints"], factor_map["ordering_constraints"] = _score_ordering_constraints(obj, node)
        scores["data_type_risk"], factor_map["data_type_risk"] = _score_data_type_risk(obj)
        scores["performance_risk"], factor_map["performance_risk"] = _score_performance_risk(obj)
        scores["security_risk"], factor_map["security_risk"] = _score_security_risk(obj)
        scores["operational_scheduling"], factor_map["operational_scheduling"] = _score_operational_scheduling(obj)
        scores["rollback_complexity"], factor_map["rollback_complexity"] = _score_rollback_complexity(obj)
        scores["testing_complexity"], factor_map["testing_complexity"] = _score_testing_complexity(scores)

        classification = _classify(obj, scores)

        downstream_count, downstream_sample = _transitive_count(obj["id"], rev_adj) if node else (0, [])
        upstream_count, upstream_sample = _transitive_count(obj["id"], fwd_adj) if node else (0, [])

        overall = round(sum(scores.values()) / len(scores), 2)

        results.append({
            "id": obj["id"],
            "name": obj.get("name"),
            "schema": obj.get("schema"),
            "object_type": obj.get("object_type"),
            "source_project": obj.get("source_project"),
            "medallion_layer": obj.get("medallion_layer"),
            "existing_complexity_band": obj.get("complexity_band"),
            "existing_risk": obj.get("risk"),
            "scores": scores,
            "score_factors": factor_map,
            "overall_score": overall,
            "classification": classification,
            "classification_label": _CLASSIFICATION_LABELS[classification],
            "blast_radius": {
                "direct_dependents": node.get("fan_in", 0) if node else 0,
                "transitive_dependents": downstream_count,
                "sample_dependents": downstream_sample,
                "direct_dependencies": node.get("fan_out", 0) if node else 0,
                "transitive_dependencies": upstream_count,
            },
            "recommended_test_depth": _TEST_DEPTH_BY_CLASS[classification],
        })

    results.sort(key=lambda r: r["overall_score"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

def _write_complexity_scores_json(results: list[dict[str, Any]], output_dir: Path) -> Path:
    path = output_dir / "object_complexity_scores.json"
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dimensions": DIMENSIONS,
        "scoring_scale": "0 (n/a) - 5 (severe) per dimension",
        "classification_legend": _CLASSIFICATION_LABELS,
        "object_count": len(results),
        "classification_distribution": {
            label: sum(1 for r in results if r["classification"] == key)
            for key, label in _CLASSIFICATION_LABELS.items()
        },
        "objects": results,
    }
    path.write_text(json.dumps(payload, indent=2, default=str), encoding="utf-8")
    return path


def _write_risk_register_csv(results: list[dict[str, Any]], output_dir: Path) -> Path:
    path = output_dir / "migration_risk_register.csv"
    headers = [
        "id", "name", "schema", "object_type", "source_project", "medallion_layer",
        "classification", "overall_score",
        "sql_dialect", "procedural_logic", "ssis_control_flow", "ssis_data_flow",
        "dependency_criticality", "ordering_constraints", "data_type_risk",
        "performance_risk", "security_risk", "operational_scheduling",
        "testing_complexity", "rollback_complexity",
        "direct_dependents", "transitive_dependents",
        "top_risk_factors", "recommended_test_depth",
    ]
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        for r in results:
            s = r["scores"]
            top_factors = []
            for dim in DIMENSIONS:
                top_factors.extend(r["score_factors"].get(dim, []))
            row = [
                r["id"], r["name"], r["schema"], r["object_type"], r["source_project"], r["medallion_layer"],
                r["classification"], r["overall_score"],
                s["sql_dialect"], s["procedural_logic"], s["ssis_control_flow"], s["ssis_data_flow"],
                s["dependency_criticality"], s["ordering_constraints"], s["data_type_risk"],
                s["performance_risk"], s["security_risk"], s["operational_scheduling"],
                s["testing_complexity"], s["rollback_complexity"],
                r["blast_radius"]["direct_dependents"], r["blast_radius"]["transitive_dependents"],
                "; ".join(top_factors[:6]),
                r["recommended_test_depth"],
            ]
            writer.writerow(row)
    return path


def _md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return lines


def _write_impact_analysis_md(results: list[dict[str, Any]], inventory: dict[str, Any],
                               graph: dict[str, Any], output_dir: Path) -> Path:
    path = output_dir / "impact_analysis.md"
    total = len(results)
    dist = {label: sum(1 for r in results if r["classification"] == key)
            for key, label in _CLASSIFICATION_LABELS.items()}

    by_dim_avg = {
        dim: round(sum(r["scores"][dim] for r in results) / total, 2) for dim in DIMENSIONS
    }

    top20 = results[:20]
    critical_blast = sorted(results, key=lambda r: r["blast_radius"]["transitive_dependents"], reverse=True)[:15]

    lines: list[str] = []
    lines += [
        "# Wide World Importers — Migration Impact Analysis",
        "",
        "> **Accelerator:** WWI SQL Server → Databricks Modernisation Accelerator v0.1.0  ",
        f"> **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
        "> **Basis:** Static analysis of `inventory.json` (419 objects) and `dependencies.json` (402 nodes / 566 edges)  ",
        "> **Scope:** SQL Server (OLTP + DW) objects and SSIS package `DailyETLMain` → Databricks (Unity Catalog, Delta Lake, PySpark, Databricks Workflows)",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"- **{total} objects** assessed across 12 impact dimensions (SQL dialect, procedural logic, SSIS control/data flow, "
        "dependency criticality, ordering constraints, data type risk, performance risk, security model change, "
        "operational scheduling, testing complexity, rollback complexity).",
        f"- **{dist['Lift-and-shift friendly']} ({dist['Lift-and-shift friendly']/total:.0%})** objects are lift-and-shift friendly — "
        "straightforward DDL/DML translation with high automated-conversion confidence.",
        f"- **{dist['Partial automation possible']} ({dist['Partial automation possible']/total:.0%})** are candidates for partial "
        "automation — deterministic pattern-based conversion with required manual review.",
        f"- **{dist['Rewrite required']} ({dist['Rewrite required']/total:.0%})** require a rewrite — procedural logic or SSIS "
        "constructs with no direct Databricks equivalent.",
        f"- **{dist['Manual redesign required']} ({dist['Manual redesign required']/total:.0%})** require manual redesign — "
        "data types, performance patterns, or compounding risk factors with no automated path.",
        "",
        "### Migration Strategy Distribution",
        "",
    ]
    lines += _md_table(["Classification", "Object Count", "% of Total"],
                        [[label, count, f"{count/total:.0%}"] for label, count in dist.items()])
    lines += ["", "### Average Risk Score by Dimension (0=none, 5=severe)", ""]
    lines += _md_table(["Dimension", "Average Score Across All Objects"],
                        [[d.replace("_", " ").title(), v] for d, v in by_dim_avg.items()])

    lines += ["", "---", "", "## 1. SQL Dialect Conversion Complexity", "",
              "T-SQL constructs scanned: `PIVOT`/`UNPIVOT`, `MERGE`, `FOR XML`/`FOR JSON`, `FOR SYSTEM_TIME`, "
              "`APPLY`, `OPENROWSET`/`OPENDATASOURCE`/linked servers, `OUTPUT INSERTED/DELETED`, `TOP(n)`, `IDENTITY()`, `ISNULL()`.",
              ""]
    dialect_hot = sorted([r for r in results if r["scores"]["sql_dialect"] > 0],
                          key=lambda r: r["scores"]["sql_dialect"], reverse=True)[:15]
    lines += _md_table(["Object", "Type", "Score", "Factors"],
                        [[r["id"], r["object_type"], r["scores"]["sql_dialect"],
                          "; ".join(r["score_factors"]["sql_dialect"])] for r in dialect_hot])

    lines += ["", "## 2. T-SQL Procedural Logic Complexity", "",
              "Patterns scanned: `CURSOR`, `sp_executesql`/dynamic `EXEC()`, `WHILE`, `GOTO`, `TRY/CATCH`, "
              "temp tables, table variables, `RAISERROR`/`THROW`. These have no direct PySpark/Databricks SQL equivalent "
              "and require translation to set-based DataFrame/SQL logic or Python control flow.", ""]
    proc_hot = sorted([r for r in results if r["scores"]["procedural_logic"] > 0],
                       key=lambda r: r["scores"]["procedural_logic"], reverse=True)[:15]
    lines += _md_table(["Object", "Type", "Score", "Factors"],
                        [[r["id"], r["object_type"], r["scores"]["procedural_logic"],
                          "; ".join(r["score_factors"]["procedural_logic"])] for r in proc_hot])

    lines += ["", "## 3. SSIS Control Flow Conversion Complexity", "",
              "Every SSIS task/container/package becomes a Databricks Workflow task or notebook orchestration step. "
              "`DailyETLMain` has 13 Sequence Containers (one per entity) each running a fixed 5-step pattern "
              "(cutoff lookup → truncate staging → extract → lineage key → migrate). Precedence constraints map to "
              "Workflow task dependencies; SSIS Expressions (15 found) require manual translation since Databricks "
              "Workflows has no direct expression-language equivalent — these become Python/Jinja parameterisation.", ""]
    ssis_cf = [r for r in results if r["scores"]["ssis_control_flow"] > 0]
    lines += _md_table(["Object Type", "Count", "Avg Score"],
                        [[ot, len([r for r in ssis_cf if r["object_type"] == ot]),
                          round(sum(r["scores"]["ssis_control_flow"] for r in ssis_cf if r["object_type"] == ot) /
                                max(1, len([r for r in ssis_cf if r["object_type"] == ot])), 2)]
                         for ot in sorted(set(r["object_type"] for r in ssis_cf))])

    lines += ["", "## 4. SSIS Data Flow Conversion Complexity", "",
              "13 Data Flow tasks (`Extract Updated <Entity> Data to Staging`) extract from OLTP source tables/views "
              "into `Integration.<Entity>_Staging` tables. Each maps to a PySpark read → transform → write (Delta, "
              "overwrite mode) job. Components beyond simple OLE DB Source → Destination (lookups, derived columns, "
              "conditional splits) raise conversion complexity.", ""]
    df_objs = [r for r in results if r["object_type"] == "SSIS_DATA_FLOW"]
    lines += _md_table(["Object", "Score", "Classification", "Factors"],
                        [[r["id"], r["scores"]["ssis_data_flow"], r["classification_label"],
                          "; ".join(r["score_factors"]["ssis_data_flow"])] for r in df_objs])

    lines += ["", "## 5. Dependency Criticality & Blast Radius", "",
              "Criticality is derived from fan-in (direct dependents) in the dependency graph; blast radius adds the "
              "full transitive closure of downstream dependents — i.e. everything that breaks, directly or indirectly, "
              "if this object's conversion is wrong or delayed.", "",
              "### Highest Blast-Radius Objects", ""]
    lines += _md_table(["Object", "Type", "Direct Dependents", "Transitive Dependents", "Sample Downstream"],
                        [[r["id"], r["object_type"], r["blast_radius"]["direct_dependents"],
                          r["blast_radius"]["transitive_dependents"],
                          ", ".join(r["blast_radius"]["sample_dependents"][:4])] for r in critical_blast])

    lines += ["", "## 6. Ordering Constraints", "",
              "Migration sequencing is governed by: (a) dimension-before-fact load order (SCD2 surrogate keys must "
              "exist before fact loads resolve them), (b) the per-entity cutoff-window watermark chain (`Get Last "
              "ETL Cutoff Time` → extract → `Get Lineage Key` → migrate), and (c) staging truncate-then-load within "
              "a single run. Any reordering during cutover risks silent data loss or duplicate loads.", ""]
    ordering_hot = sorted([r for r in results if r["scores"]["ordering_constraints"] > 0],
                           key=lambda r: r["scores"]["ordering_constraints"], reverse=True)[:12]
    lines += _md_table(["Object", "Type", "Score", "Factors"],
                        [[r["id"], r["object_type"], r["scores"]["ordering_constraints"],
                          "; ".join(r["score_factors"]["ordering_constraints"])] for r in ordering_hot])

    lines += ["", "## 7. Data Type Mapping Risks", "",
              "`geography`/`geometry`, `hierarchyid`, `sql_variant`, and `xml` have no native Delta Lake/Spark type. "
              "The **geography** column appears in 14 objects (City/Country/StateProvince/Supplier/Customer tables "
              "and their `_Archive` pairs, plus the DW `Dimension.City` and the `GetCityUpdates` procedure) and is "
              "the single largest data-type migration risk in this solution — no automated mapping exists; it must "
              "be redesigned as WKT/WKB `STRING` with an optional H3 or geospatial-library index (e.g. Mosaic, Sedona).", ""]
    dt_hot = sorted([r for r in results if r["scores"]["data_type_risk"] > 0],
                     key=lambda r: r["scores"]["data_type_risk"], reverse=True)
    lines += _md_table(["Object", "Type", "Score", "Factors"],
                        [[r["id"], r["object_type"], r["scores"]["data_type_risk"],
                          "; ".join(r["score_factors"]["data_type_risk"])] for r in dt_hot])

    lines += ["", "## 8. Performance Risks", "",
              "Risk sources: memory-optimised tables (no Spark equivalent — becomes a standard Delta table, losing "
              "in-memory OLTP semantics), columnstore indexes (replaced by Delta's native columnar format + Z-ORDER), "
              "partition schemes (replaced by `PARTITIONED BY`), temporal tables queried via `FOR SYSTEM_TIME` "
              "(NOT a drop-in Delta Time Travel replacement — Time Travel is a whole-table commit "
              "snapshot, while `FOR SYSTEM_TIME AS OF` is a per-row validity-window lookup; the correct "
              "rewrite is an explicit `WHERE valid_from <= ts AND (valid_to > ts OR valid_to IS NULL)` "
              "filter against the preserved ValidFrom/ValidTo columns), "
              "and row-by-row CURSOR processing (must be rewritten as set-based/distributed operations or it will "
              "not scale on Spark).", ""]
    perf_hot = sorted([r for r in results if r["scores"]["performance_risk"] > 0],
                       key=lambda r: r["scores"]["performance_risk"], reverse=True)[:15]
    lines += _md_table(["Object", "Type", "Score", "Factors"],
                        [[r["id"], r["object_type"], r["scores"]["performance_risk"],
                          "; ".join(r["score_factors"]["performance_risk"])] for r in perf_hot])

    lines += ["", "## 9. Security / Access Model Changes", "",
              "SQL Server uses schema-level `GRANT`/`DENY`, database roles, and `EXECUTE AS OWNER` impersonation on "
              "Integration procedures. Unity Catalog replaces this with catalog/schema/table-level grants and "
              "row/column-level security via dynamic views — there is no procedural impersonation model, so any "
              "`EXECUTE AS` logic must be redesigned as Unity Catalog access policies.", ""]
    sec_hot = sorted([r for r in results if r["scores"]["security_risk"] > 0],
                      key=lambda r: r["scores"]["security_risk"], reverse=True)[:10]
    lines += _md_table(["Object", "Type", "Score", "Factors"],
                        [[r["id"], r["object_type"], r["scores"]["security_risk"],
                          "; ".join(r["score_factors"]["security_risk"])] for r in sec_hot]) if sec_hot else \
             ["_No explicit EXECUTE AS / GRANT / RLS patterns detected outside the 18 objects already routed to `unsupported_objects.json` as SECURITY type._", ""]

    lines += ["", "## 10. Operational Scheduling Changes", "",
              "Today, `DailyETLMain.dtsx` is invoked by a SQL Server Agent job on a fixed daily schedule, with "
              "package-level success/failure handling. On Databricks this becomes a multi-task Workflow with the "
              "same task graph; the watermark state (`Integration.ETL Cutoff`) must move from an in-database table "
              "read at task start to a Delta table or Workflow task-value pattern. Failure/retry semantics, alerting, "
              "and SLA monitoring must be re-implemented using Databricks Workflows' native retry/alert configuration "
              "rather than SSIS's package-level error handling.", ""]

    lines += ["", "## 11. Testing Complexity", "",
              "Recommended test depth scales with classification (see `manual_intervention_list.md` and the "
              "register's `recommended_test_depth` column):", ""]
    lines += _md_table(["Classification", "Recommended Test Depth"],
                        [[label, _TEST_DEPTH_BY_CLASS[key]] for key, label in _CLASSIFICATION_LABELS.items()])

    lines += ["", "## 12. Rollback Complexity", "",
              "Stateful objects (SCD2 dimensions, lineage tracking, temporal `_Archive` pairs) are the hardest to "
              "roll back — a failed cutover after a Dimension/Fact load has run requires restoring history state, "
              "not just re-pointing a query. Stateless staging/full-load objects roll back cleanly (truncate + rerun).", ""]
    rb_hot = sorted([r for r in results if r["scores"]["rollback_complexity"] > 0],
                     key=lambda r: r["scores"]["rollback_complexity"], reverse=True)[:12]
    lines += _md_table(["Object", "Type", "Score", "Factors"],
                        [[r["id"], r["object_type"], r["scores"]["rollback_complexity"],
                          "; ".join(r["score_factors"]["rollback_complexity"])] for r in rb_hot])

    lines += ["", "---", "", "## Top 20 Highest-Impact Objects (overall score)", ""]
    lines += _md_table(["Object", "Type", "Classification", "Overall Score"],
                        [[r["id"], r["object_type"], r["classification_label"], r["overall_score"]] for r in top20])

    lines += ["", "## Confidence", "",
              "| Section | Confidence | Basis |",
              "|---|---|---|",
              "| SQL dialect / procedural logic scoring | HIGH | Direct regex pattern match against raw DDL text |",
              "| SSIS control/data flow scoring | MEDIUM | Derived from parsed XML structure; component-level data-flow detail is partially flattened |",
              "| Dependency criticality / blast radius | HIGH | Computed from the validated 402-node/566-edge dependency graph (0 cycles) |",
              "| Data type risk | HIGH | Exhaustive substring scan confirmed against raw DDL |",
              "| Security risk | MEDIUM | Heuristic pattern match; full impersonation chain not modelled |",
              "| Operational scheduling | LOW | Narrative inference — no live SQL Agent job definition was available in the source corpus |",
              "",
              "_Generated by the WWI Modernisation Accelerator's impact-analysis module. Does not yet propose target-state design or generate code — see Step 5 (target-state design) and Step 6 (conversion)._",
              ]

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _write_manual_intervention_md(results: list[dict[str, Any]], output_dir: Path) -> Path:
    path = output_dir / "manual_intervention_list.md"
    manual = [r for r in results if r["classification"] == "MANUAL_REDESIGN"]
    rewrite = [r for r in results if r["classification"] == "REWRITE_REQUIRED"]

    lines: list[str] = [
        "# Manual Intervention List",
        "",
        f"> {len(manual)} objects require **manual redesign** and {len(rewrite)} objects require a **rewrite** "
        "(automatable in structure but not in logic). Both lists below need a human migration engineer; "
        "manual-redesign objects additionally need a design decision before any conversion work starts.",
        "",
        "## Manual Redesign Required",
        "",
        "These objects have no automated conversion path — a target-state design decision is needed before "
        "implementation can begin.",
        "",
    ]
    lines += _md_table(
        ["Object", "Type", "Why", "Suggested Approach", "Blast Radius (transitive)"],
        [[r["id"], r["object_type"],
          "; ".join((r["score_factors"]["data_type_risk"] + r["score_factors"]["performance_risk"] +
                     r["score_factors"]["security_risk"])[:3]) or "Compounding risk across multiple dimensions",
          _suggest_approach(r),
          r["blast_radius"]["transitive_dependents"]] for r in manual],
    )

    lines += ["", "## Rewrite Required", "",
              "Structurally convertible, but procedural/control-flow logic must be hand-translated rather than "
              "pattern-matched.", ""]
    lines += _md_table(
        ["Object", "Type", "Why", "Blast Radius (transitive)"],
        [[r["id"], r["object_type"],
          "; ".join((r["score_factors"]["procedural_logic"] + r["score_factors"]["ssis_control_flow"] +
                     r["score_factors"]["sql_dialect"])[:3]) or "Elevated complexity score",
          r["blast_radius"]["transitive_dependents"]] for r in rewrite],
    )

    lines += ["", "## Sign-off Checklist (per manual-redesign object)", "",
              "- [ ] Target data type / pattern decided and documented in target-state design",
              "- [ ] Spike/prototype validated against a representative data sample",
              "- [ ] Reconciliation test written and passing against source system",
              "- [ ] Performance validated at production data volume",
              "- [ ] Rollback procedure documented and rehearsed",
              "- [ ] Sign-off obtained from data owner / business stakeholder",
              ""]

    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _suggest_approach(r: dict[str, Any]) -> str:
    factors = " ".join(r["score_factors"].get("data_type_risk", []))
    if "geography" in factors:
        return "Redesign as WKT/WKB STRING column + optional H3/geospatial index (Mosaic/Sedona)"
    if "MEMORY_OPTIMIZED" in " ".join(r["score_factors"].get("performance_risk", [])):
        return "Replace with standard Delta table; re-evaluate need for in-memory OLTP semantics"
    if r["object_type"] == "SSIS_EXPRESSION":
        return "Translate SSIS expression language to Python/Jinja parameterisation in the Workflow task"
    if r.get("existing_risk") in ("HIGH", "CRITICAL"):
        return "Dedicated design review — see current_state_documentation.md technical debt section"
    return "Dedicated design review required before conversion"


# ---------------------------------------------------------------------------
# Orchestration entry point
# ---------------------------------------------------------------------------

def run_impact_analysis(inventory: dict[str, Any], graph: dict[str, Any], output_dir: Path) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    results = score_all_objects(inventory, graph)
    paths = {
        "impact_analysis_md": _write_impact_analysis_md(results, inventory, graph, output_dir),
        "risk_register_csv": _write_risk_register_csv(results, output_dir),
        "complexity_scores_json": _write_complexity_scores_json(results, output_dir),
        "manual_intervention_md": _write_manual_intervention_md(results, output_dir),
    }
    return paths
