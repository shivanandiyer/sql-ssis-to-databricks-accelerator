# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Nothing yet — add entries here as PRs land, under Added/Changed/Fixed as
appropriate (see [0.1.0] below for the expected level of detail).

## [0.1.0] - 2026-06-30

Initial public release.

### Added

- **Parsers**: SSDT `.sqlproj` SQL file classifier (`accelerator/parsers/sql_project_parser.py`)
  covering tables, views, materialized-view detection, stored procedures,
  scalar/inline/multi-statement functions, sequences, user-defined types,
  triggers, indexes, and security objects; SSIS `.dtsx`/`.conmgr` parser
  (`accelerator/parsers/ssis_parser.py`) covering packages, sequence
  containers, Execute SQL tasks, Data Flow tasks, expressions, precedence
  constraints, connection managers, and variables.
- **Inventory & dependency graph**: canonical metadata model with medallion
  layer/risk/confidence assignment (`accelerator/analyzers/inventory_builder.py`);
  dependency DAG construction, topological sort, and cycle detection
  (`accelerator/analyzers/dependency_graph.py`).
- **Current-state documentation generator**: executive summary, technical
  deep dive, schema inventory, object taxonomy, dependency map, data
  domains, load patterns, operational assumptions, and technical debt
  sections with per-section confidence ratings
  (`accelerator/docs/current_state_doc.py`).
- **Impact analysis**: 12-dimension risk scoring (SQL dialect, procedural
  logic, SSIS control/data flow, dependency criticality, ordering
  constraints, data type risk, performance risk, security risk, operational
  scheduling, testing complexity, rollback complexity) with lift-and-shift /
  partial-automation / rewrite-required / manual-redesign classification
  and blast-radius analysis (`accelerator/analyzers/impact_analysis.py`).
- **Target-state architecture design**: medallion-vs-Data-Vault-vs-One-Big-
  Table evaluation with a documented default and a supported override
  mechanism; Unity Catalog catalog/schema/naming design; Delta file-layout
  recommendations (partitioning/clustering); SSIS-to-Workflows orchestration
  mapping; T-SQL-to-Databricks-SQL/PySpark code mapping; observability and
  CI/CD recommendations (`accelerator/docs/target_state_design.py`).
- **SQL object conversion**: tables, views, functions, and procedures
  converted to Databricks SQL or PySpark with explicit type mapping (SQL
  Server → Delta/Spark types, including geography/hierarchyid/sql_variant
  gap flagging), procedural-construct detection (CURSOR, dynamic SQL,
  OPENJSON, temp tables, table variables, MERGE-against-non-persistent-
  targets), and an orchestration/transformation-logic split for
  ETL-orchestration-heavy procedures (`accelerator/converters/sql_converter.py`).
- **SSIS conversion**: SSIS package converted to a Databricks Workflow job
  spec, Asset Bundle YAML, and per-task Python/SQL modules, with connection
  manager → secret-scope mapping, variable → watermark-table/job-parameter
  mapping, shared-mutable-variable scoping hazard detection, and per-task
  confidence scores and test recommendations
  (`accelerator/converters/ssis_converter.py`).
- **Test matrix and automated test suite**: scenario-driven test matrix
  covering 13 required migration scenarios across object type, complexity,
  load style, source pattern, target layer, conversion mode, and confidence
  band (`accelerator/docs/test_matrix.py`); a 117-test pytest suite covering
  parsers, metadata extraction, dependency graph, SQL conversion, SSIS
  mapping, architecture recommendation, deployment bundle generation, and
  regression tests for previously-found bugs, with golden-snapshot testing
  for deterministic conversion output (`tests/`).
- **Deployment artifacts**: Databricks Asset Bundle (`bundle/`) generated
  from the real conversion output (never hand-transcribed); per-environment
  configuration (`conf/`); deploy/promote/rollback tooling (`deploy/`)
  including an idempotent, dependency-ordered SQL DDL deployment script and
  a post-deploy smoke test.
- **End-to-end validation**: a 12-step validation script
  (`run_validation.py`) that re-runs the full pipeline against the real
  source repo, runs the test suite, diffs golden snapshots, and classifies
  any failure as unsupported-source-semantics / ambiguous-intent /
  implementation-bug / expected-manual-scope.
- **Adversarial self-review**: a structured review (`docs/example-run/adversarial_review.md`)
  covering hidden dependencies, dynamic SQL, temp tables, MERGE semantics,
  cursor-like procedural logic, unsupported T-SQL functions, SSIS
  expression edge cases, variable scoping, restartability, schema drift,
  Unity Catalog naming collisions, medallion placement, and naive-
  translation risks — with 12 of 15 findings fixed in code and verified by
  re-running the full pipeline.
- Worked example output of a full run against the public
  [Wide World Importers](https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/wide-world-importers)
  sample corpus, included under `docs/example-run/`.

### Fixed

(All found during development via the test suite and adversarial review,
fixed before this initial release — see `docs/example-run/remediation_backlog.csv`
for full detail.)

- `OPENJSON` usage was undetected by any complexity/risk pattern, causing 38
  affected procedures to convert to empty, falsely "safe" output files.
- Temp-table detection regex (`\b#\w+\b`) could never match due to an
  incorrect word-boundary assertion against the non-word `#` character —
  present independently in both the parser and the impact-analysis scorer.
- `topological_sort()` returned dependants before their dependencies,
  contradicting its own "safe deployment order" contract.
- `EXECUTE AS OWNER` double-matched two overlapping security-risk patterns,
  inflating ~113 routine procedures to a false "manual redesign" severity.
- Function name/schema extraction broke for refined function subtypes
  (`TVF_INLINE`, `TVF_MULTI`, `SCALAR_FUNCTION`), corrupting 3 object names.
- A multi-statement, branching scalar function was wrongly treated as a
  trivial single-expression function, which would have produced a broken
  SQL UDF silently discarding its business logic.
- `FOR SYSTEM_TIME AS OF` was incorrectly documented as equivalent to Delta
  `TIMESTAMP AS OF` — these have different semantics (per-row validity
  window vs. whole-table commit snapshot); the design documentation and
  generated warnings now state the correct rewrite pattern.
- SSIS Workflow task definitions could reference converted-SQL files that
  were never actually generated for inline-SQL (non-EXEC) Execute SQL
  tasks, which would have failed at job-run time.

### Known limitations

See the README's "Known Limitations" section and
`docs/example-run/adversarial_review.md` for full detail. Headline items:
materialized views, SSIS Foreach Loops, flat-file connections, event
handlers, and dynamic SQL have documented mapping rules but no validated
instance in the bundled sample corpus; procedural DML extraction is regex-
based, not a full T-SQL parser.

[0.1.0]: https://github.com/<org>/sql-ssis-to-databricks-accelerator/releases/tag/v0.1.0
