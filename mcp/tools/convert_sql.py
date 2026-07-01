"""
mcp/tools/convert_sql.py
Handler for the convert_sql MCP tool.

NOTE ON IMPLEMENTATION: the original spec named four converter modules
(ddl_converter.py, view_converter.py, proc_converter.py, function_converter.py)
that never existed — the real implementation consolidated all four into
accelerator.converters.sql_converter (convert_table / convert_view /
convert_function / convert_procedure), which is what this handler calls. The
per-object conversion logic and disposition rules mirror run_conversion.py.
"""

from __future__ import annotations

import csv
import json
import logging
import re
import time
from pathlib import Path
from typing import Any

from accelerator.converters.sql_converter import (
    convert_function,
    convert_procedure,
    convert_table,
    convert_view,
)

logger = logging.getLogger(__name__)

_CONVERTIBLE_TYPES = {"TABLE", "VIEW", "PROCEDURE", "SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI"}


def _slug(text: str) -> str:
    text = re.sub(r"[^\w]+", "_", text.strip())
    return re.sub(r"_+", "_", text).strip("_").lower()


def _disposition(needs_review: bool, conversion_method: str) -> str:
    """converted = no review needed; manual = procedural logic with no SQL
    path at all (pure PySpark stub); partial = everything else flagged for
    review (has at least a SQL skeleton or a split SQL+orchestration pair)."""
    if not needs_review:
        return "converted"
    if conversion_method == "pyspark":
        return "manual"
    return "partial"


def _load_classification(manifest_dir: Path) -> dict[str, str]:
    scores_file = manifest_dir / "object_complexity_scores.json"
    if not scores_file.exists():
        return {}
    scores = json.loads(scores_file.read_text(encoding="utf-8"))
    return {o["id"]: o["classification"] for o in scores["objects"]}


def _load_medallion_targets(manifest_dir: Path) -> dict[str, str]:
    medallion_file = manifest_dir / "medallion_mapping.csv"
    if not medallion_file.exists():
        return {}
    with medallion_file.open(encoding="utf-8") as f:
        return {row["source_id"]: row["target_fqn"] for row in csv.DictReader(f)}


