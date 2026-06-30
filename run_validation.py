"""
run_validation.py
End-to-end validation of the WWI Modernisation Accelerator against the real
Wide World Importers sample repository.

Runs all 12 validation steps fresh (re-parsing the source repo, not reusing
any previously cached outputs), records pass/partial/fail status with
evidence for each step, runs the pytest suite, diffs golden snapshots, and
produces (under docs/example-run/):
    validation_summary.md
    validation_results.json
    failed_cases.json
    recommended_backlog.md

Usage:
    python run_validation.py
"""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent
OUTPUTS_DIR = ROOT / "outputs"
OUTPUT_DIR = ROOT / "output"
EXAMPLE_RUN_DIR = ROOT / "docs" / "example-run"

sys.path.insert(0, str(ROOT))

from accelerator.parsers.ssis_parser import parse_project as parse_ssis
from accelerator.parsers.sql_project_parser import parse_sqlproj
from accelerator.analyzers.inventory_builder import build_inventory
from accelerator.analyzers.dependency_graph import build_and_save_graph
from accelerator.docs.current_state_doc import generate_current_state_docs
from accelerator.analyzers.impact_analysis import run_impact_analysis
from accelerator.docs.target_state_design import generate_target_state_design
from accelerator.converters.sql_converter import convert_table, convert_view, convert_function, convert_procedure
from accelerator.converters.ssis_converter import convert_ssis_package

_BASE = ROOT.parent
REPO_ROOT = _BASE / "sql-server-samples" / "samples" / "databases" / "wide-world-importers"
OLTP_DIR = REPO_ROOT / "wwi-ssdt" / "wwi-ssdt"
DW_DIR = REPO_ROOT / "wwi-dw-ssdt" / "wwi-dw-ssdt"
SSIS_DIR = REPO_ROOT / "wwi-ssis" / "wwi-ssis"

CONVERTIBLE_TYPES = {"TABLE", "VIEW", "PROCEDURE", "SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI"}

results: list[dict[str, Any]] = []
failed_cases: list[dict[str, Any]] = []


def record(step_no: int, name: str, status: str, duration: float, evidence: dict[str, Any],
           failure_reason: str | None = None, failure_category: str | None = None,
           severity: str | None = None) -> None:
    entry = {
        "step": step_no,
        "name": name,
        "status": status,  # PASS | PARTIAL | FAIL
        "duration_seconds": round(duration, 3),
        "evidence": evidence,
    }
    if status != "PASS":
        entry["failure_reason"] = failure_reason
        entry["failure_category"] = failure_category  # unsupported_source_semantics | ambiguous_intent | implementation_bug | expected_manual_scope
        # BLOCKING: breaks a downstream deliverable or produces incorrect output.
        # NON_BLOCKING: cosmetic / informational, no functional impact.
        entry["severity"] = severity or ("BLOCKING" if status == "FAIL" else "NON_BLOCKING")
        failed_cases.append(entry)
    results.append(entry)
    icon = {"PASS": "✓", "PARTIAL": "△", "FAIL": "✗"}[status]
    print(f"  {icon} Step {step_no:2d} [{status:7s}] {name} ({duration:.2f}s)")


