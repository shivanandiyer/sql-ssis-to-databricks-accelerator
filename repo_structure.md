# Repository Structure

Complete file tree of the SQL / SSIS / Synapse → Databricks Modernisation Accelerator.
Generated: 2026-07-01. Excludes `.git/`, `.mypy_cache/`, `.ruff_cache/`, `.pytest_cache/`,
`__pycache__/`, `*.pyc`, and generated output directories (`outputs/`, `output/`,
`bundle/`, `golden_outputs/`, `docs/example-run/`).

---

## Root

```
.
├── CHANGELOG.md              Release history with version, date, and summary of changes
├── CLAUDE.md                 Project guide for Claude Code — layout, run commands, rules
├── CONTRIBUTING.md           Contribution guide — how to fork, branch, test, and PR
├── LICENSE                   MIT licence
├── README.md                 Public-facing project overview, quickstart, and feature list
├── mcpb.toml                 MCPB registry config — entry point, transport, includes/excludes
├── pyproject.toml            Build metadata, extras (dev / deploy / mcp), ruff / mypy config
├── pytest.ini                Pytest settings — testpaths, asyncio_mode, log_cli
├── requirements.txt          Full dependency list for MCP server, pipeline, and test suite
│
├── run_analysis.py           CLI step 1 — parse source SQL/SSIS and build inventory.json
├── run_impact_analysis.py    CLI step 2 — impact analysis, complexity scoring, risk register
├── run_target_state_design.py CLI step 3 — architecture recommendation and medallion mapping
├── run_conversion.py         CLI step 4 — SQL object conversion (tables/views/procs/functions)
├── run_ssis_conversion.py    CLI step 5 — SSIS conversion to Databricks Workflows + PySpark
├── run_test_matrix.py        CLI step 6 — generate test matrix, coverage gaps, test strategy
└── run_validation.py         CLI step 7 — end-to-end validation with pass/fail summary
```

---

## accelerator/ — Core Python pipeline

```
accelerator/
├── __init__.py
│
├── parsers/
│   ├── __init__.py
│   ├── sql_project_parser.py   Walks .sqlproj dirs; classifies every .sql file by object type
│   └── ssis_parser.py          Parses .dtsx and .conmgr files into task/connection catalogs
│
├── analyzers/
│   ├── __init__.py
│   ├── inventory_builder.py    Merges SQL and SSIS objects into a canonical inventory.json
│   ├── dependency_graph.py     Builds directed graph, detects cycles, topological-sorts objects
│   └── impact_analysis.py      12-dimension risk scoring; outputs complexity_scores.json
│
├── converters/
│   ├── __init__.py
│   ├── sql_converter.py        Converts TABLE/VIEW/PROCEDURE/FUNCTION to Databricks SQL/PySpark
│   └── ssis_converter.py       Converts SSIS control/data flow to workflow_spec.json + PySpark
│
└── docs/
    ├── __init__.py
    ├── current_state_doc.py    Generates source_summary.md and unsupported_objects.md
    ├── target_state_design.py  Decides architecture, builds medallion mapping CSV
    └── test_matrix.py          Generates test_matrix.csv, test_strategy.md, coverage_gaps.md
```

---

## mcp/ — MCP server (AI agent interface)

```
mcp/
├── server.py         Low-level MCP Server API: 6 tools, 1 resource, 1 prompt; stdio transport
├── plugin.json       MCPB registry manifest — tool list, resources, prompts, install instructions
├── README.md         How to run locally, add to Claude Desktop / Claude Code, install via MCPB
│
└── tools/
    ├── __init__.py
    ├── parse_source.py       handle_parse_source — auto-detect or config-driven source parsing
    ├── analyse_inventory.py  handle_analyse_inventory — impact analysis + architecture design
    ├── convert_sql.py        handle_convert_sql — SQL object conversion with medallion targets
    ├── convert_ssis.py       handle_convert_ssis — SSIS-to-Workflow conversion
    ├── generate_bundle.py    handle_generate_bundle — Databricks Asset Bundle YAML generation
    └── run_validation.py     handle_run_validation — pytest runner with scope filtering
```

---

## skills/ — Step-by-step prompt guides (paste into Claude Code)

```
skills/
├── 00_overview.md                Master system prompt: role, rules, output list, medallion defaults
├── 01_set_role_and_rules.md      Identical master prompt — paste first in every new Claude session
├── 02_runtime_input_interface.md Point the accelerator at a source repo; scaffold the workspace
├── 03_implement_parsers.md       Crawl SQL/SSIS source files; build inventory and dependency graph
├── 04_implement_analyzers.md     Impact analysis: complexity scoring, risk, blast radius
├── 05_convert_sql_objects.md     Convert tables/views/procedures/functions to Databricks
├── 06_convert_ssis_packages.md   Convert SSIS control flow/data flow to Workflows and PySpark
├── 07_documentation_generators.md Current-state docs and target-state architecture design
├── 08_deployment_generator.md    Databricks Asset Bundle, env config, deploy tooling
├── 09_test_matrix_and_fixtures.md Scenario-driven test matrix covering all migration patterns
├── 10_automated_tests.md         pytest suite, fixtures, and golden-output snapshots
├── 11_end_to_end_validation.md   Full pipeline run against the sample repo; validate outputs
├── 12_adversarial_review.md      Hunt for hidden dependencies, naive-translation risks, scope gaps
├── 13_github_push.md             git init, gh repo create, push, tag, create release
└── 14_architecture_override.md   Optional: re-map the design to a non-medallion architecture
```