async def handle_convert_sql(
    manifest_path: str,
    output_path: str = "./output",
    object_filter: list[str] | None = None,
) -> dict[str, Any]:
    """Convert SQL Server / Synapse objects to Databricks SQL and PySpark.

    Args:
        manifest_path: Path to inventory.json produced by parse_source.
        output_path: Directory to write converted output to.
        object_filter: Optional list of object ids to restrict conversion to.

    Returns:
        {converted_count, partial_count, manual_count, output_paths}
        on success, or {error: True, message: str} on failure.
    """
    logger.info(
        "tool_call timestamp=%s tool=convert_sql input=%s",
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        json.dumps({"manifest_path": manifest_path, "output_path": output_path,
                     "object_filter": object_filter}),
    )
    try:
        manifest_file = Path(manifest_path)
        if not manifest_file.exists():
            return {"error": True, "message": f"manifest_path does not exist: {manifest_path}"}

        inventory = json.loads(manifest_file.read_text(encoding="utf-8"))
        manifest_dir = manifest_file.parent
        classification_by_id = _load_classification(manifest_dir)
        medallion_by_id = _load_medallion_targets(manifest_dir)

        out_dir = Path(output_path)
        sql_dir, py_dir, review_dir = out_dir / "databricks_sql", out_dir / "pyspark", out_dir / "review_required"
        for d in (sql_dir, py_dir, review_dir):
            d.mkdir(parents=True, exist_ok=True)

        objects = [o for o in inventory["objects"] if o.get("object_type") in _CONVERTIBLE_TYPES]
        if object_filter:
            wanted = set(object_filter)
            objects = [o for o in objects if o["id"] in wanted]

        manifest_entries: list[dict[str, Any]] = []
        converted = partial = manual = 0

        for obj in objects:
            otype = obj["object_type"]
            target_fqn = medallion_by_id.get(
                obj["id"], f"wwi_<env>.{obj.get('medallion_layer', 'bronze').lower()}.x"
            )
            base_name = f"{_slug(obj.get('schema', 'default'))}__{_slug(obj.get('name', 'unknown'))}"

            try:
                if otype == "TABLE":
                    result = convert_table(obj, target_fqn)
                elif otype == "VIEW":
                    result = convert_view(obj, target_fqn)
                elif otype in ("SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI"):
                    result = convert_function(obj, target_fqn)
                else:
                    result = convert_procedure(
                        obj, classification_by_id.get(obj["id"], "PARTIAL_AUTOMATION"), target_fqn
                    )
            except Exception as conv_exc:  # noqa: BLE001 — one bad object must not abort the batch
                logger.exception("conversion failed for object_id=%s", obj["id"])
                manifest_entries.append({"id": obj["id"], "object_type": otype, "error": str(conv_exc)})
                manual += 1
                continue

            files_written: list[str] = []
            conversion_method = "databricks_sql"
            if "sql" in result:
                p = sql_dir / f"{base_name}.sql"
                p.write_text(result["sql"], encoding="utf-8")
                files_written.append(str(p))
                conversion_method = "databricks_sql"
            elif "pyspark" in result:
                p = py_dir / f"{base_name}.py"
                p.write_text(result["pyspark"], encoding="utf-8")
                files_written.append(str(p))
                conversion_method = "pyspark"
            elif "files" in result:
                files = result["files"]
                if "databricks_sql" in files:
                    p = sql_dir / f"{base_name}.sql"
                    p.write_text(files["databricks_sql"], encoding="utf-8")
                    files_written.append(str(p))
                if "pyspark" in files:
                    suffix = "_orchestration" if result.get("split") else ""
                    p = py_dir / f"{base_name}{suffix}.py"
                    p.write_text(files["pyspark"], encoding="utf-8")
                    files_written.append(str(p))
                conversion_method = (
                    "split_sql_pyspark" if result.get("split")
                    else ("pyspark" if "pyspark" in files and "databricks_sql" not in files else "databricks_sql")
                )

            needs_review = bool(result.get("needs_review", False))
            disposition = _disposition(needs_review, conversion_method)
            if disposition == "converted":
                converted += 1
            elif disposition == "partial":
                partial += 1
            else:
                manual += 1

            if needs_review:
                review_path = review_dir / f"{base_name}.md"
                warnings = result.get("warnings", [])
                review_path.write_text(
                    f"# Review Required: {obj['id']}\n\n"
                    f"- **Object type:** {otype}\n\n## Why this needs manual review\n\n"
                    + "\n".join(f"- {w}" for w in warnings),
                    encoding="utf-8",
                )
                files_written.append(str(review_path))

            manifest_entries.append({
                "id": obj["id"],
                "object_type": otype,
                "target_fqn": target_fqn,
                "conversion_method": conversion_method,
                "needs_review": needs_review,
                "disposition": disposition,
                "files_written": files_written,
                "warnings": result.get("warnings", []),
            })

        manifest_out = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "object_count": len(manifest_entries),
            "conversion_method_distribution": {
                m: sum(1 for e in manifest_entries if e.get("conversion_method") == m)
                for m in {e.get("conversion_method") for e in manifest_entries if e.get("conversion_method")}
            },
            "objects": manifest_entries,
        }
        manifest_out_path = out_dir / "conversion_manifest.json"
        manifest_out_path.write_text(json.dumps(manifest_out, indent=2, default=str), encoding="utf-8")

        return {
            "converted_count": converted,
            "partial_count": partial,
            "manual_count": manual,
            "output_paths": {
                "databricks_sql": str(sql_dir),
                "pyspark": str(py_dir),
                "review_required": str(review_dir),
                "manifest": str(manifest_out_path),
            },
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("convert_sql failed")
        return {"error": True, "message": str(exc)}
