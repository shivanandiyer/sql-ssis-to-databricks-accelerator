"""
run_target_state_design.py
Entry point for the target-state design step.

Reads:
    <input-path>/inventory.json
    <input-path>/dependencies.json
    <input-path>/object_complexity_scores.json

Produces:
    <input-path>/target_state_design.md
    <input-path>/target_state_mappings.json
    <input-path>/medallion_mapping.csv
    <input-path>/unity_catalog_design.md

Usage:
    python run_target_state_design.py --input-path ./outputs
    python run_target_state_design.py --input-path ./outputs --architecture lakehouse
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from accelerator.docs.target_state_design import generate_target_state_design

_VALID_ARCHITECTURES = {"medallion", "lakehouse", "lambda", "kappa"}


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Generate target-state architecture design and medallion mapping.",
    )
    p.add_argument("--input-path", metavar="DIR", default="./outputs",
                   help="Directory containing inventory.json + object_complexity_scores.json "
                        "(produced by previous steps). Default: ./outputs")
    p.add_argument("--architecture", metavar="NAME", default=None,
                   choices=sorted(_VALID_ARCHITECTURES),
                   help="Override the recommended architecture. "
                        "One of: medallion (default), lakehouse, lambda, kappa.")
    p.add_argument("--output-path", metavar="DIR", default=None,
                   help="Write outputs to a different directory (default: same as --input-path).")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    input_dir  = Path(args.input_path)
    output_dir = Path(args.output_path) if args.output_path else input_dir

    for required in ("inventory.json", "dependencies.json", "object_complexity_scores.json"):
        if not (input_dir / required).exists():
            print(f"error: {required} not found in {input_dir}. "
                  "Run run_analysis.py and run_impact_analysis.py first.", file=sys.stderr)
            sys.exit(1)

    t0 = time.time()
    inventory        = json.loads((input_dir / "inventory.json").read_text(encoding="utf-8"))
    graph            = json.loads((input_dir / "dependencies.json").read_text(encoding="utf-8"))
    complexity_scores = json.loads((input_dir / "object_complexity_scores.json").read_text(encoding="utf-8"))

    print("=" * 60)
    print("  Generating target-state design")
    print("=" * 60)
    if args.architecture:
        print(f"  Architecture override: {args.architecture}")

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = generate_target_state_design(
        inventory, graph, complexity_scores, output_dir, args.architecture
    )

    for key, path in paths.items():
        size = path.stat().st_size if path.exists() else 0
        print(f"  {'✓' if path.exists() else '✗'}  {path.name:<40} {size:>8,} bytes")

    elapsed = time.time() - t0
    print(f"\n  Completed in {elapsed:.1f}s")
    print(f"  Next step: python run_conversion.py --input-path {input_dir} --output-path ./output")


if __name__ == "__main__":
    main()