def main() -> None:
    print("=" * 70)
    print("  WWI MODERNISATION ACCELERATOR — END-TO-END VALIDATION")
    print("=" * 70)
    t_start = time.time()

    # ── Step 1: Parse source repo ────────────────────────────────────────
    t0 = time.time()
    oltp_objects = parse_sqlproj(OLTP_DIR, source_project="OLTP")
    dw_objects = parse_sqlproj(DW_DIR, source_project="DW")
    ssis_packages = parse_ssis(SSIS_DIR)
    all_sql = oltp_objects + dw_objects
    parse_errors = [o for o in all_sql if o.get("object_type") in ("UNREADABLE",)]
    status = "PASS" if not parse_errors and oltp_objects and dw_objects and ssis_packages else "PARTIAL"
    record(1, "Parse source repo", status, time.time() - t0, {
        "oltp_files_parsed": len(oltp_objects),
        "dw_files_parsed": len(dw_objects),
        "ssis_packages_parsed": len(ssis_packages),
        "unreadable_files": len(parse_errors),
    }, failure_reason=f"{len(parse_errors)} files unreadable" if parse_errors else None,
       failure_category="implementation_bug" if parse_errors else None)

    # ── Step 2: Extract object inventory ─────────────────────────────────
    t0 = time.time()
    inventory = build_inventory(all_sql, ssis_packages, OUTPUTS_DIR)
    expected_min_objects = 400
    misnamed = [o for o in inventory["objects"]
                if o.get("name", "") in ("Application", "DataLoadSimulation", "Integration", "External", "Far")
                and o.get("source_project") == "OLTP"]
    status = "PASS" if inventory["total_objects"] >= expected_min_objects and not misnamed else "PARTIAL"
    record(2, "Extract object inventory", status, time.time() - t0, {
        "total_objects": inventory["total_objects"],
        "unsupported_count": inventory["unsupported_count"],
        "avg_conversion_confidence": inventory["summary"]["avg_conversion_confidence"],
        "object_type_breakdown": inventory["summary"]["by_type"],
        "known_misparsed_names_found": [o["id"] for o in misnamed],
    }, failure_reason="Object name-extraction fallback still misparses some multi-word GRANT/security "
                       "statement files (e.g. 'External Sales.sql' -> dbo.External) — cosmetic, routed "
                       "to SECURITY/unsupported, doesn't affect functional conversion."
       if misnamed else None,
       failure_category="implementation_bug" if misnamed else None,
       severity="NON_BLOCKING")

    # ── Step 3: Build dependency graph ───────────────────────────────────
    t0 = time.time()
    graph = build_and_save_graph(inventory, OUTPUTS_DIR)
    status = "PASS" if not graph["has_cycles"] and graph["node_count"] > 0 else "FAIL"
    record(3, "Build dependency graph", status, time.time() - t0, {
        "node_count": graph["node_count"],
        "edge_count": graph["edge_count"],
        "has_cycles": graph["has_cycles"],
        "etl_lineage_targets": len(graph["etl_lineage"]),
    }, failure_reason="Cycles detected in dependency graph" if graph["has_cycles"] else None,
       failure_category="implementation_bug" if graph["has_cycles"] else None)

    # ── Step 4: Produce documentation ────────────────────────────────────
    t0 = time.time()
    try:
        md_path, json_path = generate_current_state_docs(inventory, graph, OUTPUTS_DIR)
        doc_summary = json.loads(json_path.read_text(encoding="utf-8"))
        sections_ok = len(doc_summary.get("confidence_by_section", {})) >= 10
        status = "PASS" if md_path.exists() and json_path.exists() and sections_ok else "PARTIAL"
        record(4, "Produce documentation", status, time.time() - t0, {
            "markdown_bytes": md_path.stat().st_size,
            "json_bytes": json_path.stat().st_size,
            "sections_with_confidence": len(doc_summary.get("confidence_by_section", {})),
        }, failure_reason="Fewer than 10 documented sections" if not sections_ok else None,
           failure_category="implementation_bug" if not sections_ok else None)
    except Exception as exc:
        record(4, "Produce documentation", "FAIL", time.time() - t0, {}, str(exc), "implementation_bug")

    # ── Step 5: Produce impact analysis ──────────────────────────────────
    t0 = time.time()
    try:
        impact_paths = run_impact_analysis(inventory, graph, OUTPUTS_DIR)
        scores = json.loads(impact_paths["complexity_scores_json"].read_text(encoding="utf-8"))
        dist = scores["classification_distribution"]
        total_classified = sum(dist.values())
        status = "PASS" if total_classified == scores["object_count"] else "FAIL"
        record(5, "Produce impact analysis", status, time.time() - t0, {
            "object_count": scores["object_count"],
            "classification_distribution": dist,
        }, failure_reason="Classification counts don't sum to total object count" if status == "FAIL" else None,
           failure_category="implementation_bug" if status == "FAIL" else None)
    except Exception as exc:
        record(5, "Produce impact analysis", "FAIL", time.time() - t0, {}, str(exc), "implementation_bug")
        scores = {"objects": []}

    # ── Step 6: Recommend target architecture ────────────────────────────
    t0 = time.time()
    try:
        target_paths = generate_target_state_design(inventory, graph, scores, OUTPUTS_DIR)
        mappings = json.loads(target_paths["target_state_mappings_json"].read_text(encoding="utf-8"))
        decision = mappings["architecture_decision"]
        status = "PASS" if decision["chosen_architecture"] == "medallion" and decision["is_default"] else "PARTIAL"
        record(6, "Recommend target architecture", status, time.time() - t0, {
            "chosen_architecture": decision["chosen_architecture"],
            "medallion_layer_distribution": mappings["medallion_layer_distribution"],
        })
    except Exception as exc:
        record(6, "Recommend target architecture", "FAIL", time.time() - t0, {}, str(exc), "implementation_bug")

    # ── Step 7: Convert SQL objects ──────────────────────────────────────
    t0 = time.time()
    conversion_errors: list[dict[str, Any]] = []
    converted_count = 0
    needs_review_count = 0
    classification_by_id = {o["id"]: o["classification"] for o in scores.get("objects", [])}
    medallion_rows = []
    try:
        with (OUTPUTS_DIR / "medallion_mapping.csv").open(encoding="utf-8") as f:
            medallion_rows = list(csv.DictReader(f))
    except FileNotFoundError:
        pass
    medallion_by_id = {r["source_id"]: r["target_fqn"] for r in medallion_rows}

    for obj in inventory["objects"]:
        if obj["object_type"] not in CONVERTIBLE_TYPES:
            continue
        target_fqn = medallion_by_id.get(obj["id"], f"wwi_<env>.{obj.get('medallion_layer','bronze').lower()}.x")
        try:
            if obj["object_type"] == "TABLE":
                r = convert_table(obj, target_fqn)
            elif obj["object_type"] == "VIEW":
                r = convert_view(obj, target_fqn)
            elif obj["object_type"] in ("SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI"):
                r = convert_function(obj, target_fqn)
            else:
                r = convert_procedure(obj, classification_by_id.get(obj["id"], "PARTIAL_AUTOMATION"), target_fqn)
            converted_count += 1
            if r.get("needs_review"):
                needs_review_count += 1
        except Exception as exc:
            conversion_errors.append({"id": obj["id"], "object_type": obj["object_type"], "error": str(exc)})

    status = "PASS" if not conversion_errors else "FAIL"
    record(7, "Convert SQL objects", status, time.time() - t0, {
        "objects_processed": converted_count,
        "needs_review_count": needs_review_count,
        "exceptions_raised": len(conversion_errors),
    }, failure_reason=f"{len(conversion_errors)} objects raised exceptions during conversion" if conversion_errors else None,
       failure_category="implementation_bug" if conversion_errors else None)
    for e in conversion_errors:
        failed_cases.append({"step": 7, "name": "Convert SQL objects", **e, "failure_category": "implementation_bug"})

    # ── Step 8: Convert SSIS packages ────────────────────────────────────
    t0 = time.time()
    try:
        ssis_paths = convert_ssis_package(inventory, graph, OUTPUT_DIR)
        workflow_spec = json.loads(ssis_paths["workflow_spec"].read_text(encoding="utf-8"))
        n_tasks = len(workflow_spec["tasks"])
        status = "PASS" if n_tasks > 0 else "FAIL"
        record(8, "Convert SSIS packages", status, time.time() - t0, {
            "workflow_tasks_generated": n_tasks,
            "connection_managers_mapped": len(workflow_spec["connection_managers"]),
            "variables_mapped": len(workflow_spec["variables"]),
        })
    except Exception as exc:
        record(8, "Convert SSIS packages", "FAIL", time.time() - t0, {}, str(exc), "implementation_bug")
        workflow_spec = {"tasks": []}

    # ── Step 9: Build deployment artifacts (referential integrity check) ─
    t0 = time.time()
    broken_refs: list[str] = []
    for t in workflow_spec.get("tasks", []):
        if t.get("sql_task"):
            p = OUTPUT_DIR / t["sql_task"]["file"]["path"]
            if not p.exists():
                broken_refs.append(str(p))
        if t.get("notebook_task"):
            p = OUTPUT_DIR / t["notebook_task"]["notebook_path"].replace("./", "")
            if not p.exists():
                broken_refs.append(str(p))
    status = "PASS" if not broken_refs else "PARTIAL"
    record(9, "Build deployment artifacts", status, time.time() - t0, {
        "task_file_references_checked": len(workflow_spec.get("tasks", [])),
        "broken_references": len(broken_refs),
        "broken_reference_paths_sample": broken_refs[:5],
    }, failure_reason=f"{len(broken_refs)} Workflow task file references point to files that don't "
                       "exist on disk — inline-SQL Execute SQL tasks (e.g. 'Truncate City_Staging', a "
                       "raw DELETE statement, not a procedure call) never receive an output file from "
                       "the SQL conversion layer at all, but build_workflow_spec() unconditionally "
                       "assumes a databricks_sql/{task_key}.sql file exists for every sql_task. "
                       "Deploying this bundle as-is would fail at job-run time." if broken_refs else None,
       failure_category="implementation_bug" if broken_refs else None,
       severity="BLOCKING" if broken_refs else None)

    # ── Step 10: Run automated tests ─────────────────────────────────────
    t0 = time.time()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short"],
        cwd=ROOT, capture_output=True, text=True,
    )
    passed = proc.stdout.count(" PASSED")
    failed = proc.stdout.count(" FAILED")
    skipped = proc.stdout.count(" SKIPPED")
    status = "PASS" if proc.returncode == 0 else "FAIL"
    record(10, "Run automated tests", status, time.time() - t0, {
        "pytest_exit_code": proc.returncode,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
    }, failure_reason=f"pytest exited with code {proc.returncode}" if proc.returncode != 0 else None,
       failure_category="implementation_bug" if proc.returncode != 0 else None)
    if proc.returncode != 0:
        failed_cases.append({"step": 10, "name": "Run automated tests",
                              "stdout_tail": proc.stdout[-2000:], "stderr_tail": proc.stderr[-2000:],
                              "failure_category": "implementation_bug"})

    # ── Step 11: Compare outputs with expected golden results ───────────
    t0 = time.time()
    from accelerator.parsers.sql_project_parser import classify_sql_file
    golden_mismatches: list[dict[str, str]] = []
    golden_cases = [
        ("fixtures/sql/simple_table_lift_and_shift.sql", "golden_outputs/simple_table_lift_and_shift.sql",
         "wwi_dev.bronze.application__deliverymethods"),
        ("fixtures/sql/geography_temporal_table.sql", "golden_outputs/geography_temporal_table.sql",
         "wwi_dev.bronze.application__cities"),
    ]
    for fixture_rel, golden_rel, target_fqn in golden_cases:
        fixture_path, golden_path = ROOT / fixture_rel, ROOT / golden_rel
        if not golden_path.exists():
            golden_mismatches.append({"fixture": fixture_rel, "reason": "golden file missing"})
            continue
        obj = classify_sql_file(fixture_path, source_project="OLTP")
        obj["medallion_layer"] = "BRONZE"
        actual = convert_table(obj, target_fqn)["sql"]
        expected = golden_path.read_text(encoding="utf-8")
        if actual != expected:
            golden_mismatches.append({"fixture": fixture_rel, "reason": "output diverged from golden file"})
    status = "PASS" if not golden_mismatches else "FAIL"
    record(11, "Compare outputs with golden results", status, time.time() - t0, {
        "golden_cases_checked": len(golden_cases),
        "mismatches": len(golden_mismatches),
    }, failure_reason=f"{len(golden_mismatches)} of {len(golden_cases)} golden comparisons diverged" if golden_mismatches else None,
       failure_category="implementation_bug" if golden_mismatches else None)
    for m in golden_mismatches:
        failed_cases.append({"step": 11, "name": "Compare outputs with golden results", **m, "failure_category": "implementation_bug"})

    # ── Step 12: Produce final validation summary (this script's own output) ─
    t_total = time.time() - t_start
    write_outputs(t_total)
    print(f"\n  Total validation time: {t_total:.1f}s")

    # CI exit code: a hard FAIL (not PARTIAL — this project treats PARTIAL as
    # an acceptable, by-design state, e.g. expected manual-review scope) means
    # something is actually broken and the build should fail.
    blocking_failures = [s for s in results if s["status"] == "FAIL"
                          or s.get("severity") == "BLOCKING"]
    if blocking_failures:
        print(f"\n  ✗ {len(blocking_failures)} blocking failure(s) — see failed_cases.json")
        sys.exit(1)


