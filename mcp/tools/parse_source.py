"""
mcp/tools/parse_source.py
Handler for the parse_source MCP tool.

NOTE ON IMPLEMENTATION: the original tool spec for this handler referenced
`accelerator.parsers.run_parsers` and a single `run_parsers(source_path, config)`
entry point. That module/function never existed in this repo — it was part of
an early scaffold (see skills/02_runtime_input_interface.md) that was replaced
during real implementation. This handler is wired to the actual, working
parsers/analyzers instead: accelerator.parsers.sql_project_parser.parse_sqlproj(),
accelerator.parsers.ssis_parser.parse_project(), and
accelerator.analyzers.inventory_builder.build_inventory() /
accelerator.analyzers.dependency_graph.build_and_save_graph() — the same
sequence run_analysis.py drives, generalised to accept an arbitrary source_path
instead of the hardcoded WWI sample paths.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from accelerator.analyzers.dependency_graph import build_and_save_graph
from accelerator.analyzers.inventory_builder import build_inventory
from accelerator.parsers.sql_project_parser import parse_sqlproj
from accelerator.parsers.ssis_parser import parse_project as parse_ssis_project

logger = logging.getLogger(__name__)


def _detect_source_dirs(root: Path, config_path: str | None) -> tuple[Path | None, Path | None, Path | None]:
    """Locate the OLTP/.sqlproj, DW/.sqlproj, and SSIS/.dtsx project directories.

    If config_path is given, it must be a JSON file with optional
    "oltp_dir" / "dw_dir" / "ssis_dir" keys (absolute or relative to root).
    Otherwise, directories are auto-detected by scanning root for .sqlproj
    and .dtsx files — a directory whose name contains "dw" is treated as the
    DW project, the first other .sqlproj directory as OLTP.
    """
    oltp_dir = dw_dir = ssis_dir = None
    if config_path:
        cfg = json.loads(Path(config_path).read_text(encoding="utf-8"))
        if cfg.get("oltp_dir"):
            oltp_dir = Path(cfg["oltp_dir"])
        if cfg.get("dw_dir"):
            dw_dir = Path(cfg["dw_dir"])
        if cfg.get("ssis_dir"):
            ssis_dir = Path(cfg["ssis_dir"])

    if oltp_dir and dw_dir and ssis_dir:
        return oltp_dir, dw_dir, ssis_dir

    sqlproj_dirs = sorted({p.parent for p in root.rglob("*.sqlproj")})
    dtsx_dirs = sorted({p.parent for p in root.rglob("*.dtsx")})

    if not dw_dir:
        dw_candidates = [d for d in sqlproj_dirs if "dw" in d.name.lower()]
        dw_dir = dw_candidates[0] if dw_candidates else None
    if not oltp_dir:
        non_dw = [d for d in sqlproj_dirs if d != dw_dir and "dw" not in d.name.lower()]
        oltp_dir = non_dw[0] if non_dw else None
    if not ssis_dir:
        ssis_dir = dtsx_dirs[0] if dtsx_dirs else None

    return oltp_dir, dw_dir, ssis_dir


async def handle_parse_source(source_path: str, config_path: str | None = None) -> dict[str, Any]:
    """Parse a source repository and extract all SQL/SSIS objects.

    Returns:
        {inventory_path, dependency_path, object_count, unsupported_count, summary}
        on success, or {error: True, message: str} on failure.
    """
    logger.info(
        "tool_call timestamp=%s tool=parse_source input=%s",
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        json.dumps({"source_path": source_path, "config_path": config_path}),
    )
    try:
        root = Path(source_path)
        if not root.exists():
            return {"error": True, "message": f"source_path does not exist: {source_path}"}

        oltp_dir, dw_dir, ssis_dir = _detect_source_dirs(root, config_path)
        if not oltp_dir and not dw_dir and not ssis_dir:
            return {
                "error": True,
                "message": (
                    f"Could not locate any .sqlproj or .dtsx files under {source_path}. "
                    "Pass config_path pointing to a JSON file with explicit "
                    "oltp_dir/dw_dir/ssis_dir keys."
                ),
            }

        all_sql: list[dict[str, Any]] = []
        if oltp_dir and oltp_dir.exists():
            all_sql += parse_sqlproj(oltp_dir, source_project="OLTP")
        if dw_dir and dw_dir.exists():
            all_sql += parse_sqlproj(dw_dir, source_project="DW")
        ssis_packages = parse_ssis_project(ssis_dir) if ssis_dir and ssis_dir.exists() else []

        output_dir = Path("./outputs")
        output_dir.mkdir(parents=True, exist_ok=True)
        inventory = build_inventory(all_sql, ssis_packages, output_dir)
        build_and_save_graph(inventory, output_dir)

        by_type: dict[str, int] = {}
        for obj in inventory["objects"]:
            by_type[obj["object_type"]] = by_type.get(obj["object_type"], 0) + 1

        return {
            "inventory_path": str(output_dir / "inventory.json"),
            "dependency_path": str(output_dir / "dependencies.json"),
            "object_count": inventory["total_objects"],
            "unsupported_count": inventory["unsupported_count"],
            "summary": by_type,
        }
    except Exception as exc:  # noqa: BLE001 — handlers must never raise across the MCP boundary
        logger.exception("parse_source failed")
        return {"error": True, "message": str(exc)}
