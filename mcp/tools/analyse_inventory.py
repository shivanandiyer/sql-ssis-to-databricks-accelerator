"""
mcp/tools/analyse_inventory.py
Handler for the analyse_inventory MCP tool.

NOTE ON IMPLEMENTATION: "run all four analyzers" in the original spec doesn't
map onto four distinct modules in this repo — inventory building and
dependency-graph construction (two of the conceptual "analyzers") already
happen inside parse_source. This handler runs the two analysis stages that
come *after* parsing: accelerator.analyzers.impact_analysis.run_impact_analysis()
and accelerator.docs.target_state_design.generate_target_state_design() — the
same sequence run_impact_analysis.py and run_target_state_design.py drive.
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from accelerator.analyzers.impact_analysis import run_impact_analysis
from accelerator.docs.target_state_design import generate_target_state_design

logger = logging.getLogger(__name__)

# Matches the vocabulary already validated in mcp/server.py's tool stub —
# generate_target_state_design() itself accepts any string (it doesn't
# hard-enforce an enum), so these are passed through as-is rather than
# translated to the medallion/data_vault/one_big_table names used internally
# by decide_architecture()'s own evaluated-alternatives comparison.
_VALID_ARCHITECTURES = {"medallion", "lakehouse", "lambda", "kappa"}


async def handle_analyse_inventory(
    manifest_path: str,
    architecture_override: str | None = None,
) -> dict[str, Any]:
    """Run impact analysis and architecture recommendation on a parsed inventory.

    Args:
        manifest_path: Path to inventory.json produced by parse_source.
            dependencies.json is expected alongside it in the same directory.
        architecture_override: Optional target architecture —
            medallion | lakehouse | lambda | kappa.

    Returns:
        {impact_path, architecture, complexity_breakdown, manual_intervention_count}
        on success, or {error: True, message: str} on failure.
    """
    logger.info(
        "tool_call timestamp=%s tool=analyse_inventory input=%s",
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        json.dumps({"manifest_path": manifest_path, "architecture_override": architecture_override}),
    )
    try:
        if architecture_override is not None and architecture_override not in _VALID_ARCHITECTURES:
            return {
                "error": True,
                "message": (
                    f"architecture_override must be one of "
                    f"{'|'.join(sorted(_VALID_ARCHITECTURES))}, got {architecture_override!r}"
                ),
            }

        manifest_file = Path(manifest_path)
        if not manifest_file.exists():
            return {"error": True, "message": f"manifest_path does not exist: {manifest_path}"}

        output_dir = manifest_file.parent
        deps_file = output_dir / "dependencies.json"
        if not deps_file.exists():
            return {
                "error": True,
                "message": f"dependencies.json not found alongside manifest at {deps_file} — run parse_source first",
            }

        inventory = json.loads(manifest_file.read_text(encoding="utf-8"))
        graph = json.loads(deps_file.read_text(encoding="utf-8"))

        impact_paths = run_impact_analysis(inventory, graph, output_dir)
        scores = json.loads(impact_paths["complexity_scores_json"].read_text(encoding="utf-8"))

        target_paths = generate_target_state_design(inventory, graph, scores, output_dir, architecture_override)
        mappings = json.loads(target_paths["target_state_mappings_json"].read_text(encoding="utf-8"))

        manual_count = scores["classification_distribution"].get("Manual redesign required", 0)

        return {
            "impact_path": str(impact_paths["impact_analysis_md"]),
            "architecture": mappings["architecture_decision"]["chosen_architecture"],
            "complexity_breakdown": scores["classification_distribution"],
            "manual_intervention_count": manual_count,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("analyse_inventory failed")
        return {"error": True, "message": str(exc)}