def write_outputs(total_duration: float) -> None:
    EXAMPLE_RUN_DIR.mkdir(parents=True, exist_ok=True)
    pass_count = sum(1 for r in results if r["status"] == "PASS")
    partial_count = sum(1 for r in results if r["status"] == "PARTIAL")
    fail_count = sum(1 for r in results if r["status"] == "FAIL")

    validation_results = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_duration_seconds": round(total_duration, 2),
        "steps_total": len(results),
        "steps_passed": pass_count,
        "steps_partial": partial_count,
        "steps_failed": fail_count,
        "overall_status": "PASS" if fail_count == 0 and partial_count == 0
                           else ("PARTIAL" if fail_count == 0 else "FAIL"),
        "steps": results,
    }
    (EXAMPLE_RUN_DIR / "validation_results.json").write_text(
        json.dumps(validation_results, indent=2, default=str), encoding="utf-8"
    )
    (EXAMPLE_RUN_DIR / "failed_cases.json").write_text(
        json.dumps({"generated_at": datetime.now(timezone.utc).isoformat(),
                     "failed_case_count": len(failed_cases),
                     "cases": failed_cases}, indent=2, default=str),
        encoding="utf-8",
    )

    write_validation_summary_md(validation_results)
    write_recommended_backlog_md(validation_results)