---

## tests/ — Pytest suite

```
tests/
├── conftest.py                    Shared fixtures: paths, SQL/SSIS fixture paths, synthetic inventories
├── test_parsers.py                SQL project parser: object type classification, deduplication, counts
├── test_metadata_extraction.py    Metadata fields: schema, name, features, ETL semantics, medallion layer
├── test_dependency_graph.py       Graph construction, cycle detection, topological sort, ETL lineage
├── test_architecture_recommendation.py  Architecture decision logic and medallion target mapping
├── test_sql_conversion.py         SQL converter: table DDL, view, procedure, function, golden snapshots
├── test_ssis_mapping.py           SSIS converter: task catalog, workflow spec, job bundle YAML
├── test_deployment_bundle.py      Deployment bundle: env substitution, job YAML structure
├── test_regression_edge_cases.py  Edge cases: cursors, FOR JSON, geography/temporal, cycles
├── test_mcp_server.py             MCP server: tool/resource/prompt registration (requires mcp SDK ≥3.10)
└── test_mcp_tools.py              MCP tool handlers: happy paths, bad-input error dict, 6 tools × N cases
```

---

## fixtures/ — Test fixture files (real WWI excerpts)

```
fixtures/
├── sql/
│   ├── cursor_procedure.sql          Integration.GetCityUpdates — CURSOR/WHILE change detection
│   ├── forjson_view.sql              WebApi.Cities — FOR JSON view (no Spark SQL equivalent)
│   ├── geography_temporal_table.sql  Application.Cities — geography + temporal system-versioning
│   ├── scalar_function.sql           Website.CalculateCustomerPrice — multi-statement scalar UDF
│   ├── set_based_procedure.sql       Integration.MigrateStagedCityData — MERGE/INSERT procedure
│   └── simple_table_lift_and_shift.sql  DataLoadSimulation.FicticiousNamePool — plain lookup table
│
└── ssis/
    ├── minimal_package.dtsx          Real "Load City Dimension" sequence container in minimal envelope
    ├── WWI_Source_DB.conmgr          Source SQL Server connection manager
    └── WWI_DW_Destination_DB.conmgr  DW destination connection manager
```

---

## deploy/ — Deployment scripts

```
deploy/
├── generate_deployment_bundle.py  Renders workflow_spec.json → Databricks job resource YAML
├── deploy.sh                      Shell wrapper for `databricks bundle deploy`
├── promote.sh                     Promotes a bundle from dev → test → prod
├── validate_deployment.py         Post-deploy smoke tests against the Unity Catalog
├── sql_deploy.py                  Applies Databricks SQL DDL files in topological order
└── rollback.md                    Manual rollback runbook with per-step instructions
```

---

## conf/ — Environment configuration

```
conf/
├── dev.yml      Databricks workspace, catalog, and cluster config for the dev environment
├── test.yml     Config for the test (UAT) environment
├── prod.yml     Config for the production environment
└── secrets.md   Instructions for storing tokens in Databricks Secrets or CI variables
```

---

## docs/ — Documentation and runbook

```
docs/
├── DEPLOYMENT.md          Production deployment guide: prerequisites, steps, rollback
└── runbook/
    └── RUNBOOK.md         The 14-step prompt sequence used to build this accelerator from scratch
```

---

## .github/ — CI/CD workflows and issue templates

```
.github/
├── PULL_REQUEST_TEMPLATE.md
├── ISSUE_TEMPLATE/
│   ├── bug_report.md
│   ├── feature_request.md
│   └── unsupported_object_type.md
└── workflows/
    ├── ci.yml              Matrix CI (Python 3.10/3.11/3.12) — lint, type-check, pytest
    ├── release.yml         test → build → publish to PyPI → create GitHub release
    └── validate-sample.yml Weekly + on-push sparse-clone of microsoft/sql-server-samples and parse
```

---

## Generated directories (not committed, in .gitignore)

| Directory        | Contents |
|-----------------|---------|
| `outputs/`      | Pipeline stage 1–3 outputs: inventory.json, dependencies.json, impact analysis, medallion mapping |
| `output/`       | Pipeline stage 4–5 outputs: databricks_sql/, pyspark/, review_required/, workflow_spec.json |
| `bundle/`       | Generated Databricks Asset Bundle YAML ready for `databricks bundle deploy` |
| `golden_outputs/` | Golden snapshot SQL files used by test_sql_conversion.py snapshot assertions |
| `docs/example-run/` | Example pipeline run outputs for documentation purposes |
