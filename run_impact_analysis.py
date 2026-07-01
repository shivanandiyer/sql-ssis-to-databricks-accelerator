"""
run_impact_analysis.py
Entry point for the impact-analysis step.

Reads:
    <input-path>/inventory.json
    <input-path>/dependencies.json

Produces:
    <input-path>/impact_analysis.md
    <input-path>/migration_risk_register.csv
    <input-path>/object_complexity_scores.json
    <input-path>/manual_intervention_list.md

Usage:
    python run_impact_analysis.py --input-path ./outputs
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from accelerator.analyzers.impact_analysis import run_impact_analysis


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run impact analysis on a parsed inventory.",
    )
    p.add_argument("--input-path", metavar="DIR", default="./outputs",
                   help="Directory containing inventory.json and dependencies.json "
                        "(produced by run_analysis.py). Default: ./outputs")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    output_dir = Path(args.input_path)

    if not (output_dir / "inventory.json").exists():
        print(f"error: inventory.json not found in {output_dir}. "
              "Run run_analysis.py first.", file=sys.stderr)
        sys.exit(1)

    t0 = time.time()
    inventory = json.loads((output_dir / "inventory.json").read_text(encoding="utf-8"))
    graph     = json.loads((output_dir / "dependencies.json").read_text(encoding="utf-8"))

    print("=" * 60)
    print("  Running impact analysis")
    print("=" * 60)
    paths = run_impact_analysis(inventory, graph, output_dir)

    for key, path in paths.items():
        size = path.stat().st_size if path.exists() else 0
        print(f"  {'✓' if path.exists() else '✗'}  {path.name:<40} {size:>8,} bytes")

    elapsed = time.time() - t0
    print(f"\n  Completed in {elapsed:.1f}s")
    print(f"  Next step: python run_target_state_design.py --input-path {output_dir}")


if __name__ == "__main__":
    main()
