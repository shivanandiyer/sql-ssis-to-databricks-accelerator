"""
run_analysis.py
Entry point for Step 2: Source Analysis Layer.

Usage:
    python run_analysis.py

Produces:
    outputs/inventory.json
    outputs/unsupported_objects.json
    outputs/dependencies.json
    outputs/dependency_graph.dot
    outputs/dependency_graph.md   (Mermaid)
    outputs/source_summary.md
"""

from __future__ import annotations

import time
from pathlib import Path

from accelerator.parsers.ssis_parser import parse_project as parse_ssis
from accelerator.parsers.sql_project_parser import parse_sqlproj
from accelerator.analyzers.inventory_builder import build_inventory
from accelerator.analyzers.dependency_graph import build_and_save_graph
from accelerator.docs.current_state_doc import generate_current_state_docs

# ── Source paths ──────────────────────────────────────────────────────────────
# Repo is cloned one directory above the accelerator project
_BASE      = Path(__file__).parent.parent
REPO_ROOT  = _BASE / "sql-server-samples" / "samples" / "databases" / "wide-world-importers"
OLTP_DIR   = REPO_ROOT / "wwi-ssdt"    / "wwi-ssdt"
DW_DIR     = REPO_ROOT / "wwi-dw-ssdt" / "wwi-dw-ssdt"
SSIS_DIR   = REPO_ROOT / "wwi-ssis"    / "wwi-ssis"
OUTPUT_DIR = Path(__file__).parent / "outputs"


def _section(title: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {title}")
    print('='*60)


def main() -> None:
    t0 = time.time()

    # ── Step 1: Parse OLTP SQL project ──────────────────────────────────────
    _section("Parsing OLTP project (wwi-ssdt)")
    oltp_objects = parse_sqlproj(OLTP_DIR, source_project="OLTP")
    print(f"  → {len(oltp_objects)} SQL objects parsed")

    # ── Step 2: Parse DW SQL project ────────────────────────────────────────
    _section("Parsing DW project (wwi-dw-ssdt)")
    dw_objects = parse_sqlproj(DW_DIR, source_project="DW")
    print(f"  → {len(dw_objects)} SQL objects parsed")

    # ── Step 3: Parse SSIS project ──────────────────────────────────────────
    _section("Parsing SSIS project (wwi-ssis)")
    ssis_packages = parse_ssis(SSIS_DIR)
    task_count = sum(len(p.get("all_tasks_flat", [])) for p in ssis_packages)
    print(f"  → {len(ssis_packages)} package(s), {task_count} tasks parsed")

    # ── Step 4: Build unified inventory ─────────────────────────────────────
    _section("Building inventory")
    all_sql = oltp_objects + dw_objects
    inventory = build_inventory(all_sql, ssis_packages, OUTPUT_DIR)
    print(f"  → {inventory['total_objects']} total objects")
    print(f"  → {inventory['unsupported_count']} unsupported/skipped")
    print(f"  → avg confidence: {inventory['summary']['avg_conversion_confidence']:.1%}")
    print()
    print("  Object type breakdown:")
    for otype, count in sorted(inventory["summary"]["by_type"].items()):
        print(f"    {otype:<35} {count:>4}")

    # ── Step 5: Build dependency graph ───────────────────────────────────────
    _section("Building dependency graph")
    graph = build_and_save_graph(inventory, OUTPUT_DIR)
    print(f"  → {graph['node_count']} nodes, {graph['edge_count']} edges")
    print(f"  → Cycles detected: {len(graph['cycles'])}")
    if graph["cycles"]:
        for cycle in graph["cycles"]:
            print(f"    ⚠️  {'→'.join(cycle)}")
    print(f"  → ETL target objects: {len(graph['etl_lineage'])}")

    # ── Step 6: Generate current-state documentation ────────────────────────
    _section("Generating current_state_documentation.md")
    md_path, json_path = generate_current_state_docs(inventory, graph, OUTPUT_DIR)
    print(f"  → Written: {md_path}")
    print(f"  → Written: {json_path}")

    # ── Final output manifest ────────────────────────────────────────────────
    elapsed = time.time() - t0
    _section("Analysis complete")
    output_files = [
        OUTPUT_DIR / "inventory.json",
        OUTPUT_DIR / "unsupported_objects.json",
        OUTPUT_DIR / "dependencies.json",
        OUTPUT_DIR / "dependency_graph.dot",
        OUTPUT_DIR / "dependency_graph.md",
        OUTPUT_DIR / "current_state_documentation.md",
        OUTPUT_DIR / "current_state_summary.json",
    ]
    for f in output_files:
        size = f.stat().st_size if f.exists() else 0
        print(f"  {'✓' if f.exists() else '✗'}  {f.name:<35} {size:>8,} bytes")

    print(f"\n  Completed in {elapsed:.1f}s")

    # Print high-risk summary
    high_risk = [
        o for o in inventory["objects"]
        if o.get("risk") in ("HIGH", "CRITICAL") and not o.get("object_type","").startswith("SSIS_")
    ]
    if high_risk:
        print(f"\n  ⚠️  {len(high_risk)} SQL objects flagged HIGH/CRITICAL risk:")
        for obj in sorted(high_risk, key=lambda x: x["risk"], reverse=True)[:15]:
            print(f"     [{obj['risk']:8}] {obj['id']}")


if __name__ == "__main__":
    main()