CATEGORY_LABEL = {
    "unsupported_source_semantics": "Unsupported source semantics (no Databricks equivalent exists)",
    "ambiguous_intent": "Ambiguous source intent (multiple valid interpretations)",
    "implementation_bug": "Implementation bug in the accelerator itself",
    "expected_manual_scope": "Expected manual-review scope (by design, not a defect)",
}


def write_validation_summary_md(vr: dict[str, Any]) -> None:
    lines: list[str] = [
        "# End-to-End Validation Summary",
        "",
        f"> **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"> **Total duration:** {vr['total_duration_seconds']}s  ",
        f"> **Overall status: {vr['overall_status']}**  ",
        f"> **Steps:** {vr['steps_passed']} passed, {vr['steps_partial']} partial, {vr['steps_failed']} failed (of {vr['steps_total']})",
        "",
        "---", "",
        "## What Passed", "",
    ]
    passed = [s for s in vr["steps"] if s["status"] == "PASS"]
    for s in passed:
        lines.append(f"- **Step {s['step']} — {s['name']}** ({s['duration_seconds']}s): "
                      f"{_evidence_summary(s['evidence'])}")

    lines += ["", "## What Partially Passed", ""]
    partial = [s for s in vr["steps"] if s["status"] == "PARTIAL"]
    if not partial:
        lines.append("_None._")
    for s in partial:
        lines += [
            f"### Step {s['step']} — {s['name']} [{s.get('severity', 'n/a')}]",
            "",
            f"- **Evidence:** {_evidence_summary(s['evidence'])}",
            f"- **Why partial:** {s.get('failure_reason')}",
            f"- **Failure category:** {CATEGORY_LABEL.get(s.get('failure_category'), 'n/a')}",
            "",
        ]

    lines += ["## What Failed", ""]
    failed = [s for s in vr["steps"] if s["status"] == "FAIL"]
    if not failed:
        lines.append("_None._")
    for s in failed:
        lines += [
            f"### Step {s['step']} — {s['name']}",
            "",
            f"- **Evidence:** {_evidence_summary(s['evidence'])}",
            f"- **Why it failed:** {s.get('failure_reason')}",
            f"- **Failure category:** {CATEGORY_LABEL.get(s.get('failure_category'), 'n/a')}",
            "",
        ]

    lines += ["---", "", "## Failure Category Breakdown", "",
              "| Category | Step Count |", "|---|---|"]
    cat_counts: dict[str, int] = {}
    for s in vr["steps"]:
        if s["status"] != "PASS":
            cat = s.get("failure_category") or "uncategorised"
            cat_counts[cat] = cat_counts.get(cat, 0) + 1
    for cat, count in cat_counts.items():
        lines.append(f"| {CATEGORY_LABEL.get(cat, cat)} | {count} |")
    if not cat_counts:
        lines.append("| _None — all steps passed_ | 0 |")

    lines += ["", "---", "", "## Object-Level Disposition (from Step 7: SQL conversion)", ""]
    step7 = next((s for s in vr["steps"] if s["step"] == 7), None)
    if step7:
        ev = step7["evidence"]
        lines += [
            f"- Objects processed: {ev.get('objects_processed')}",
            f"- Flagged needs_review (partial/manual): {ev.get('needs_review_count')}",
            f"- Conversion exceptions (would indicate a real implementation bug): {ev.get('exceptions_raised')}",
            "",
            "_needs_review objects are an **expected** outcome of the accelerator's design "
            "(deliberately surfacing ambiguous/unsupported constructs rather than guessing), "
            "not a validation failure — see `manual_intervention_list.md` from the impact-analysis "
            "step for the full per-object breakdown._",
        ]

    lines += ["", "---", "",
              "## Must-Fix Before Accelerator Release", "",
              "Ordered by severity. See `recommended_backlog.md` for full detail and suggested owners.", ""]
    must_fix = [s for s in vr["steps"] if s.get("severity") == "BLOCKING"]
    if must_fix:
        for i, s in enumerate(must_fix, 1):
            lines.append(f"{i}. **Step {s['step']} ({s['name']})** — {s.get('failure_reason')}")
    non_blocking = [s for s in vr["steps"] if s["status"] != "PASS" and s.get("severity") == "NON_BLOCKING"]
    if non_blocking:
        lines += ["", "### Non-Blocking Issues (tracked, not release-blocking)", ""]
        for i, s in enumerate(non_blocking, 1):
            lines.append(f"{i}. **Step {s['step']} ({s['name']})** — {s.get('failure_reason')}")
    else:
        lines.append("_No release-blocking implementation bugs found in this run. See "
                      "`recommended_backlog.md` for non-blocking improvements._")

    (EXAMPLE_RUN_DIR / "validation_summary.md").write_text("\n".join(lines), encoding="utf-8")


