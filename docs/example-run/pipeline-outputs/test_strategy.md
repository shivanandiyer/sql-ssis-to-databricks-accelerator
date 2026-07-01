# WWI Modernisation Accelerator — Test Strategy

> **Generated:** 2026-06-30 03:39 UTC  
> **Test cases:** 24 across 13 required scenarios

---

## Approach

Every test case is grounded in a real object from this accelerator's own output (`inventory.json`, `object_complexity_scores.json`, `conversion_manifest.json`, `workflow_spec.json`) rather than a synthetic example, so each test is directly traceable to a specific converted artefact. The three exceptions are cases that test cross-cutting *behaviour* rather than a single object (first-run watermark handling, mid-run failure recovery, dependency-graph-wide ordering, and the architecture-override mechanism) — these are marked `object_id: n/a` and tested at the pipeline/workflow level.

## Dimensions Covered

`object_type, complexity, load_style, source_pattern, target_layer, conversion_mode, confidence_band`

Full cross-product coverage of all 7 dimensions (object type × complexity × load style × source pattern × target layer × conversion mode × confidence band) would require thousands of combinations with no corresponding real object for most of them. Instead, this matrix uses **scenario-driven representative sampling**: each of the 13 required scenarios is covered by 1-3 real test cases chosen to vary at least one dimension from neighbouring cases (e.g. Scenario 1 covers a LOW-complexity Bronze table and a HIGH-complexity Bronze table with geography/temporal features). See `coverage_gaps.md` for dimension combinations this sampling does not reach.

## Test Types Used

| Test Type | Purpose | Example |
|---|---|---|
| unit | Verify a single converted object's structure/logic in isolation | TC-001 (table DDL column mapping) |
| integration | Verify multiple converted objects work together in sequence | TC-013 (sequence container task chain) |
| reconciliation | Compare converted output data against source system data | TC-012 (data flow row/column parity) |
| e2e | Full pipeline run, closest to a production cutover rehearsal | TC-014 (full package job run) |
| documentation_review | Confirm a gap is documented even where no automated test applies | TC-024 (unsupported SSIS features) |

## Automation Levels

| Level | Meaning |
|---|---|
| automated | Can run unattended in CI against a test catalog (e.g. dbt-style assert, pytest, SQL assertion query) |
| semi-automated | Automated data checks, but requires a human to confirm a business-rule interpretation |
| manual | Requires human judgement, a live parallel run, or infrastructure not yet available (e.g. repair-run rehearsal) |

## Scenario Coverage Summary

| Scenario | Test Cases | Test IDs |
|---|---|---|
| Pure DDL conversion | 3 | TC-001, TC-002, TC-003 |
| View translation | 2 | TC-004, TC-005 |
| Stored proc with set-based SQL only | 1 | TC-006 |
| Stored proc with procedural branching | 1 | TC-007 |
| Function conversion | 2 | TC-008, TC-009 |
| Fact/dimension ETL | 2 | TC-010, TC-011 |
| SSIS control flow with sequencing | 2 | TC-012, TC-013 |
| SSIS data flow with transformations | 1 | TC-014 |
| Incremental watermark logic | 3 | TC-015, TC-016, TC-017 |
| Failure recovery / rerun logic | 2 | TC-018, TC-019 |
| Dependency ordering | 2 | TC-020, TC-021 |
| Unsupported feature detection | 2 | TC-022, TC-023 |
| User-driven architecture override | 1 | TC-024 |

## Confidence-Band Test Depth Policy

| Confidence Band | Required Test Depth |
|---|---|
| HIGH | Unit test only (structural/schema assertion); spot-check in CI |
| MEDIUM | Unit + reconciliation test against a representative data sample |
| LOW | Full reconciliation + manual review sign-off before promotion to test/prod |

This mirrors the test-depth-by-classification policy already established in `impact_analysis.md` and `manual_intervention_list.md` — this document operationalises it into concrete test cases rather than introducing a new policy.

---

_See `test_matrix.csv` for the full per-case detail and `coverage_gaps.md` for what this matrix does not yet cover._