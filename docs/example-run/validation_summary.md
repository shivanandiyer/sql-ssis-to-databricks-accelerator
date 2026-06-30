# End-to-End Validation Summary

> **Generated:** 2026-06-30 04:57 UTC  
> **Total duration:** 5.41s  
> **Overall status: PARTIAL**  
> **Steps:** 10 passed, 1 partial, 0 failed (of 11)

---

## What Passed

- **Step 1 — Parse source repo** (3.975s): oltp_files_parsed=283, dw_files_parsed=71, ssis_packages_parsed=1, unreadable_files=0
- **Step 3 — Build dependency graph** (0.013s): node_count=414, edge_count=584, has_cycles=False, etl_lineage_targets=14
- **Step 4 — Produce documentation** (0.005s): markdown_bytes=44937, json_bytes=7693, sections_with_confidence=14
- **Step 5 — Produce impact analysis** (0.31s): object_count=431, classification_distribution=<dict len=4>
- **Step 6 — Recommend target architecture** (0.006s): chosen_architecture=medallion, medallion_layer_distribution={'BRONZE': 72, 'SILVER': 34, 'GOLD': 6}
- **Step 7 — Convert SQL objects** (0.076s): objects_processed=279, needs_review_count=201, exceptions_raised=0
- **Step 8 — Convert SSIS packages** (0.042s): workflow_tasks_generated=81, connection_managers_mapped=2, variables_mapped=4
- **Step 9 — Build deployment artifacts** (0.0s): task_file_references_checked=81, broken_references=0, broken_reference_paths_sample=[]
- **Step 10 — Run automated tests** (0.964s): pytest_exit_code=0, passed=117, failed=0, skipped=0
- **Step 11 — Compare outputs with golden results** (0.004s): golden_cases_checked=2, mismatches=0

## What Partially Passed

### Step 2 — Extract object inventory [NON_BLOCKING]

- **Evidence:** total_objects=431, unsupported_count=18, avg_conversion_confidence=0.724, object_type_breakdown=<dict len=13>, known_misparsed_names_found=['OLTP:dbo.Application', 'OLTP:dbo.DataLoadSimulation', 'OLTP:dbo.Integration']
- **Why partial:** Object name-extraction fallback still misparses some multi-word GRANT/security statement files (e.g. 'External Sales.sql' -> dbo.External) — cosmetic, routed to SECURITY/unsupported, doesn't affect functional conversion.
- **Failure category:** Implementation bug in the accelerator itself

## What Failed

_None._
---

## Failure Category Breakdown

| Category | Step Count |
|---|---|
| Implementation bug in the accelerator itself | 1 |

---

## Object-Level Disposition (from Step 7: SQL conversion)

- Objects processed: 279
- Flagged needs_review (partial/manual): 201
- Conversion exceptions (would indicate a real implementation bug): 0

_needs_review objects are an **expected** outcome of the accelerator's design (deliberately surfacing ambiguous/unsupported constructs rather than guessing), not a validation failure — see `manual_intervention_list.md` from the impact-analysis step for the full per-object breakdown._

---

## Must-Fix Before Accelerator Release

Ordered by severity. See `recommended_backlog.md` for full detail and suggested owners.


### Non-Blocking Issues (tracked, not release-blocking)

1. **Step 2 (Extract object inventory)** — Object name-extraction fallback still misparses some multi-word GRANT/security statement files (e.g. 'External Sales.sql' -> dbo.External) — cosmetic, routed to SECURITY/unsupported, doesn't affect functional conversion.