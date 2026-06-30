# Recommended Backlog

> Derived from the end-to-end validation run on 2026-06-30.

## Release Blockers (implementation bugs found this run)

_None found in this run._

## Non-Blocking Follow-Ups (carried over from prior steps, still open)

These were identified during earlier accelerator development and are not re-validated by this run, but remain open:

1. **Cosmetic name-extraction gap** — multi-word GRANT/security statement files (e.g. `External Sales.sql`) still produce truncated object names (`dbo.External`). Routed to SECURITY/unsupported either way; zero functional impact, but worth a proper fix for inventory readability.
2. **Dead-code confidence deduction** — `inventory_builder._DEDUCTIONS`' `TEMPORAL`/`MEMORY_OPTIMIZED` keys never match `complexity_factors` (only `table_features`), so those penalties never apply. Low priority since impact analysis's separate, more thorough scoring model already captures this risk.
3. **Lineage metric naming** — `extract_etl_lineage`'s `upstream_count` is actually fan-in (consumers), not fan-out (dependencies). Already published in `current_state_documentation.md`; renaming the field would be a breaking change to a delivered artifact — recommend a documentation clarification instead of a code change.
4. **SQL conversion core-DML extraction** is regex-based best-effort for CURSOR-bodied procedures — correctly extracts INSERT statements but doesn't reconstruct full control flow. Acceptable since these procedures are always routed to manual review, but worth strengthening if CURSOR-heavy corpora become more common in future source repos.
5. **Scalar function signature parsing** — converted SQL UDFs leave parameter list and return type as `TODO` placeholders rather than parsed from source DDL.

## Process Recommendations

- Re-run this validation script after any change to `accelerator/parsers/`, `accelerator/analyzers/`, or `accelerator/converters/` — it is the only check that exercises the full pipeline against the real source repo end-to-end rather than fixtures alone.
- Treat any new `FAIL` with `failure_category: implementation_bug` as a release blocker; `PARTIAL` results and `expected_manual_scope` failures are acceptable release states by design.
- Keep `golden_outputs/` snapshot tests as the first line of defense against silent regressions in deterministic conversion output — regenerate only via the explicit `REGENERATE_GOLDEN=1` flag, never automatically.