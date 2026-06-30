"""
run_ssis_conversion.py
Entry point for the SSIS conversion layer.

Reads:
    outputs/inventory.json
    outputs/dependencies.json

Writes (under output/):
    workflow_spec.json
    databricks_job_bundle.yml
    ssis_tasks/*.py
    ssis_conversion_report.md
    unsupported_ssis_features.md

Usage:
    python run_ssis_conversion.py
"""

from __future__ import annotations

import json
import time
from pathlib import Path

from accelerator.converters.ssis_converter import convert_ssis_package

ROOT = Path(__file__).parent
OUTPUTS_DIR = ROOT / "outputs"
OUTPUT_ROOT = ROOT / "output"


def main() -> None:
    t0 = time.time()
    inventory = json.loads((OUTPUTS_DIR / "inventory.json").read_text(encoding="utf-8"))
    graph = json.loads((OUTPUTS_DIR / "dependencies.json").read_text(encoding="utf-8"))

    print("=" * 60)
    print("  Converting SSIS package")
    print("=" * 60)
    paths = convert_ssis_package(inventory, graph, OUTPUT_ROOT)

    paths.pop("_module_count", 0)
    paths.pop("_sql_file_count", 0)
    for key, path in paths.items():
        if isinstance(path, Path) and path.is_dir():
            pattern = "*.sql" if "sql" in key else "*.py"
            n = len(list(path.glob(pattern)))
            print(f"  ✓  {path.relative_to(ROOT)!s:<35} {n} files")
        else:
            size = path.stat().st_size if path.exists() else 0
            print(f"  {'✓' if path.exists() else '✗'}  {path.relative_to(ROOT)!s:<35} {size:>8,} bytes")

    elapsed = time.time() - t0
    print(f"\n  Completed in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
