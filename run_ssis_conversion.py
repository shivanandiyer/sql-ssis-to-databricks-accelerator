"""
run_ssis_conversion.py
Entry point for the SSIS conversion layer.

Reads:
    <input-path>/inventory.json
    <input-path>/dependencies.json

Writes (under <output-path>/):
    workflow_spec.json
    databricks_job_bundle.yml
    ssis_tasks/*.py
    ssis_conversion_report.md
    unsupported_ssis_features.md

Usage:
    python run_ssis_conversion.py --input-path ./outputs --output-path ./output
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from accelerator.converters.ssis_converter import convert_ssis_package


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Convert SSIS packages to Databricks Workflows and PySpark.",
    )
    p.add_argument("--input-path", metavar="DIR", default="./outputs",
                   help="Directory containing inventory.json and dependencies.json. Default: ./outputs")
    p.add_argument("--output-path", metavar="DIR", default="./output",
                   help="Directory to write converted workflow spec and task modules. Default: ./output")
    return p.parse_args()


def main() -> None:
    args = _parse_args()
    input_dir  = Path(args.input_path)
    output_dir = Path(args.output_path)

    for required in ("inventory.json", "dependencies.json"):
        if not (input_dir / required).exists():
            print(f"error: {required} not found in {input_dir}. "
                  "Run run_analysis.py first.", file=sys.stderr)
            sys.exit(1)

    t0 = time.time()
    inventory = json.loads((input_dir / "inventory.json").read_text(encoding="utf-8"))
    graph     = json.loads((input_dir / "dependencies.json").read_text(encoding="utf-8"))

    ssis_objects = [o for o in inventory["objects"] if o.get("object_type") == "SSIS_PACKAGE"]
    if not ssis_objects:
        print("No SSIS_PACKAGE objects found in inventory — nothing to convert.")
        print("(If your repo has SSIS packages, check that --ssis-dir was detected correctly "
              "during run_analysis.py.)")
        return

    print("=" * 60)
    print(f"  Converting {len(ssis_objects)} SSIS package(s)")
    print("=" * 60)

    output_dir.mkdir(parents=True, exist_ok=True)
    paths = convert_ssis_package(inventory, graph, output_dir)

    paths.pop("_module_count", 0)
    paths.pop("_sql_file_count", 0)
    for key, path in paths.items():
        if isinstance(path, Path) and path.is_dir():
            pattern = "*.sql" if "sql" in key else "*.py"
            n = len(list(path.glob(pattern)))
            print(f"  ✓  {path.name:<40} {n} files")
        else:
            size = path.stat().st_size if path.exists() else 0
            print(f"  {'✓' if path.exists() else '✗'}  {path.name:<40} {size:>8,} bytes")

    elapsed = time.time() - t0
    print(f"\n  Completed in {elapsed:.1f}s")
    print(f"  Outputs written to: {output_dir.resolve()}")
    print(f"  Next step: python deploy/generate_deployment_bundle.py --input-path {output_dir} --env dev")


if __name__ == "__main__":
    main()
