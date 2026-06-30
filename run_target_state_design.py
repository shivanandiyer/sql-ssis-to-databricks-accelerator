"""
run_target_state_design.py
Entry point for the target-state design step.

Usage:
    python run_target_state_design.py [architecture_override]

architecture_override: optional, one of "medallion" (default), "data_vault", "one_big_table".
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

from accelerator.docs.target_state_design import generate_target_state_design

OUTPUT_DIR = Path(__file__).parent / "outputs"


def main() -> None:
    t0 = time.time()
    override = sys.argv[1] if len(sys.argv) > 1 else None

    inventory = json.loads((OUTPUT_DIR / "inventory.json").read_text(encoding="utf-8"))
    graph = json.loads((OUTPUT_DIR / "dependencies.json").read_text(encoding="utf-8"))
    complexity_scores = json.loads((OUTPUT_DIR / "object_complexity_scores.json").read_text(encoding="utf-8"))

    print("=" * 60)
    print("  Generating target-state design")
    print("=" * 60)
    paths = generate_target_state_design(inventory, graph, complexity_scores, OUTPUT_DIR, override)

    for key, path in paths.items():
        size = path.stat().st_size if path.exists() else 0
        print(f"  {'✓' if path.exists() else '✗'}  {path.name:<35} {size:>8,} bytes")

    elapsed = time.time() - t0
    print(f"\n  Completed in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
