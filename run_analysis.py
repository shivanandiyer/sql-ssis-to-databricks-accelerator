"""
run_analysis.py
Entry point for Step 1: parse any SQL Server / SSIS / Synapse source repo
and produce the inventory and dependency graph.

Usage (auto-detect project dirs):
    python run_analysis.py --source-path /path/to/your/repo

Usage (explicit dirs for non-standard folder names):
    python run_analysis.py \\
        --oltp-dir  /path/to/repo/OLTP_Project \\
        --dw-dir    /path/to/repo/DW_Project \\
        --ssis-dir  /path/to/repo/SSIS_Packages

Output directory (default: ./outputs):
    python run_analysis.py --source-path /path/to/repo --output-path ./my-outputs

Produces:
    <output-path>/inventory.json
    <output-path>/unsupported_objects.json
    <output-path>/dependencies.json
    <output-path>/dependency_graph.dot
    <output-path>/dependency_graph.md   (Mermaid)
    <output-path>/current_state_documentation.md
    <output-path>/current_state_summary.json
    <output-path>/source_summary.md
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from accelerator.parsers.ssis_parser import parse_project as parse_ssis
from accelerator.parsers.sql_project_parser import parse_sqlproj
from accelerator.analyzers.inventory_builder import build_inventory
from accelerator.analyzers.dependency_graph import build_and_save_graph
from accelerator.docs.current_state_doc import generate_current_state_docs


def _detect_dirs(source_path: Path) -> tuple[Path | None, Path | None, Path | None]:
    """Auto-detect OLTP, DW and SSIS directories under source_path.

    A directory whose name contains 'dw' (case-insensitive) is treated as the
    DW project; the first other .sqlproj directory is treated as OLTP. The
    first directory containing .dtsx files is the SSIS project.
    """
    sqlproj_dirs = sorted({p.parent for p in source_path.rglob("*.sqlproj")})
    dtsx_dirs    = sorted({p.parent for p in source_path.rglob("*.dtsx")})

    dw_candidates   = [d for d in sqlproj_dirs if "dw" in d.name.lower()]
    dw_dir          = dw_candidates[0] if dw_candidates else None
    non_dw          = [d for d in sqlproj_dirs if d != dw_dir]
    oltp_dir        = non_dw[0] if non_dw else None
    ssis_dir        = dtsx_dirs[0] if dtsx_dirs else None

    return oltp_dir, dw_dir, ssis_dir


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Parse a SQL Server / SSIS / Synapse source repo and build an object inventory.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto-detect project folders inside the repo:
  python run_analysis.py --source-path /path/to/your/repo

  # Explicit folder paths (when folder names don't contain 'dw'):
  python run_analysis.py \\
      --oltp-dir  /path/to/repo/OLTP \\
      --dw-dir    /path/to/repo/DataWarehouse \\
      --ssis-dir  /path/to/repo/ETL

  # Custom output location:
  python run_analysis.py --source-path /path/to/repo --output-path ./my-project/outputs
""",
    )
    p.add_argument("--source-path", metavar="DIR",
                   help="Root of the source repository (auto-detects OLTP/DW/SSIS dirs).")
    p.add_argument("--oltp-dir",  metavar="DIR", help="Explicit path to the OLTP .sqlproj directory.")
    p.add_argument("--dw-dir",    metavar="DIR", help="Explicit path to the DW .sqlproj directory.")
    p.add_argument("--ssis-dir",  metavar="DIR", help="Explicit path to the SSIS .dtsx directory.")
    p.add_argument("--output-path", metavar="DIR", default="./outputs",
                   help="Directory to write all outputs into (default: ./outputs).")
    return p.parse_args()


