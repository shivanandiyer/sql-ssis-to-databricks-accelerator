"""
run_conversion.py
Entry point for the SQL object conversion layer.

Reads:
    <input-path>/inventory.json
    <input-path>/object_complexity_scores.json
    <input-path>/medallion_mapping.csv

Writes (under <output-path>/):
    databricks_sql/<layer>/<schema>__<name>.sql
    pyspark/<schema>__<name>.py  [_orchestration.py for split procedures]
    review_required/<schema>__<name>.md
    conversion_manifest.json
    conversion_decisions.md

Usage:
    python run_conversion.py --input-path ./outputs --output-path ./output
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
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

CONVERTIBLE_TYPES = {"TABLE", "VIEW", "PROCEDURE", "SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI"}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Convert SQL Server / Synapse objects to Databricks SQL and PySpark.",
    )
    p.add_argument("--input-path", metavar="DIR", default="./outputs",
                   help="Directory containing inventory.json, object_complexity_scores.json, "
                        "and medallion_mapping.csv. Default: ./outputs")
    p.add_argument("--output-path", metavar="DIR", default="./output",
                   help="Directory to write converted assets into. Default: ./output")
    return p.parse_args()


def _slug(text: str) -> str:
    text = re.sub(r"[^\w]+", "_", text.strip())
    return re.sub(r"_+", "_", text).strip("_").lower()


def _load_medallion_targets(input_dir: Path) -> dict[str, str]:
    path = input_dir / "medallion_mapping.csv"
    targets: dict[str, str] = {}
    if not path.exists():
        return targets
    with path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            targets[row["source_id"]] = row["target_fqn"]
    return targets


def _target_fqn_for(obj: dict[str, Any], medallion_targets: dict[str, str]) -> str:
    if obj["id"] in medallion_targets:
        return medallion_targets[obj["id"]]
    layer      = obj.get("medallion_layer", "BRONZE").lower()
    schema_slug = _slug(obj.get("schema", "default"))
    name_slug   = _slug(obj.get("name", "unknown"))
    proj        = obj.get("source_project", "")
    table_name  = f"{schema_slug}__{name_slug}" if proj == "OLTP" else name_slug
    return f"<catalog>_{{}}.{layer}.{table_name}"


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
    lines += ["", "## Source DDL (for reference)", "", "```sql",
              (obj.get("raw_ddl") or "").strip()[:3000], "```"]
    return "\n".join(lines)


def main() -> None:
    args = _parse_args()
    input_dir  = Path(args.input_path)
    output_dir = Path(args.output_path)

    for required in ("inventory.json", "object_complexity_scores.json"):
        if not (input_dir / required).exists():
            print(f"error: {required} not found in {input_dir}. "
                  "Run previous pipeline steps first.", file=sys.stderr)
            sys.exit(1)

    sql_dir    = output_dir / "databricks_sql"
    pyspark_dir = output_dir / "pyspark"
    review_dir  = output_dir / "review_required"
    for d in (sql_dir, pyspark_dir, review_dir):
        d.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    inventory         = json.loads((input_dir / "inventory.json").read_text(encoding="utf-8"))
    complexity        = json.loads((input_dir / "object_complexity_scores.json").read_text(encoding="utf-8"))
    classification_by_id = {o["id"]: o["classification"] for o in complexity["objects"]}
    medallion_targets = _load_medallion_targets(input_dir)

    objects = [o for o in inventory["objects"] if o.get("object_type") in CONVERTIBLE_TYPES]
    print("=" * 60)
    print(f"  Converting {len(objects)} objects")
    print("=" * 60)

    manifest: list[dict[str, Any]] = []
    method_counts: Counter[str] = Counter()
    review_count = 0

    for obj in objects:
        otype          = obj["object_type"]
        target_fqn     = _target_fqn_for(obj, medallion_targets)
        layer          = obj.get("medallion_layer", "BRONZE")
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
            result   = convert_table(obj, target_fqn)
            sql_path = sql_dir / layer.lower() / f"{_slug(obj['schema'])}__{_slug(obj['name'])}.sql"
            _write(sql_path, result["sql"])
            entry["files_written"].append(str(sql_path.relative_to(output_dir)))
            entry["conversion_method"] = "databricks_sql"
            method_counts["databricks_sql"] += 1

        elif otype == "VIEW":
            result   = convert_view(obj, target_fqn)
            sql_path = sql_dir / layer.lower() / f"{_slug(obj['schema'])}__{_slug(obj['name'])}.sql"
            _write(sql_path, result["sql"])
            entry["files_written"].append(str(sql_path.relative_to(output_dir)))
            entry["conversion_method"] = "databricks_sql"
            method_counts["databricks_sql"] += 1

        elif otype in ("SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI"):
            result = convert_function(obj, target_fqn)
            if "sql" in result:
                sql_path = sql_dir / layer.lower() / f"{_slug(obj['schema'])}__{_slug(obj['name'])}.sql"
                _write(sql_path, result["sql"])
                entry["files_written"].append(str(sql_path.relative_to(output_dir)))
                entry["conversion_method"] = "databricks_sql"
                method_counts["databricks_sql"] += 1
            else:
                py_path = pyspark_dir / f"{_slug(obj['schema'])}__{_slug(obj['name'])}.py"
                _write(py_path, result["pyspark"])
                entry["files_written"].append(str(py_path.relative_to(output_dir)))
                entry["conversion_method"] = "pyspark"
                method_counts["pyspark"] += 1

        elif otype == "PROCEDURE":
            result    = convert_procedure(obj, classification or "PARTIAL_AUTOMATION", target_fqn)
            files     = result["files"]
            base_name = f"{_slug(obj['schema'])}__{_slug(obj['name'])}"
            if "databricks_sql" in files:
                sql_path = sql_dir / layer.lower() / f"{base_name}.sql"
                _write(sql_path, files["databricks_sql"])
                entry["files_written"].append(str(sql_path.relative_to(output_dir)))
            if "pyspark" in files:
                suffix  = "_orchestration" if result.get("split") else ""
                py_path = pyspark_dir / f"{base_name}{suffix}.py"
                _write(py_path, files["pyspark"])
                entry["files_written"].append(str(py_path.relative_to(output_dir)))
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

        entry["warnings"]     = result["warnings"]
        entry["needs_review"] = result["needs_review"]
        if result["needs_review"]:
            review_count += 1
            base_name   = f"{_slug(obj['schema'])}__{_slug(obj['name'])}"
            review_path = review_dir / f"{base_name}.md"
            _write(review_path, _review_doc(obj, result["warnings"], classification))
            entry["files_written"].append(str(review_path.relative_to(output_dir)))

        manifest.append(entry)

    manifest_payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "object_count": len(manifest),
        "conversion_method_distribution": dict(method_counts),
        "needs_review_count": review_count,
        "objects": manifest,
    }
    (output_dir / "conversion_manifest.json").write_text(
        json.dumps(manifest_payload, indent=2, default=str), encoding="utf-8"
    )
    _write_decisions_doc(output_dir, manifest, method_counts, review_count)

    elapsed = time.time() - t0
    print(f"  Objects converted : {len(manifest)}")
    print(f"  Method distribution: {dict(method_counts)}")
    print(f"  Needs review      : {review_count}")
    print(f"\n  Completed in {elapsed:.1f}s")
    print(f"  Outputs written to: {output_dir.resolve()}")
    print(f"  Next step: python run_ssis_conversion.py --input-path {input_dir} --output-path {output_dir}")


def _write_decisions_doc(output_dir: Path, manifest: list[dict[str, Any]],
                          method_counts: Counter, review_count: int) -> None:
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
        "is logged to `conversion_manifest.json` and, where it blocks safe deployment, to a file "
        "under `review_required/`.",
        "",
        "## Type Mapping Summary",
        "",
        "| SQL Server Type | Databricks Type | Notes |",
        "|---|---|---|",
        "| NVARCHAR/VARCHAR/CHAR/TEXT | STRING | Length bound dropped (Spark STRING is unbounded) |",
        "| INT / BIGINT / SMALLINT / TINYINT | INT / BIGINT / SMALLINT / TINYINT | Direct mapping |",
        "| BIT | BOOLEAN | Direct mapping |",
        "| DECIMAL/NUMERIC(p,s) | DECIMAL(p,s) | Precision/scale preserved |",
        "| MONEY / SMALLMONEY | DECIMAL(19,4) | Matches SQL Server MONEY precision |",
        "| FLOAT / REAL | DOUBLE / FLOAT | Direct mapping |",
        "| DATE | DATE | Direct mapping |",
        "| DATETIME/DATETIME2/SMALLDATETIME | TIMESTAMP | Direct mapping |",
        "| DATETIMEOFFSET | TIMESTAMP | **Review:** UTC offset not preserved |",
        "| TIME | STRING | **Review:** no native Spark TIME type |",
        "| UNIQUEIDENTIFIER | STRING | Direct mapping |",
        "| VARBINARY/BINARY/IMAGE | BINARY | Direct mapping |",
        "| XML | STRING | **Review:** XPath needs reimplementation via xpath_* functions |",
        "| geography/geometry | STRING (WKT) | **Manual review required** |",
        "| hierarchyid | STRING | **Manual review required** |",
        "| sql_variant | STRING | **Manual review required** |",
        "| rowversion/timestamp | BINARY | **Review:** replace with Delta CDF for change-detection |",
        "",
        "## Conversion Method Distribution",
        "",
        "| Method | Object Count |",
        "|---|---|",
    ]
    for method, count in method_counts.most_common():
        lines.append(f"| {method} | {count} |")

    lines += ["", "## Objects Flagged for Manual Review", "",
              "See `review_required/*.md` for full detail per object.", ""]
    review_objs = [m for m in manifest if m["needs_review"]]
    if review_objs:
        lines += ["| Object | Type | Classification | Top Warning |", "|---|---|---|---|"]
        for m in review_objs[:40]:
            top_warning = (m["warnings"][0][:100] + "...") if m["warnings"] else ""
            lines.append(f"| {m['id']} | {m['object_type']} | {m['classification']} | {top_warning} |")
        if len(review_objs) > 40:
            lines.append(f"\n_...and {len(review_objs)-40} more — see `conversion_manifest.json`._")

    (output_dir / "conversion_decisions.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
