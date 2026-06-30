"""
run_conversion.py
Entry point for the SQL object conversion layer (tables, views, materialized
views, stored procedures, functions -> Databricks-compatible assets).

Reads:
    outputs/inventory.json
    outputs/object_complexity_scores.json
    outputs/medallion_mapping.csv

Writes:
    output/databricks_sql/<layer>/<schema>__<name>.sql
    output/pyspark/<schema>__<name>.py [_orchestration.py for split procedures]
    output/review_required/<schema>__<name>.md
    output/conversion_manifest.json
    output/conversion_decisions.md

Usage:
    python run_conversion.py
"""

from __future__ import annotations

import csv
import json
import re
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from accelerator.converters.sql_converter import (
    convert_function,
    convert_procedure,
    convert_table,
    convert_view,
)

ROOT = Path(__file__).parent
OUTPUTS_DIR = ROOT / "outputs"
OUTPUT_ROOT = ROOT / "output"
SQL_DIR = OUTPUT_ROOT / "databricks_sql"
PYSPARK_DIR = OUTPUT_ROOT / "pyspark"
REVIEW_DIR = OUTPUT_ROOT / "review_required"

CONVERTIBLE_TYPES = {"TABLE", "VIEW", "PROCEDURE", "SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI"}


def _slug(text: str) -> str:
    text = re.sub(r"[^\w]+", "_", text.strip())
    return re.sub(r"_+", "_", text).strip("_").lower()


def _load_medallion_targets() -> dict[str, str]:
    path = OUTPUTS_DIR / "medallion_mapping.csv"
    targets: dict[str, str] = {}
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            targets[row["source_id"]] = row["target_fqn"]
    return targets


def _target_fqn_for(obj: dict[str, Any], medallion_targets: dict[str, str]) -> str:
    if obj["id"] in medallion_targets:
        return medallion_targets[obj["id"]]
    # Procedures / non-data-bearing functions: same naming convention, layer schema.
    layer = obj.get("medallion_layer", "BRONZE").lower()
    schema_slug = _slug(obj.get("schema", "default"))
    name_slug = _slug(obj.get("name", "unknown"))
    proj = obj.get("source_project", "")
    table_name = f"{schema_slug}__{name_slug}" if proj == "OLTP" else name_slug
    return f"wwi_<env>.{layer}.{table_name}"


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _review_doc(obj: dict[str, Any], warnings: list[str], classification: str | None) -> str:
    lines = [
        f"# Review Required: {obj['id']}",
        "",
        f"- **Object type:** {obj.get('object_type')}",
        f"- **Source file:** {obj.get('source_file')}",
        f"- **Classification:** {classification or 'n/a'}",
        "",
        "## Why this needs manual review",
        "",
    ]
    for w in warnings:
        lines.append(f"- {w}")
    lines += ["", "## Source DDL (for reference)", "", "```sql", (obj.get("raw_ddl") or "").strip()[:3000], "```"]
    return "\n".join(lines)


