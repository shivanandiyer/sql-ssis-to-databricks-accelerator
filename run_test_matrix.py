"""
run_test_matrix.py
Entry point for building the accelerator's test matrix.

Reads:
    outputs/inventory.json
    outputs/object_complexity_scores.json
    outputs/medallion_mapping.csv
    output/conversion_manifest.json
    output/workflow_spec.json

Writes (under outputs/):
    test_matrix.csv
    test_strategy.md
    coverage_gaps.md

Usage:
    python run_test_matrix.py
"""

from __future__ import annotations

import csv
import json
import time
from pathlib import Path

from accelerator.docs.test_matrix import generate_test_matrix

ROOT = Path(__file__).parent
OUTPUTS_DIR = ROOT / "outputs"
OUTPUT_DIR = ROOT / "output"


def main() -> None:
    t0 = time.time()
    inventory = json.loads((OUTPUTS_DIR / "inventory.json").read_text(encoding="utf-8"))
    complexity_scores = json.loads((OUTPUTS_DIR / "object_complexity_scores.json").read_text(encoding="utf-8"))
    medallion_rows = list(csv.DictReader((OUTPUTS_DIR / "medallion_mapping.csv").open(encoding="utf-8")))
    conversion_manifest = json.loads((OUTPUT_DIR / "conversion_manifest.json").read_text(encoding="utf-8"))
    workflow_spec = json.loads((OUTPUT_DIR / "workflow_spec.json").read_text(encoding="utf-8"))

    print("=" * 60)
    print("  Building test matrix")
    print("=" * 60)
    paths = generate_test_matrix(inventory, complexity_scores, medallion_rows,
                                  conversion_manifest, workflow_spec, OUTPUTS_DIR)

    for key, path in paths.items():
        size = path.stat().st_size if path.exists() else 0
        print(f"  {'✓' if path.exists() else '✗'}  {path.name:<35} {size:>8,} bytes")

    elapsed = time.time() - t0
    print(f"\n  Completed in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
