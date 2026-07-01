# Coverage Gaps

> **Generated:** 2026-06-30 03:39 UTC

This matrix samples representative cases per scenario rather than testing all 419 inventory objects individually. The gaps below are deliberate scope boundaries, not oversights — each is paired with a mitigation.

## 1. Object Coverage

- 17 of 279 convertible objects (tables/views/procedures/functions) have a dedicated test case in this matrix.
- **Gap:** the remaining objects rely on the *pattern* being validated by their representative case, not individual testing.
- **Mitigation:** before production cutover, run the automated unit-test pattern from each scenario's representative case against every object sharing its classification (see `migration_risk_register.csv`'s `classification` column to enumerate the set) — this is a mechanical expansion of TC-001/TC-002/etc., not new test design.

## 2. Materialized Views

- **Gap:** zero test cases for materialized/indexed views — the WWI source corpus has none (confirmed in `conversion_decisions.md`), so no real object exists to ground a test case.
- **Mitigation:** if a future source corpus includes indexed views, add a test case following the Pattern 1 (Pure DDL conversion) template, validating the recommended scheduled-refresh-Delta-table or native Databricks SQL materialized view target.

## 3. Foreach Loops, Flat Files, Event Handlers, Conditional Branching

- **Gap:** no test cases exercise actual Foreach Loop iteration, flat-file ingestion, event-handler-triggered compensation, or expression-based precedence-constraint branching — none exist in `DailyETLMain.dtsx`.
- **Mitigation:** `unsupported_ssis_features.md` documents the intended mapping rule for each; treat that document's rules as the test-design starting point the day a package using any of them is added to scope.

## 4. Performance / Scale Testing

- **Gap:** this matrix validates correctness (row counts, schema, ordering) but does not include load/performance testing at production data volume — e.g. confirming the liquid clustering recommendation on `Fact.Sale` actually improves query performance, or that the geography-as-WKT-STRING redesign performs acceptably for spatial queries.
- **Mitigation:** add a dedicated performance test pass once a representative production-volume dataset is available in the test catalog; out of scope for this accelerator's static-analysis-driven test design.

## 5. Security / Access Model Validation

- **Gap:** no test case validates that Unity Catalog grants actually replicate the intended effect of the source `EXECUTE AS OWNER` / `GRANT`/`DENY` statements end-to-end for a real user/group.
- **Mitigation:** this requires a deployed Unity Catalog environment with real principals — track as a deployment-phase (not conversion-phase) test, to be added once Unity Catalog grants are actually issued (see `target_state_architecture.md` security note).

## 6. Cross-Entity Concurrency

- **Gap:** no test validates behaviour when multiple entity loads (e.g. City and Customer Dimension chains) run concurrently rather than sequentially, even though the target design recommends parallelising independent entity loads (`orchestration_design.md`).
- **Mitigation:** add a concurrency test once the collapsed 3-task-per-entity design (rather than this matrix's 1:1-fidelity tasks) is implemented and entity loads are actually configured to run in parallel.

## 7. Rollback Rehearsal

- **Gap:** TC for failure recovery (mid-run repair) is marked `manual` because no test environment exists yet to rehearse it; full rollback via `RESTORE TABLE ... VERSION AS OF` (per `target_state_architecture.md`'s CI/CD section) is not exercised here.
- **Mitigation:** schedule a rollback rehearsal as part of the first deployment to the test catalog, before any production cutover.
