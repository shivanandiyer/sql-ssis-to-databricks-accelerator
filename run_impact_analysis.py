"""
run_impact_analysis.py
Entry point for the impact-analysis step.

Loads outputs/inventory.json and outputs/dependencies.json (already produced by
run_analysis.py) and produces:
    outputs/impact_analysis.md
    outputs/migration_risk_register.csv
    outputs/object_complexity_scores.json
    outputs/manual_intervention_list.md

Usage:
    python run_impact_analysis.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from accelerator.analyzers.impact_analysis import run_impact_analysis

OUTPUT_DIR = Path(__file__).parent / "outputs"


def main() -> None:
    t0 = time.time()

    inventory = json.loads((OUTPUT_DIR / "inventory.json").read_text(encoding="utf-8"))
    graph = json.loads((OUTPUT_DIR / "dependencies.json").read_text(encoding="utf-8"))

    print("=" * 60)
    print("  Running impact analysis")
    print("=" * 60)
    paths = run_impact_analysis(inventory, graph, OUTPUT_DIR)

    for key, path in paths.items():
        size = path.stat().st_size if path.exists() else 0
        print(f"  {'✓' if path.exists() else '✗'}  {path.name:<35} {size:>8,} bytes")

    elapsed = time.time() - t0
    print(f"\n  Completed in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
