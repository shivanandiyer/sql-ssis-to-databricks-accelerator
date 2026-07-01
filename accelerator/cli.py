"""
accelerator/cli.py
Single-command entry point that runs the full modernisation pipeline
in one shot against any SQL Server / SSIS / Synapse source repository.

Usage:
    python accelerator/cli.py --source-path /path/to/your/repo

    # Custom output directories:
    python accelerator/cli.py \\
        --source-path /path/to/repo \\
        --analysis-path ./my-project/analysis \\
        --conversion-path ./my-project/converted \\
        --bundle-path ./my-project/bundle \\
        --env prod

    # Skip steps you've already run:
    python accelerator/cli.py \\
        --source-path /path/to/repo \\
        --skip-analysis \\
        --skip-ssis

    # Override architecture recommendation:
    python accelerator/cli.py --source-path /path/to/repo --architecture lakehouse

Run individual steps instead (finer control):
    python run_analysis.py --source-path ...
    python run_impact_analysis.py --input-path ./outputs
    python run_target_state_design.py --input-path ./outputs
    python run_conversion.py --input-path ./outputs --output-path ./output
    python run_ssis_conversion.py --input-path ./outputs --output-path ./output
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]  # repo root


def _parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Run the full SQL Server / SSIS / Synapse → Databricks modernisation pipeline.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Steps executed in order:
  1. parse     — scan source repo, build inventory.json + dependency graph
  2. analyse   — impact analysis, complexity scoring, risk register
  3. design    — target-state architecture + medallion mapping
  4. convert   — SQL objects → Databricks SQL / PySpark
  5. ssis      — SSIS packages → Databricks Workflows + PySpark
  6. bundle    — Databricks Asset Bundle YAML for deployment

Examples:
  python accelerator/cli.py --source-path /path/to/your/repo
  python accelerator/cli.py --source-path /repo --architecture lakehouse --env prod
  python accelerator/cli.py --source-path /repo --skip-ssis --skip-bundle
""",
    )
    # Source
    src = p.add_argument_group("source (auto-detect or explicit)")
    src.add_argument("--source-path", metavar="DIR",
                     help="Root of the source repository (auto-detects OLTP/DW/SSIS sub-dirs).")
    src.add_argument("--oltp-dir",  metavar="DIR", help="Explicit OLTP .sqlproj directory.")
    src.add_argument("--dw-dir",    metavar="DIR", help="Explicit DW .sqlproj directory.")
    src.add_argument("--ssis-dir",  metavar="DIR", help="Explicit SSIS .dtsx directory.")

    # Output
    out = p.add_argument_group("output paths")
    out.add_argument("--analysis-path",   metavar="DIR", default="./outputs",
                     help="Where to write analysis outputs (default: ./outputs).")
    out.add_argument("--conversion-path", metavar="DIR", default="./output",
                     help="Where to write converted SQL/PySpark assets (default: ./output).")
    out.add_argument("--bundle-path",     metavar="DIR", default="./bundle",
                     help="Where to write the Databricks Asset Bundle (default: ./bundle).")

    # Pipeline options
    opts = p.add_argument_group("pipeline options")
    opts.add_argument("--architecture", metavar="NAME",
                      choices=["medallion", "lakehouse", "lambda", "kappa"],
                      help="Override the recommended architecture.")
    opts.add_argument("--env", metavar="NAME", default="dev",
                      choices=["dev", "test", "prod"],
                      help="Target environment for the deployment bundle (default: dev).")

    # Skip flags
    skip = p.add_argument_group("skip steps (when re-running after partial completion)")
    skip.add_argument("--skip-analysis",  action="store_true", help="Skip parse + analyse + design.")
    skip.add_argument("--skip-sql",       action="store_true", help="Skip SQL object conversion.")
    skip.add_argument("--skip-ssis",      action="store_true", help="Skip SSIS conversion.")
    skip.add_argument("--skip-bundle",    action="store_true", help="Skip bundle generation.")

    return p.parse_args()


def _run(label: str, cmd: list[str]) -> None:
    print(f"\n{'='*60}")
    print(f"  {label}")
    print('='*60)
    t0 = time.time()
    result = subprocess.run(cmd, cwd=str(ROOT))
    elapsed = time.time() - t0
    if result.returncode != 0:
        print(f"\n  ✗ {label} failed (exit {result.returncode}) after {elapsed:.1f}s",
              file=sys.stderr)
        sys.exit(result.returncode)
    print(f"\n  ✓ {label} completed in {elapsed:.1f}s")


def main() -> None:
    args = _parse_args()

    # Validate that at least one source location was given
    has_source = (
        args.source_path
        or args.oltp_dir
        or args.dw_dir
        or args.ssis_dir
    )
    if not has_source and not args.skip_analysis:
        print("error: provide --source-path for auto-detection, or at least one of "
              "--oltp-dir / --dw-dir / --ssis-dir", file=sys.stderr)
        sys.exit(1)

    py = sys.executable

    # ── Step 1-3: Parse + Analyse + Design ───────────────────────────────
    if not args.skip_analysis:
        src_args: list[str] = []
        if args.source_path:
            src_args += ["--source-path", args.source_path]
        if args.oltp_dir:
            src_args += ["--oltp-dir", args.oltp_dir]
        if args.dw_dir:
            src_args += ["--dw-dir", args.dw_dir]
        if args.ssis_dir:
            src_args += ["--ssis-dir", args.ssis_dir]

        _run("Step 1: Parse source repository",
             [py, "run_analysis.py"] + src_args + ["--output-path", args.analysis_path])

        _run("Step 2: Impact analysis",
             [py, "run_impact_analysis.py", "--input-path", args.analysis_path])

        design_cmd = [py, "run_target_state_design.py", "--input-path", args.analysis_path]
        if args.architecture:
            design_cmd += ["--architecture", args.architecture]
        _run("Step 3: Target-state design", design_cmd)

    # ── Step 4: SQL conversion ────────────────────────────────────────────
    if not args.skip_sql:
        _run("Step 4: Convert SQL objects",
             [py, "run_conversion.py",
              "--input-path", args.analysis_path,
              "--output-path", args.conversion_path])

    # ── Step 5: SSIS conversion ───────────────────────────────────────────
    if not args.skip_ssis:
        _run("Step 5: Convert SSIS packages",
             [py, "run_ssis_conversion.py",
              "--input-path", args.analysis_path,
              "--output-path", args.conversion_path])

    # ── Step 6: Generate deployment bundle ────────────────────────────────
    if not args.skip_bundle:
        _run("Step 6: Generate Databricks Asset Bundle",
             [py, "deploy/generate_deployment_bundle.py",
              "--input-path", args.conversion_path,
              "--output-path", args.bundle_path,
              "--env", args.env])

    # ── Done ──────────────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("  Pipeline complete")
    print('='*60)
    print(f"  Analysis outputs : {Path(args.analysis_path).resolve()}")
    print(f"  Converted assets : {Path(args.conversion_path).resolve()}")
    if not args.skip_bundle:
        print(f"  Deployment bundle: {Path(args.bundle_path).resolve()}")
    print()
    print("  Review items that need manual attention:")
    print(f"    {args.conversion_path}/review_required/   ← SQL objects flagged for review")
    print(f"    {args.analysis_path}/manual_intervention_list.md")
    print()
    print(f"  To deploy: databricks bundle deploy --target {args.env}")


if __name__ == "__main__":
    main()