def _section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def main() -> None:
    args = _parse_args()

    # Resolve source directories
    oltp_dir = Path(args.oltp_dir) if args.oltp_dir else None
    dw_dir   = Path(args.dw_dir)   if args.dw_dir   else None
    ssis_dir = Path(args.ssis_dir) if args.ssis_dir else None

    if not (oltp_dir or dw_dir or ssis_dir):
        if not args.source_path:
            print("error: provide --source-path for auto-detection, or set at least one of "
                  "--oltp-dir / --dw-dir / --ssis-dir", file=sys.stderr)
            sys.exit(1)
        source_root = Path(args.source_path)
        if not source_root.exists():
            print(f"error: --source-path does not exist: {source_root}", file=sys.stderr)
            sys.exit(1)
        oltp_dir, dw_dir, ssis_dir = _detect_dirs(source_root)
        if not oltp_dir and not dw_dir and not ssis_dir:
            print(
                f"error: no .sqlproj or .dtsx files found under {source_root}.\n"
                "       Use --oltp-dir / --dw-dir / --ssis-dir to specify paths explicitly.",
                file=sys.stderr,
            )
            sys.exit(1)

    output_dir = Path(args.output_path)
    output_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()

    # ── Parse OLTP project ────────────────────────────────────────────────
    oltp_objects: list = []
    if oltp_dir and oltp_dir.exists():
        _section(f"Parsing OLTP project ({oltp_dir.name})")
        oltp_objects = parse_sqlproj(oltp_dir, source_project="OLTP")
        print(f"  → {len(oltp_objects)} SQL objects parsed")
    else:
        print("\n  [skip] No OLTP directory found or specified")

    # ── Parse DW project ──────────────────────────────────────────────────
    dw_objects: list = []
    if dw_dir and dw_dir.exists():
        _section(f"Parsing DW project ({dw_dir.name})")
        dw_objects = parse_sqlproj(dw_dir, source_project="DW")
        print(f"  → {len(dw_objects)} SQL objects parsed")
    else:
        print("\n  [skip] No DW directory found or specified")

    # ── Parse SSIS project ────────────────────────────────────────────────
    ssis_packages: list = []
    if ssis_dir and ssis_dir.exists():
        _section(f"Parsing SSIS project ({ssis_dir.name})")
        ssis_packages = parse_ssis(ssis_dir)
        task_count = sum(len(p.get("all_tasks_flat", [])) for p in ssis_packages)
        print(f"  → {len(ssis_packages)} package(s), {task_count} tasks parsed")
    else:
        print("\n  [skip] No SSIS directory found or specified")

    # ── Build unified inventory ───────────────────────────────────────────
    _section("Building inventory")
    all_sql = oltp_objects + dw_objects
    inventory = build_inventory(all_sql, ssis_packages, output_dir)
    print(f"  → {inventory['total_objects']} total objects")
    print(f"  → {inventory['unsupported_count']} unsupported/skipped")
    print(f"  → avg confidence: {inventory['summary']['avg_conversion_confidence']:.1%}")
    print()
    print("  Object type breakdown:")
    for otype, count in sorted(inventory["summary"]["by_type"].items()):
        print(f"    {otype:<35} {count:>4}")

    # ── Build dependency graph ────────────────────────────────────────────
    _section("Building dependency graph")
    graph = build_and_save_graph(inventory, output_dir)
    print(f"  → {graph['node_count']} nodes, {graph['edge_count']} edges")
    print(f"  → Cycles detected: {len(graph['cycles'])}")
    if graph["cycles"]:
        for cycle in graph["cycles"]:
            print(f"    ⚠  {'→'.join(cycle)}")
    print(f"  → ETL target objects: {len(graph['etl_lineage'])}")

    # ── Generate current-state docs ───────────────────────────────────────
    _section("Generating current_state_documentation.md")
    md_path, json_path = generate_current_state_docs(inventory, graph, output_dir)
    print(f"  → Written: {md_path}")
    print(f"  → Written: {json_path}")

    # ── Summary ───────────────────────────────────────────────────────────
    elapsed = time.time() - t0
    _section("Analysis complete")
    output_files = [
        output_dir / "inventory.json",
        output_dir / "unsupported_objects.json",
        output_dir / "dependencies.json",
        output_dir / "dependency_graph.dot",
        output_dir / "dependency_graph.md",
        output_dir / "current_state_documentation.md",
        output_dir / "current_state_summary.json",
    ]
    for f in output_files:
        size = f.stat().st_size if f.exists() else 0
        print(f"  {'✓' if f.exists() else '✗'}  {f.name:<40} {size:>8,} bytes")

    print(f"\n  Completed in {elapsed:.1f}s")
    print(f"  Outputs written to: {output_dir.resolve()}")

    high_risk = [
        o for o in inventory["objects"]
        if o.get("risk") in ("HIGH", "CRITICAL") and not o.get("object_type", "").startswith("SSIS_")
    ]
    if high_risk:
        print(f"\n  ⚠  {len(high_risk)} SQL objects flagged HIGH/CRITICAL risk:")
        for obj in sorted(high_risk, key=lambda x: x["risk"], reverse=True)[:15]:
            print(f"     [{obj['risk']:8}] {obj['id']}")

    print(f"\n  Next step: python run_impact_analysis.py --input-path {output_dir}")


if __name__ == "__main__":
    main()