def _evidence_summary(evidence: dict[str, Any]) -> str:
    parts = []
    for k, v in evidence.items():
        if isinstance(v, (dict, list)) and len(str(v)) > 80:
            parts.append(f"{k}=<{type(v).__name__} len={len(v)}>")
        else:
            parts.append(f"{k}={v}")
    return ", ".join(parts)


def write_recommended_backlog_md(vr: dict[str, Any]) -> None:
    lines: list[str] = [
        "# Recommended Backlog",
        "",
        f"> Derived from the end-to-end validation run on {datetime.now(timezone.utc).strftime('%Y-%m-%d')}.",
        "",
        "## Release Blockers (implementation bugs found this run)", "",
    ]
    blockers = [s for s in vr["steps"] if s.get("severity") == "BLOCKING"]
    if blockers:
        for s in blockers:
            lines += [f"### {s['name']} (Step {s['step']})", "",
                      f"- {s.get('failure_reason')}",
                      f"- Evidence: {_evidence_summary(s['evidence'])}", ""]
    else:
        lines.append("_None found in this run._")

    lines += ["", "## Non-Blocking Follow-Ups (carried over from prior steps, still open)", "",
              "These were identified during earlier accelerator development and are not "
              "re-validated by this run, but remain open:", "",
              "1. **Cosmetic name-extraction gap** — multi-word GRANT/security statement files "
              "(e.g. `External Sales.sql`) still produce truncated object names (`dbo.External`). "
              "Routed to SECURITY/unsupported either way; zero functional impact, but worth a "
              "proper fix for inventory readability.",
              "2. **Dead-code confidence deduction** — `inventory_builder._DEDUCTIONS`' "
              "`TEMPORAL`/`MEMORY_OPTIMIZED` keys never match `complexity_factors` (only "
              "`table_features`), so those penalties never apply. Low priority since impact "
              "analysis's separate, more thorough scoring model already captures this risk.",
              "3. **Lineage metric naming** — `extract_etl_lineage`'s `upstream_count` is actually "
              "fan-in (consumers), not fan-out (dependencies). Already published in "
              "`current_state_documentation.md`; renaming the field would be a breaking change to "
              "a delivered artifact — recommend a documentation clarification instead of a code change.",
              "4. **SQL conversion core-DML extraction** is regex-based best-effort for CURSOR-bodied "
              "procedures — correctly extracts INSERT statements but doesn't reconstruct full control "
              "flow. Acceptable since these procedures are always routed to manual review, but worth "
              "strengthening if CURSOR-heavy corpora become more common in future source repos.",
              "5. **Scalar function signature parsing** — converted SQL UDFs leave parameter list and "
              "return type as `TODO` placeholders rather than parsed from source DDL.",
              "",
              "## Process Recommendations", "",
              "- Re-run this validation script after any change to `accelerator/parsers/`, "
              "`accelerator/analyzers/`, or `accelerator/converters/` — it is the only check that "
              "exercises the full pipeline against the real source repo end-to-end rather than "
              "fixtures alone.",
              "- Treat any new `FAIL` with `failure_category: implementation_bug` as a release "
              "blocker; `PARTIAL` results and `expected_manual_scope` failures are acceptable "
              "release states by design.",
              "- Keep `golden_outputs/` snapshot tests as the first line of defense against silent "
              "regressions in deterministic conversion output — regenerate only via the explicit "
              "`REGENERATE_GOLDEN=1` flag, never automatically.",
              ]
    (EXAMPLE_RUN_DIR / "recommended_backlog.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    main()
