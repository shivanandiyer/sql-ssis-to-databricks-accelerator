"""
run_test_matrix.py
Entry point for building the test matrix.

Reads:
    <analysis-path>/inventory.json
    <analysis-path>/object_complexity_scores.json
    <analysis-path>/medallion_mapping.csv
    <conversion-path>/conversion_manifest.json
    <conversion-path>/workflow_spec.json

Writes (under <analysis-path>/):
    test_matrix.csv
    test_strategy.md
    coverage_gaps.md

Usage:
    python run_test_matrix.py --input-path ./outputs --conversion-path ./output
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from pathlib import Path

from accelerator.docs.test_matrix import generate_test_matrix


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate the test matrix and coverage gaps report.",
    )
    p.add_argument("--input-path", metavar="DIR", default="./outputs",
                   help="Directory containing inventory.json and analysis outputs. Default: ./outputs")
    p.add_argument("--conversion-path", metavar="DIR", default="./output",
                   help="Directory containing conversion_manifest.json and workflow_spec.json. "
                        "Default: ./output")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    input_dir      = Path(args.input_path)
    conversion_dir = Path(args.conversion_path)

    for path, label in [
        (input_dir / "inventory.json",              "inventory.json"),
        (input_dir / "object_complexity_scores.json", "object_complexity_scores.json"),
        (input_dir / "medallion_mapping.csv",        "medallion_mapping.csv"),
        (conversion_dir / "conversion_manifest.json", "conversion_manifest.json"),
        (conversion_dir / "workflow_spec.json",       "workflow_spec.json"),
    ]:
        if not path.exists():
            print(f"error: {label} not found at {path}. Run previous pipeline steps first.",
                  file=sys.stderr)
            sys.exit(1)

    t0 = time.time()
    inventory         = json.loads((input_dir / "inventory.json").read_text(encoding="utf-8"))
    complexity_scores = json.loads((input_dir / "object_complexity_scores.json").read_text(encoding="utf-8"))
    medallion_rows    = list(csv.DictReader((input_dir / "medallion_mapping.csv").open(encoding="utf-8")))
    conversion_manifest = json.loads((conversion_dir / "conversion_manifest.json").read_text(encoding="utf-8"))
    workflow_spec     = json.loads((conversion_dir / "workflow_spec.json").read_text(encoding="utf-8"))

    print("=" * 60)
    print("  Building test matrix")
    print("=" * 60)
    paths = generate_test_matrix(
        inventory, complexity_scores, medallion_rows,
        conversion_manifest, workflow_spec, input_dir,
    )

    for key, path in paths.items():
        size = path.stat().st_size if path.exists() else 0
        print(f"  {'✓' if path.exists() else '✗'}  {path.name:<40} {size:>8,} bytes")

    elapsed = time.time() - t0
    print(f"\n  Completed in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