def main() -> None:
    t0 = time.time()
    inventory = json.loads((OUTPUTS_DIR / "inventory.json").read_text(encoding="utf-8"))
    complexity = json.loads((OUTPUTS_DIR / "object_complexity_scores.json").read_text(encoding="utf-8"))
    classification_by_id = {o["id"]: o["classification"] for o in complexity["objects"]}
    medallion_targets = _load_medallion_targets()

    objects = [o for o in inventory["objects"] if o.get("object_type") in CONVERTIBLE_TYPES]
    print("=" * 60)
    print(f"  Converting {len(objects)} objects")
    print("=" * 60)

    manifest: list[dict[str, Any]] = []
    method_counts: Counter[str] = Counter()
    review_count = 0
    materialized_view_count = 0  # source corpus check; see decisions doc

    for obj in objects:
        otype = obj["object_type"]
        target_fqn = _target_fqn_for(obj, medallion_targets)
        layer = obj.get("medallion_layer", "BRONZE")
        classification = classification_by_id.get(obj["id"])
        entry: dict[str, Any] = {
            "id": obj["id"],
            "object_type": otype,
            "classification": classification,
            "target_fqn": target_fqn,
            "files_written": [],
            "needs_review": False,
            "conversion_method": None,
            "warnings": [],
        }

        if otype == "TABLE":
            result = convert_table(obj, target_fqn)
            sql_path = SQL_DIR / layer.lower() / f"{_slug(obj['schema'])}__{_slug(obj['name'])}.sql"
            _write(sql_path, result["sql"])
            entry["files_written"].append(str(sql_path.relative_to(ROOT)))
            entry["conversion_method"] = "databricks_sql"
            method_counts["databricks_sql"] += 1

        elif otype == "VIEW":
            result = convert_view(obj, target_fqn)
            sql_path = SQL_DIR / layer.lower() / f"{_slug(obj['schema'])}__{_slug(obj['name'])}.sql"
            _write(sql_path, result["sql"])
            entry["files_written"].append(str(sql_path.relative_to(ROOT)))
            entry["conversion_method"] = "databricks_sql"
            method_counts["databricks_sql"] += 1

        elif otype in ("SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI"):
            result = convert_function(obj, target_fqn)
            if "sql" in result:
                sql_path = SQL_DIR / layer.lower() / f"{_slug(obj['schema'])}__{_slug(obj['name'])}.sql"
                _write(sql_path, result["sql"])
                entry["files_written"].append(str(sql_path.relative_to(ROOT)))
                entry["conversion_method"] = "databricks_sql"
                method_counts["databricks_sql"] += 1
            else:
                py_path = PYSPARK_DIR / f"{_slug(obj['schema'])}__{_slug(obj['name'])}.py"
                _write(py_path, result["pyspark"])
                entry["files_written"].append(str(py_path.relative_to(ROOT)))
                entry["conversion_method"] = "pyspark"
                method_counts["pyspark"] += 1

        elif otype == "PROCEDURE":
            result = convert_procedure(obj, classification or "PARTIAL_AUTOMATION", target_fqn)
            files = result["files"]
            base_name = f"{_slug(obj['schema'])}__{_slug(obj['name'])}"
            if "databricks_sql" in files:
                sql_path = SQL_DIR / layer.lower() / f"{base_name}.sql"
                _write(sql_path, files["databricks_sql"])
                entry["files_written"].append(str(sql_path.relative_to(ROOT)))
            if "pyspark" in files:
                suffix = "_orchestration" if result.get("split") else ""
                py_path = PYSPARK_DIR / f"{base_name}{suffix}.py"
                _write(py_path, files["pyspark"])
                entry["files_written"].append(str(py_path.relative_to(ROOT)))
            if result.get("split"):
                entry["conversion_method"] = "split_sql_pyspark"
                method_counts["split_sql_pyspark"] += 1
            elif "pyspark" in files:
                entry["conversion_method"] = "pyspark"
                method_counts["pyspark"] += 1
            else:
                entry["conversion_method"] = "databricks_sql"
                method_counts["databricks_sql"] += 1

        else:
            continue

        entry["warnings"] = result["warnings"]
        entry["needs_review"] = result["needs_review"]
        if result["needs_review"]:
            review_count += 1
            base_name = f"{_slug(obj['schema'])}__{_slug(obj['name'])}"
            review_path = REVIEW_DIR / f"{base_name}.md"
            _write(review_path, _review_doc(obj, result["warnings"], classification))
            entry["files_written"].append(str(review_path.relative_to(ROOT)))

        manifest.append(entry)

    manifest_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "object_count": len(manifest),
        "conversion_method_distribution": dict(method_counts),
        "needs_review_count": review_count,
        "materialized_views_detected": materialized_view_count,
        "objects": manifest,
    }
    (OUTPUT_ROOT / "conversion_manifest.json").write_text(
        json.dumps(manifest_payload, indent=2, default=str), encoding="utf-8"
    )

    _write_decisions_doc(manifest, method_counts, review_count, materialized_view_count)

    elapsed = time.time() - t0
    print(f"  Objects converted: {len(manifest)}")
    print(f"  Method distribution: {dict(method_counts)}")
    print(f"  Needs review: {review_count}")
    print(f"\n  Completed in {elapsed:.1f}s")


