"""
mcp/tools/convert_ssis.py
Handler for the convert_ssis MCP tool.

NOTE ON IMPLEMENTATION: the original spec named ssis_to_workflows.py and
ssis_to_pyspark.py, which never existed as separate modules — the real
implementation is accelerator.converters.ssis_converter, whose single
convert_ssis_package() entry point already produces workflow_spec.json,
databricks_job_bundle.yml, per-task Python/SQL modules, and
ssis_conversion_report.md together (this mirrors run_ssis_conversion.py).
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from accelerator.converters.ssis_converter import build_task_catalog, convert_ssis_package

logger = logging.getLogger(__name__)

# A task below this confidence is treated as needing manual completion before
# it's safe to deploy — matches the "needs_review" intent used elsewhere in
# the accelerator (see object_complexity_scores.json's classification logic).
_UNSUPPORTED_CONFIDENCE_THRESHOLD = 0.6


async def handle_convert_ssis(manifest_path: str, output_path: str = "./output") -> dict[str, Any]:
    """Convert SSIS packages to Databricks Workflows and PySpark notebooks.

    Args:
        manifest_path: Path to inventory.json produced by parse_source.
        output_path: Directory to write the Workflow spec and converted modules to.

    Returns:
        {workflow_spec_path, bundle_path, task_count, unsupported_task_count}
        on success, or {error: True, message: str} on failure.
    """
    logger.info(
        "tool_call timestamp=%s tool=convert_ssis input=%s",
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        json.dumps({"manifest_path": manifest_path, "output_path": output_path}),
    )
    try:
        manifest_file = Path(manifest_path)
        if not manifest_file.exists():
            return {"error": True, "message": f"manifest_path does not exist: {manifest_path}"}

        deps_file = manifest_file.parent / "dependencies.json"
        if not deps_file.exists():
            return {
                "error": True,
                "message": f"dependencies.json not found alongside manifest at {deps_file} — run parse_source first",
            }

        inventory = json.loads(manifest_file.read_text(encoding="utf-8"))
        graph = json.loads(deps_file.read_text(encoding="utf-8"))

        if not any(o.get("object_type") == "SSIS_PACKAGE" for o in inventory["objects"]):
            return {"error": True, "message": "No SSIS_PACKAGE object found in inventory — nothing to convert."}

        out_dir = Path(output_path)
        paths = convert_ssis_package(inventory, graph, out_dir)

        tasks = build_task_catalog(inventory, graph)
        task_count = len(tasks)
        unsupported_task_count = sum(1 for t in tasks if t["confidence"] < _UNSUPPORTED_CONFIDENCE_THRESHOLD)

        return {
            "workflow_spec_path": str(paths["workflow_spec"]),
            "bundle_path": str(paths["job_bundle"]),
            "task_count": task_count,
            "unsupported_task_count": unsupported_task_count,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("convert_ssis failed")
        return {"error": True, "message": str(exc)}
