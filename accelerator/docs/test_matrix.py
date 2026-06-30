"""
test_matrix.py
Builds a comprehensive test matrix for the accelerator's output, grounded in
real converted objects from the prior steps (not synthetic placeholders,
except where the source corpus genuinely has no example of a required
object type — e.g. materialized views — which is called out explicitly).

Consumes:
    outputs/inventory.json
    outputs/object_complexity_scores.json
    outputs/medallion_mapping.csv
    output/conversion_manifest.json
    output/workflow_spec.json

Produces:
    test_matrix.csv
    test_strategy.md
    coverage_gaps.md
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCENARIOS = [
    "Pure DDL conversion",
    "View translation",
    "Stored proc with set-based SQL only",
    "Stored proc with procedural branching",
    "Function conversion",
    "Fact/dimension ETL",
    "SSIS control flow with sequencing",
    "SSIS data flow with transformations",
    "Incremental watermark logic",
    "Failure recovery / rerun logic",
    "Dependency ordering",
    "Unsupported feature detection",
    "User-driven architecture override",
]

DIMENSIONS_NOTE = (
    "object_type, complexity, load_style, source_pattern, target_layer, "
    "conversion_mode, confidence_band"
)


def _find(objs: dict[str, Any], obj_id: str) -> dict[str, Any] | None:
    return objs.get(obj_id)


def _classification(scores_by_id: dict[str, dict], obj_id: str) -> dict[str, Any]:
    return scores_by_id.get(obj_id, {})


def _confidence_band(score: float | None) -> str:
    if score is None:
        return "UNKNOWN"
    if score >= 0.8:
        return "HIGH"
    if score >= 0.6:
        return "MEDIUM"
    return "LOW"


def build_test_cases(
    inventory: dict[str, Any],
    complexity_scores: dict[str, Any],
    medallion_rows: list[dict[str, Any]],
    conversion_manifest: dict[str, Any],
    workflow_spec: dict[str, Any],
) -> list[dict[str, Any]]:
    scores_by_id = {o["id"]: o for o in complexity_scores["objects"]}
    manifest_by_id = {o["id"]: o for o in conversion_manifest["objects"]}

    cases: list[dict[str, Any]] = []
    tid = [0]

    def add(scenario: str, obj_id: str | None, object_type: str, complexity: str,
            load_style: str, source_pattern: str, target_layer: str, conversion_mode: str,
            test_description: str, expected_result: str, test_type: str,
            automation_level: str, confidence_override: float | None = None) -> None:
        tid[0] += 1
        score_entry = _classification(scores_by_id, obj_id) if obj_id else {}
        manifest_entry = manifest_by_id.get(obj_id, {}) if obj_id else {}
        confidence = confidence_override if confidence_override is not None else (
            score_entry.get("overall_score") and (1 - score_entry["overall_score"] / 5)
        )
        cases.append({
            "test_id": f"TC-{tid[0]:03d}",
            "scenario": scenario,
            "object_id": obj_id or "n/a (synthetic — see coverage_gaps.md)",
            "object_type": object_type,
            "complexity": complexity,
            "load_style": load_style,
            "source_pattern": source_pattern,
            "target_layer": target_layer,
            "conversion_mode": conversion_mode,
            "confidence_band": _confidence_band(confidence),
            "classification": score_entry.get("classification", "n/a"),
            "conversion_method": manifest_entry.get("conversion_method", "n/a"),
            "test_description": test_description,
            "expected_result": expected_result,
            "test_type": test_type,
            "automation_level": automation_level,
        })

    # ------------------------------------------------------------------
    # Scenario 1: Pure DDL conversion
    # ------------------------------------------------------------------
    add("Pure DDL conversion", "OLTP:DataLoadSimulation.FicticiousNamePool", "TABLE", "LOW", "FULL",
        "OLTP", "BRONZE", "SQL",
        "Convert a simple lookup table (no geography/temporal/memory-optimized features) DDL to Delta.",
        "Generated CREATE TABLE matches column count/order/nullability of source; classified "
        "LIFT_AND_SHIFT with no manual-review flags raised.",
        "unit", "automated")
    add("Pure DDL conversion", "OLTP:Application.Cities", "TABLE", "HIGH", "FULL",
        "OLTP", "BRONZE", "SQL",
        "Convert a table with geography column + temporal system-versioning to Delta.",
        "Geography column mapped to STRING with explicit review flag; system-versioning columns dropped with a point-in-time-filter rewrite note (not a Time Travel equivalence claim); no silent data loss.",
        "unit", "automated")
    add("Pure DDL conversion", "DW:Fact.Sale", "TABLE", "MEDIUM", "INCREMENTAL",
        "DW", "GOLD", "SQL",
        "Convert a Gold fact table DDL, confirming partition/clustering recommendation is present.",
        "DDL includes a TODO partition marker (PARTITIONED BY date key) consistent with target_state_architecture.md's file-layout recommendation.",
        "unit", "automated")

    # ------------------------------------------------------------------
    # Scenario 2: View translation
    # ------------------------------------------------------------------
    add("View translation", "OLTP:WebApi.BuyingGroups", "VIEW", "LOW", "FULL",
        "OLTP", "SILVER", "SQL",
        "Translate a simple single-table SELECT view.",
        "CREATE OR REPLACE VIEW produced with bracket identifiers converted to backticks; no warnings.",
        "unit", "automated")
    add("View translation", "OLTP:WebApi.Cities", "VIEW", "HIGH", "FULL",
        "OLTP", "SILVER", "SQL",
        "Translate a view using FOR JSON (no Spark SQL equivalent).",
        "View routed to review_required with an explicit FOR JSON -> to_json(struct(...)) rewrite note; conversion NOT silently approximated.",
        "unit", "automated")

    # ------------------------------------------------------------------
    # Scenario 3: Stored proc, set-based SQL only
    # ------------------------------------------------------------------
    add("Stored proc with set-based SQL only", "DW:Integration.MigrateStagedCityData", "PROCEDURE",
        "MEDIUM", "INCREMENTAL", "DW", "BRONZE", "SQL",
        "Convert a staging-to-DW migration procedure with no CURSOR/WHILE/dynamic SQL.",
        "Procedure converted to Databricks SQL only (no PySpark stub generated); core DML preserved.",
        "integration", "automated")

    # ------------------------------------------------------------------
    # Scenario 4: Stored proc with procedural branching
    # ------------------------------------------------------------------
    add("Stored proc with procedural branching", "OLTP:Integration.GetCityUpdates", "PROCEDURE",
        "HIGH", "INCREMENTAL", "OLTP", "BRONZE", "Workflow",
        "Convert a CURSOR/WHILE-driven change-detection procedure, orchestration-heavy.",
        "Procedure split per rule 4 into a SQL transformation file and a PySpark orchestration "
        "file; both routed to review_required with CURSOR/WHILE/temp-table factors listed.",
        "integration", "manual")

    # ------------------------------------------------------------------
    # Scenario 5: Function conversion
    # ------------------------------------------------------------------
    add("Function conversion", "OLTP:Website.CalculateCustomerPrice", "FUNCTION", "MEDIUM",
        "FULL", "OLTP", "SILVER", "SQL",
        "Convert a scalar function with multiple DECLARE statements and business-rule branching.",
        "Function routed to review_required (procedural body) rather than silently emitted as an "
        "incomplete SQL UDF; PySpark stub generated with original body preserved as comment.",
        "unit", "manual")
    add("Function conversion", "OLTP:Application.DetermineCustomerAccess", "FUNCTION", "HIGH",
        "FULL", "OLTP", "SILVER", "PySpark",
        "Convert an inline TVF that calls IS_ROLEMEMBER (security-context-dependent logic).",
        "Routed to PySpark stub with explicit warning that Unity Catalog row/column-level "
        "security must replace the SQL Server role-membership check — not auto-translated.",
        "unit", "manual")

    # ------------------------------------------------------------------
    # Scenario 6: Fact/dimension ETL
    # ------------------------------------------------------------------
    add("Fact/dimension ETL", "DW:Dimension.City", "TABLE", "HIGH", "SCD", "DW", "SILVER", "SQL",
        "Validate end-to-end City dimension load: staging -> SCD2 MERGE -> Silver table.",
        "New and changed source rows produce correctly versioned Valid From/Valid To rows; no "
        "duplicate 'current' rows per natural key.",
        "reconciliation", "semi-automated")
    add("Fact/dimension ETL", "DW:Fact.Sale", "TABLE", "MEDIUM", "INCREMENTAL", "DW", "GOLD", "SQL",
        "Validate Sale fact load resolves all dimension foreign keys correctly after Dimension loads complete.",
        "Zero orphaned fact rows (every dimension key resolves); row count matches expected daily volume +/- tolerance.",
        "reconciliation", "semi-automated")

    # ------------------------------------------------------------------
    # Scenario 7: SSIS control flow with sequencing
    # ------------------------------------------------------------------
    add("SSIS control flow with sequencing", "SSIS:DailyETLMain:Load City Dimension",
        "SSIS_SEQUENCE_CONTAINER", "MEDIUM", "INCREMENTAL", "Hybrid", "SILVER", "Workflow",
        "Validate the 4-task City Dimension chain (Truncate -> Cutoff -> Extract -> Migrate) "
        "preserves SSIS's precedence-constraint order as Workflow depends_on.",
        "Workflow task graph topologically matches the original SSIS precedence constraints; no "
        "task starts before its SSIS-defined predecessor completes.",
        "integration", "automated")
    add("SSIS control flow with sequencing", "SSIS:DailyETLMain", "SSIS_PACKAGE",
        "HIGH", "INCREMENTAL", "Hybrid", "GOLD", "Workflow",
        "Validate the full package-level job (81 tasks) runs to completion in dependency order.",
        "Full job run completes with all 13 entity chains finishing; job-level run history shows "
        "no out-of-order task starts.",
        "e2e", "manual")

    # ------------------------------------------------------------------
    # Scenario 8: SSIS data flow with transformations
    # ------------------------------------------------------------------
    add("SSIS data flow with transformations", "SSIS:DailyETLMain:Extract Updated City Data to Staging",
        "SSIS_DATA_FLOW", "LOW", "INCREMENTAL", "Hybrid", "BRONZE", "PySpark",
        "Validate the OLE DB Source (EXEC GetCityUpdates) -> Destination data flow converts to a "
        "single JDBC-read-then-Delta-write PySpark task with no in-pipeline transforms lost.",
        "Row count and column values in the Bronze staging Delta table match the SQL Server "
        "source query result for the same watermark window.",
        "reconciliation", "automated")

    # ------------------------------------------------------------------
    # Scenario 9: Incremental watermark logic
    # ------------------------------------------------------------------
    add("Incremental watermark logic", "DW:Integration.GetLastETLCutoffTime", "PROCEDURE",
        "LOW", "CDC-like window", "OLTP", "BRONZE", "SQL",
        "Validate the watermark read at the start of an entity load returns the correct prior cutoff.",
        "Watermark read returns the exact value written by the previous successful run's advance step.",
        "unit", "automated")
    add("Incremental watermark logic", "SSIS:DailyETLMain:Calculate ETL Cutoff Time backup",
        "SSIS_EXPRESSION", "MEDIUM", "CDC-like window", "Hybrid", "BRONZE", "PySpark",
        "Validate the Python translation of the SSIS expression "
        "DATEADD(\"Minute\",-5,GETUTCDATE()) (5-minute safety buffer for in-flight transactions).",
        "Computed cutoff is always exactly 5 minutes behind UTC now, across DST boundaries.",
        "unit", "automated")
    add("Incremental watermark logic", None, "WORKFLOW", "MEDIUM", "CDC-like window",
        "Hybrid", "BRONZE", "Workflow",
        "Validate first-run behaviour when ops.etl_watermark has no prior row for an entity.",
        "Pipeline performs a full initial load and writes an initial watermark row, rather than "
        "failing or silently skipping all rows.",
        "integration", "manual", confidence_override=0.6)

    # ------------------------------------------------------------------
    # Scenario 10: Failure recovery / rerun logic
    # ------------------------------------------------------------------
    add("Failure recovery / rerun logic", None, "WORKFLOW", "HIGH", "INCREMENTAL", "Hybrid",
        "SILVER", "Workflow",
        "Simulate a mid-run failure in a MERGE task (e.g. Migrate Staged City Data) and re-run "
        "using Databricks Workflows' repair-run feature.",
        "Repaired run produces an identical end-state to a clean run with no duplicate or missing "
        "rows — confirms idempotency of overwrite/MERGE-based tasks replacing SSIS checkpoint restart.",
        "e2e", "manual", confidence_override=0.55)
    add("Failure recovery / rerun logic", "SSIS:DailyETLMain:Truncate City_Staging",
        "SSIS_EXECUTE_SQL", "LOW", "FULL", "Hybrid", "BRONZE", "SQL",
        "Validate re-running the staging overwrite step twice in a row is safe.",
        "Second run produces the same staging table contents as the first (idempotent overwrite).",
        "unit", "automated")

    # ------------------------------------------------------------------
    # Scenario 11: Dependency ordering
    # ------------------------------------------------------------------
    add("Dependency ordering", None, "WORKFLOW", "MEDIUM", "FULL", "DW", "GOLD", "Workflow",
        "Validate all 6 Fact tables' MERGE tasks only run after their corresponding Dimension "
        "tables' loads complete (per dependencies.json topological order).",
        "No Fact load task starts before all Dimension tables it references have completed in the "
        "same run; topological_order from dependencies.json is preserved in the deployed job graph.",
        "integration", "semi-automated")
    add("Dependency ordering", "DW:Fact.Movement", "TABLE", "LOW", "FULL", "DW", "GOLD", "SQL",
        "Validate a 0-upstream-dependency fact table (Fact.Movement) is not blocked by an "
        "unnecessary dependency edge introduced during conversion.",
        "Fact.Movement's converted job task has no spurious depends_on entries beyond its actual source data flow.",
        "unit", "automated")

    # ------------------------------------------------------------------
    # Scenario 12: Unsupported feature detection
    # ------------------------------------------------------------------
    add("Unsupported feature detection", "OLTP:WebApi.Cities", "VIEW", "HIGH", "FULL", "OLTP",
        "SILVER", "SQL",
        "Confirm the conversion layer detects and flags FOR JSON rather than emitting broken SQL.",
        "Object appears in conversion_manifest.json with needs_review=true and in "
        "output/review_required/; equivalent entry exists in manual_intervention_list.md from the "
        "impact-analysis step.",
        "unit", "automated")
    add("Unsupported feature detection", None, "SSIS_TASK", "HIGH", "FULL", "Hybrid", "n/a",
        "Workflow",
        "Confirm Foreach Loop containers, flat-file connections, and event handlers — none present "
        "in this package — would be correctly flagged as unsupported-but-documented if encountered.",
        "unsupported_ssis_features.md explicitly lists the mapping rule for each feature even "
        "though zero instances exist in this source corpus (verified via raw DTSX inspection: 0 "
        "EventHandler elements, 0 ForEach containers, 0 Flat File connection managers).",
        "documentation_review", "manual", confidence_override=0.9)

    # ------------------------------------------------------------------
    # Scenario 13: User-driven architecture override
    # ------------------------------------------------------------------
    add("User-driven architecture override", None, "WORKFLOW", "LOW", "FULL", "DW", "n/a",
        "Workflow",
        "Run generate_target_state_design() with architecture_override='data_vault' and confirm "
        "the decision is recorded and propagated rather than silently ignored.",
        "target_state_mappings.json's architecture_decision.chosen_architecture == 'data_vault' "
        "and is_default == False, while evaluated_alternatives still documents why medallion was "
        "the default.",
        "unit", "automated", confidence_override=0.85)

    return cases


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------

CSV_HEADERS = [
    "test_id", "scenario", "object_id", "object_type", "complexity", "load_style",
    "source_pattern", "target_layer", "conversion_mode", "confidence_band",
    "classification", "conversion_method", "test_type", "automation_level",
    "test_description", "expected_result",
]


def write_test_matrix_csv(cases: list[dict[str, Any]], output_dir: Path) -> Path:
    path = output_dir / "test_matrix.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)
        for c in cases:
            writer.writerow([c[h] for h in CSV_HEADERS])
    return path


def _md_table(headers: list[str], rows: list[list[Any]]) -> list[str]:
    lines = ["| " + " | ".join(headers) + " |", "|" + "|".join(["---"] * len(headers)) + "|"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return lines


def write_test_strategy_md(cases: list[dict[str, Any]], output_dir: Path) -> Path:
    path = output_dir / "test_strategy.md"
    lines: list[str] = [
        "# WWI Modernisation Accelerator — Test Strategy",
        "",
        f"> **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}  ",
        f"> **Test cases:** {len(cases)} across 13 required scenarios",
        "",
        "---",
        "",
        "## Approach",
        "",
        "Every test case is grounded in a real object from this accelerator's own output "
        "(`inventory.json`, `object_complexity_scores.json`, `conversion_manifest.json`, "
        "`workflow_spec.json`) rather than a synthetic example, so each test is directly "
        "traceable to a specific converted artefact. The three exceptions are cases that test "
        "cross-cutting *behaviour* rather than a single object (first-run watermark handling, "
        "mid-run failure recovery, dependency-graph-wide ordering, and the architecture-override "
        "mechanism) — these are marked `object_id: n/a` and tested at the pipeline/workflow level.",
        "",
        "## Dimensions Covered", "",
        f"`{DIMENSIONS_NOTE}`",
        "",
        "Full cross-product coverage of all 7 dimensions (object type × complexity × load style × "
        "source pattern × target layer × conversion mode × confidence band) would require "
        "thousands of combinations with no corresponding real object for most of them. Instead, "
        "this matrix uses **scenario-driven representative sampling**: each of the 13 required "
        "scenarios is covered by 1-3 real test cases chosen to vary at least one dimension from "
        "neighbouring cases (e.g. Scenario 1 covers a LOW-complexity Bronze table and a "
        "HIGH-complexity Bronze table with geography/temporal features). See `coverage_gaps.md` "
        "for dimension combinations this sampling does not reach.",
        "",
        "## Test Types Used", "",
        "| Test Type | Purpose | Example |",
        "|---|---|---|",
        "| unit | Verify a single converted object's structure/logic in isolation | TC-001 (table DDL column mapping) |",
        "| integration | Verify multiple converted objects work together in sequence | TC-013 (sequence container task chain) |",
        "| reconciliation | Compare converted output data against source system data | TC-012 (data flow row/column parity) |",
        "| e2e | Full pipeline run, closest to a production cutover rehearsal | TC-014 (full package job run) |",
        "| documentation_review | Confirm a gap is documented even where no automated test applies | TC-024 (unsupported SSIS features) |",
        "",
        "## Automation Levels", "",
        "| Level | Meaning |",
        "|---|---|",
        "| automated | Can run unattended in CI against a test catalog (e.g. dbt-style assert, pytest, SQL assertion query) |",
        "| semi-automated | Automated data checks, but requires a human to confirm a business-rule interpretation |",
        "| manual | Requires human judgement, a live parallel run, or infrastructure not yet available (e.g. repair-run rehearsal) |",
        "",
    ]

    lines += ["## Scenario Coverage Summary", ""]
    by_scenario: dict[str, list[dict[str, Any]]] = {}
    for c in cases:
        by_scenario.setdefault(c["scenario"], []).append(c)
    rows = [[s, len(by_scenario.get(s, [])), ", ".join(sorted(set(c["test_id"] for c in by_scenario.get(s, []))))]
            for s in SCENARIOS]
    lines += _md_table(["Scenario", "Test Cases", "Test IDs"], rows)

    lines += ["", "## Confidence-Band Test Depth Policy", "",
              "| Confidence Band | Required Test Depth |",
              "|---|---|",
              "| HIGH | Unit test only (structural/schema assertion); spot-check in CI |",
              "| MEDIUM | Unit + reconciliation test against a representative data sample |",
              "| LOW | Full reconciliation + manual review sign-off before promotion to test/prod |",
              "",
              "This mirrors the test-depth-by-classification policy already established in "
              "`impact_analysis.md` and `manual_intervention_list.md` — this document operationalises "
              "it into concrete test cases rather than introducing a new policy.",
              "",
              "---", "",
              "_See `test_matrix.csv` for the full per-case detail and `coverage_gaps.md` for what "
              "this matrix does not yet cover._",
              ]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def write_coverage_gaps_md(cases: list[dict[str, Any]], inventory: dict[str, Any],
                            complexity_scores: dict[str, Any], output_dir: Path) -> tuple[Path, str]:
    path = output_dir / "coverage_gaps.md"

    objs = inventory["objects"]
    total_convertible = sum(1 for o in objs if o["object_type"] in
                             ("TABLE", "VIEW", "PROCEDURE", "SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI"))
    tested_object_ids = {c["object_id"] for c in cases if c["object_id"] != "n/a (synthetic — see coverage_gaps.md)"}

    lines: list[str] = [
        "# Coverage Gaps",
        "",
        f"> **Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "",
        "This matrix samples representative cases per scenario rather than testing all 419 "
        "inventory objects individually. The gaps below are deliberate scope boundaries, not "
        "oversights — each is paired with a mitigation.",
        "",
        "## 1. Object Coverage", "",
        f"- {len(tested_object_ids)} of {total_convertible} convertible objects (tables/views/"
        "procedures/functions) have a dedicated test case in this matrix.",
        "- **Gap:** the remaining objects rely on the *pattern* being validated by their "
        "representative case, not individual testing.",
        "- **Mitigation:** before production cutover, run the automated unit-test pattern from "
        "each scenario's representative case against every object sharing its classification "
        "(see `migration_risk_register.csv`'s `classification` column to enumerate the set) — this "
        "is a mechanical expansion of TC-001/TC-002/etc., not new test design.",
        "",
        "## 2. Materialized Views", "",
        "- **Gap:** zero test cases for materialized/indexed views — the WWI source corpus has "
        "none (confirmed in `conversion_decisions.md`), so no real object exists to ground a test case.",
        "- **Mitigation:** if a future source corpus includes indexed views, add a test case "
        "following the Pattern 1 (Pure DDL conversion) template, validating the recommended "
        "scheduled-refresh-Delta-table or native Databricks SQL materialized view target.",
        "",
        "## 3. Foreach Loops, Flat Files, Event Handlers, Conditional Branching", "",
        "- **Gap:** no test cases exercise actual Foreach Loop iteration, flat-file ingestion, "
        "event-handler-triggered compensation, or expression-based precedence-constraint branching "
        "— none exist in `DailyETLMain.dtsx`.",
        "- **Mitigation:** `unsupported_ssis_features.md` documents the intended mapping rule for "
        "each; treat that document's rules as the test-design starting point the day a package "
        "using any of them is added to scope.",
        "",
        "## 4. Performance / Scale Testing", "",
        "- **Gap:** this matrix validates correctness (row counts, schema, ordering) but does not "
        "include load/performance testing at production data volume — e.g. confirming the liquid "
        "clustering recommendation on `Fact.Sale` actually improves query performance, or that the "
        "geography-as-WKT-STRING redesign performs acceptably for spatial queries.",
        "- **Mitigation:** add a dedicated performance test pass once a representative production-"
        "volume dataset is available in the test catalog; out of scope for this accelerator's "
        "static-analysis-driven test design.",
        "",
        "## 5. Security / Access Model Validation", "",
        "- **Gap:** no test case validates that Unity Catalog grants actually replicate the "
        "intended effect of the source `EXECUTE AS OWNER` / `GRANT`/`DENY` statements end-to-end "
        "for a real user/group.",
        "- **Mitigation:** this requires a deployed Unity Catalog environment with real "
        "principals — track as a deployment-phase (not conversion-phase) test, to be added once "
        "Unity Catalog grants are actually issued (see `target_state_architecture.md` security "
        "note).",
        "",
        "## 6. Cross-Entity Concurrency", "",
        "- **Gap:** no test validates behaviour when multiple entity loads (e.g. City and Customer "
        "Dimension chains) run concurrently rather than sequentially, even though the target "
        "design recommends parallelising independent entity loads (`orchestration_design.md`).",
        "- **Mitigation:** add a concurrency test once the collapsed 3-task-per-entity design "
        "(rather than this matrix's 1:1-fidelity tasks) is implemented and entity loads are "
        "actually configured to run in parallel.",
        "",
        "## 7. Rollback Rehearsal", "",
        "- **Gap:** TC for failure recovery (mid-run repair) is marked `manual` because no test "
        "environment exists yet to rehearse it; full rollback via `RESTORE TABLE ... VERSION AS "
        "OF` (per `target_state_architecture.md`'s CI/CD section) is not exercised here.",
        "- **Mitigation:** schedule a rollback rehearsal as part of the first deployment to the "
        "test catalog, before any production cutover.",
        "",
    ]
    return path, "\n".join(lines)


def generate_test_matrix(
    inventory: dict[str, Any],
    complexity_scores: dict[str, Any],
    medallion_rows: list[dict[str, Any]],
    conversion_manifest: dict[str, Any],
    workflow_spec: dict[str, Any],
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    cases = build_test_cases(inventory, complexity_scores, medallion_rows, conversion_manifest, workflow_spec)

    csv_path = write_test_matrix_csv(cases, output_dir)
    strategy_path = write_test_strategy_md(cases, output_dir)
    gaps_path, gaps_content = write_coverage_gaps_md(cases, inventory, complexity_scores, output_dir)
    gaps_path.write_text(gaps_content, encoding="utf-8")

    return {"test_matrix_csv": csv_path, "test_strategy_md": strategy_path, "coverage_gaps_md": gaps_path}