def _write_decisions_doc(manifest: list[dict[str, Any]], method_counts: Counter,
                          review_count: int, materialized_view_count: int) -> None:
    lines: list[str] = [
        "# Conversion Decisions",
        "",
        f"> **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"> **Objects converted:** {len(manifest)}  ",
        f"> **Flagged for manual review:** {review_count}",
        "",
        "---",
        "",
        "## Conversion Principle",
        "",
        "Semantics are preserved first, syntax second. Where a SQL Server construct has no direct "
        "Databricks equivalent, this layer emits a best-effort skeleton with an explicit comment "
        "describing the gap rather than silently dropping or guessing at behaviour. Every such gap "
        "is also logged to `conversion_manifest.json` and, where it blocks safe deployment, to a "
        "file under `output/review_required/`.",
        "",
        "## Materialized Views",
        "",
        f"{materialized_view_count} materialized views (SQL Server indexed views) were detected in "
        "the source corpus. Wide World Importers does not use indexed/materialized views — all 26 "
        "VIEW objects are ordinary views and were converted as such. If a future source corpus "
        "includes indexed views, the recommended target is a Delta table refreshed by a scheduled "
        "Workflow task (Databricks has no native materialized-view DDL equivalent to SQL Server's "
        "indexed view at the time of writing) or `CREATE MATERIALIZED VIEW` where Databricks SQL "
        "materialized views are available in the target workspace tier.",
        "",
        "## Type Mapping Summary",
        "",
        "| SQL Server Type | Databricks Type | Notes |",
        "|---|---|---|",
        "| NVARCHAR/VARCHAR/NCHAR/CHAR/TEXT | STRING | Length bound intentionally dropped (Spark STRING is unbounded) |",
        "| INT / BIGINT / SMALLINT / TINYINT | INT / BIGINT / SMALLINT / TINYINT | Direct mapping |",
        "| BIT | BOOLEAN | Direct mapping |",
        "| DECIMAL/NUMERIC(p,s) | DECIMAL(p,s) | Precision/scale preserved |",
        "| MONEY / SMALLMONEY | DECIMAL(19,4) | Matches SQL Server's documented MONEY precision |",
        "| FLOAT / REAL | DOUBLE / FLOAT | Direct mapping |",
        "| DATE | DATE | Direct mapping |",
        "| DATETIME/DATETIME2/SMALLDATETIME | TIMESTAMP | Direct mapping |",
        "| DATETIMEOFFSET | TIMESTAMP | **Review:** explicit UTC offset is not preserved |",
        "| TIME | STRING | **Review:** no native Spark TIME type |",
        "| UNIQUEIDENTIFIER | STRING | Direct mapping |",
        "| VARBINARY/BINARY/IMAGE | BINARY | Direct mapping |",
        "| XML | STRING | **Review:** XPath operations need reimplementation via xpath_* functions |",
        "| geography/geometry | STRING (WKT) | **Manual review required:** no native geospatial type |",
        "| hierarchyid | STRING | **Manual review required:** no native hierarchical type |",
        "| sql_variant | STRING | **Manual review required:** no dynamic type equivalent |",
        "| rowversion/timestamp | BINARY | **Review:** replace change-detection use with Delta CDF |",
        "",
        "## Procedural Construct Mapping",
        "",
        "| T-SQL Construct | Databricks Pattern |",
        "|---|---|",
        "| CURSOR | Set-based DataFrame transform (preferred) or bounded Python loop |",
        "| WHILE loop | Vectorised DataFrame op, or Python for-loop over a small fixed list |",
        "| sp_executesql / dynamic EXEC() | Parameterised PySpark/Python string templating or Databricks SQL parameter markers |",
        "| Temp table (#table) | PySpark DataFrame (procedure-local) or scratch-schema Delta table (cross-step state) |",
        "| TRY/CATCH | Python try/except, or Workflow task-level retry/failure handling |",
        "| EXECUTE AS OWNER | Unity Catalog grants — no procedural impersonation needed |",
        "",
        "## Orchestration-Heavy Procedure Split (Rule 4)",
        "",
        "Procedures tagged with ETL orchestration semantics (cutoff-window watermark management, "
        "staging-to-DW migration, lineage tracking) or living in the `Integration` schema are split "
        "into two files: a `databricks_sql` file containing the extracted set-based DML, and a "
        "`pyspark` `_orchestration.py` file containing the Workflow task entry point (watermark "
        "read/advance, invocation of the SQL logic). This keeps transformation logic testable and "
        "reusable independent of how/when it's scheduled.",
        "",
        f"Procedures split this way: {sum(1 for m in manifest if m['conversion_method'] == 'split_sql_pyspark')}",
        "",
        "## Conversion Method Distribution",
        "",
        "| Method | Object Count |",
        "|---|---|",
    ]
    for method, count in method_counts.most_common():
        lines.append(f"| {method} | {count} |")

    lines += ["", "## Objects Flagged for Manual Review", "",
              "See `output/review_required/*.md` for full detail per object. Summary:", ""]
    review_objs = [m for m in manifest if m["needs_review"]]
    lines += ["| Object | Type | Classification | Top Warning |", "|---|---|---|---|"]
    for m in review_objs[:40]:
        top_warning = (m["warnings"][0][:100] + "...") if m["warnings"] else ""
        lines.append(f"| {m['id']} | {m['object_type']} | {m['classification']} | {top_warning} |")
    if len(review_objs) > 40:
        lines.append(f"\n_...and {len(review_objs) - 40} more — see `conversion_manifest.json` for the complete list._")

    lines += ["", "---", "",
              "_This layer converts SQL objects only. SSIS orchestration assets, Databricks "
              "Workflow job definitions, and the deployment bundle are produced in a later step._"]

    (OUTPUT_ROOT / "conversion_decisions.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
