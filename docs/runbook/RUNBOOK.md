# SQL Server / SSIS → Databricks Modernisation Accelerator
## Prompt Runbook

> **Purpose:** Step-by-step prompt sequence to build a Python-based modernisation accelerator
> **Target:** Converts SQL Server / Azure Synapse + SSIS solutions into Databricks assets
> **Sample corpus:** microsoft/sql-server-samples — WideWorldImporters
> **Repo:** https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/wide-world-importers
> **Audience:** Anyone reusing this accelerator in a fresh Claude Code or Copilot session

---

## How to Use This Runbook

1. Open a **fresh Claude Code session**
2. Paste each step **one at a time**, in order
3. After each step, review outputs before proceeding
4. Append the **Standard Gate Check** (below) to any step where you want Claude to pause and summarise
5. Append the **Standard Implementation Rule** to any step where you want real files, not just plans

---

## Standard Gate Check
> Append to any step to force a summary before proceeding

```
Before moving on:
1. Summarise what you completed
2. List created/updated files
3. List unresolved issues
4. Recommend whether to proceed or fix issues first
```

---

## Standard Implementation Rule
> Append to any step to ensure Claude writes real code, not just plans

```
Do not skip implementation details.
Do not give only a plan.
Create or update the actual project files.
If assumptions are required, document them explicitly.
If something cannot be fully automated, create a manual-review artifact for it.
```

---

## STEP 1 — Set the Role and Rules

> **Paste this first in every new session. This is your system prompt.**

```
You are building a reusable Python-based modernisation accelerator that converts
SQL Server / Azure Synapse + SSIS solutions into Databricks assets.

Primary objective:
1. Analyse source assets
2. Document the current state
3. Perform impact analysis
4. Propose a target-state design
5. Convert code and orchestration
6. Generate deployable Databricks assets
7. Test and validate conversion quality

Source asset types to support:
- SSIS packages (.dtsx / .ispac metadata)
- SQL Server / Synapse tables
- Views
- Materialized views
- Stored procedures
- Scalar/table-valued functions
- Triggers if present
- Schemas, constraints, indexes, keys
- SQL Agent / scheduling metadata if present
- External flat files and connection managers if referenced

Default target architecture:
- Databricks medallion architecture: Bronze, Silver, Gold
- Optional architecture override driven by user input
- Unity Catalog-aware design
- Delta Lake as default persistence layer
- Databricks Workflows for orchestration
- PySpark and/or Databricks SQL as target languages
- Optional DLT / Lakeflow / streaming patterns only when source characteristics justify them

Core behaviours:
- Never do blind conversion
- Always classify each source object first
- Always preserve lineage, dependencies, and execution order
- Always emit confidence scores, assumptions, unresolved issues, and manual remediation steps
- Always separate deterministic conversion from heuristic conversion
- Always generate machine-readable outputs and human-readable documentation

For each run, produce these outputs:
A. Inventory of source objects
B. Dependency graph
C. Current-state documentation
D. Impact/risk analysis
E. Target-state design recommendation
F. Conversion plan by object
G. Generated Databricks code
H. Deployment bundle
I. Test pack and validation report
J. Exception log for unsupported or ambiguous cases

Validation requirement:
The solution must test and validate all supported patterns, including control flow,
data flow, SQL logic, schema translation, incremental loads, SCD patterns, and
orchestration dependencies.

If I do not specify a target style, assume:
- Bronze = raw landed source-aligned tables
- Silver = cleansed/conformed business entities
- Gold  = marts, facts, dimensions, serving views

Do not generate everything at once.
Work step by step.
At the end of each step:
1. Summarise what was done
2. List files created/updated
3. List open issues
4. Wait for my next instruction
```

---

## STEP 2 — Set Up the Repo Context and Project Scaffold

```
Use this GitHub sample as the source corpus:

https://github.com/microsoft/sql-server-samples/tree/master/samples/databases/wide-world-importers

Important folders:
- wwi-ssdt     = SQL Server OLTP database project
- wwi-dw-ssdt  = SQL Server DW project
- wwi-ssis     = SSIS ETL project

The SSIS package DailyETLMain.dtsx loads WideWorldImporters into WideWorldImportersDW.

Your task now:
1. Clone or prepare this repo locally
2. Inspect the folder structure
3. Confirm the key folders exist
4. Create a Python project skeleton for the accelerator

Use this module structure:

accelerator/
  parsers/
    ssis_parser.py
    sql_project_parser.py
    tsql_parser.py
  analyzers/
    inventory_builder.py
    dependency_graph.py
    impact_analyzer.py
    architecture_recommender.py
  converters/
    ddl_converter.py
    view_converter.py
    proc_converter.py
    function_converter.py
    ssis_to_workflows.py
    ssis_to_pyspark.py
  deploy/
    bundle_generator.py
    env_config_generator.py
  docs/
    current_state_doc.py
    target_state_doc.py
    validation_doc.py
  models/
    canonical_metadata.py
    conversion_manifest.py
  tests/

Do not implement full logic yet.
Only scaffold the project and prepare the workspace.
```

---

## STEP 3 — Analyse the Source Repo

```
Now implement the source analysis layer.

Tasks:
1. Crawl all supported source files in:
   - wwi-ssdt
   - wwi-dw-ssdt
   - wwi-ssis
2. Build an inventory of:
   - schemas
   - tables
   - views
   - materialized views if present
   - stored procedures
   - functions
   - SSIS packages
   - related ETL assets
3. Detect object categories, naming patterns, and folder conventions
4. Extract dependencies between SQL objects and SSIS tasks
5. Identify source-to-target data movement paths
6. Detect ETL semantics such as:
   - full loads
   - incremental loads
   - SCD logic
   - dimension/fact loading order
   - cutoff-window logic

Outputs required:
- inventory.json
- dependencies.json
- source_summary.md
- unsupported_objects.json

Rules:
- Do not convert anything yet
- Normalise findings into a canonical metadata model
- Tag each object with source type, schema, dependency type, and conversion complexity
```

---

## STEP 4 — Document the Current State

```
Using the extracted metadata, generate current-state documentation for the
SQL Server/Synapse + SSIS solution.

Document sections:
1.  Business overview inferred from object model
2.  Source platform overview
3.  Schema inventory
4.  ETL/orchestration overview
5.  Object taxonomy:
    - tables
    - views
    - materialized views
    - stored procedures
    - functions
    - SSIS packages
6.  Dependency map
7.  Data domains
8.  Load patterns
9.  Operational assumptions
10. Technical debt / migration hotspots

Output requirements:
- Generate a concise executive summary
- Generate a technical deep dive
- Produce markdown plus machine-readable summaries
- Add confidence level per section

Outputs:
- current_state_documentation.md
- current_state_summary.json
```

---

## STEP 5 — Perform Impact Analysis

```
Perform an impact analysis for migrating this SQL Server/Synapse + SSIS solution
to Databricks.

Assess:
- SQL dialect conversion complexity
- T-SQL procedural logic complexity
- SSIS control flow conversion complexity
- SSIS data flow conversion complexity
- Dependency criticality
- Ordering constraints
- Data type mapping risks
- Performance risks
- Security / access model changes
- Operational scheduling changes
- Testing complexity
- Rollback complexity

Classify each object as:
- lift-and-shift friendly
- rewrite required
- partial automation possible
- manual redesign required

Produce:
- impact_analysis.md
- migration_risk_register.csv
- object_complexity_scores.json
- manual_intervention_list.md

Include:
- Blast radius by object
- Downstream dependency impacts
- Likely semantic drift risks
- Recommended test depth by object class
```

---

## STEP 6 — Recommend Target-State Architecture

```
Propose a target-state Databricks design for this workload.

Default assumption:
- Medallion architecture (Bronze/Silver/Gold)

But:
- If the source workload suggests a better architecture, recommend an alternative
  and explain why
- Allow architecture override from user input at runtime

Design tasks:
1. Map source OLTP and DW objects into Bronze/Silver/Gold layers
2. Separate ingestion, transformation, serving, and orchestration concerns
3. Recommend Unity Catalog structure:
   - catalog
   - schema
   - table naming conventions
4. Recommend file/layout strategy:
   - Delta tables
   - partitioning
   - liquid clustering if justified
5. Recommend orchestration mapping:
   - SSIS control flow -> Databricks Workflows tasks
6. Recommend code mapping:
   - T-SQL -> Databricks SQL and/or PySpark
7. Recommend observability:
   - audit logging
   - lineage
   - data quality checks
8. Recommend CI/CD and environment promotion strategy

Outputs:
- target_state_architecture.md
- target_state_mappings.json
- medallion_mapping.csv
- orchestration_design.md

For each recommendation:
- Explain rationale
- Explain tradeoffs
- Note assumptions
```

---

## STEP 7 — Convert SQL Objects

```
Now implement the SQL object conversion layer.

Convert these source object types into Databricks-compatible assets:
- tables
- views
- materialized views
- stored procedures
- functions

Rules:
1. Preserve semantics first, syntax second
2. Map SQL Server types to Databricks-compatible types
3. Replace unsupported procedural constructs with equivalent Databricks patterns
4. Where stored procedures are orchestration-heavy, split them into:
   - SQL transformation logic
   - workflow/task orchestration logic
5. For warehouse objects:
   - facts/dimensions map to Gold unless the architecture mapping says otherwise
6. Emit:
   - converted SQL
   - PySpark where SQL is insufficient
   - comments explaining non-trivial rewrites
   - unresolved items flagged for manual review

Output folders:
- output/databricks_sql/
- output/pyspark/
- output/review_required/

Also produce:
- conversion_manifest.json
- conversion_decisions.md
```

---

## STEP 8 — Convert SSIS Packages

```
Now implement the SSIS conversion layer.

Convert SSIS packages into Databricks orchestration and transformation assets.

Input scope:
- Package XML / DTSX structure
- Control flow
- Data flow tasks
- Variables
- Connection managers
- Expressions
- Precedence constraints
- Event handlers if present

Mapping goals:
- SSIS package              -> Databricks Workflow job
- Control flow task         -> workflow task or notebook step
- Data flow transformations -> Spark SQL / PySpark transformations
- Package variables         -> workflow parameters / notebook widgets / config objects
- Connection managers       -> secret-backed config and data source definitions

Required handling:
- Sequence containers
- Execute SQL task
- Data flow task
- Foreach loops
- Conditional branching
- Row count logic
- Flat file ingestion if present
- Error handling and restartability
- Cutoff-time / watermark logic

Deliverables:
- workflow_spec.json
- databricks_job_bundle.yml
- notebooks or python modules
- ssis_conversion_report.md
- unsupported_ssis_features.md

For every SSIS task:
- Show original metadata
- Show target mapping
- Show confidence score
- Show test recommendation
```

---

## STEP 9 — Build the Test Matrix

```
Create a comprehensive test matrix for the accelerator.

Test dimensions:
- Object type:    table, view, MV, proc, function, SSIS task, workflow
- Complexity:     low, medium, high
- Load style:     full, incremental, CDC-like window, SCD
- Source pattern: OLTP, DW, hybrid
- Target layer:   Bronze, Silver, Gold
- Conversion mode: SQL, PySpark, Workflow
- Confidence band: high, medium, low

Cover these scenarios:
1.  Pure DDL conversion
2.  View translation
3.  Stored proc with set-based SQL only
4.  Stored proc with procedural branching
5.  Function conversion
6.  Fact/dimension ETL
7.  SSIS control flow with sequencing
8.  SSIS data flow with transformations
9.  Incremental watermark logic
10. Failure recovery / rerun logic
11. Dependency ordering
12. Unsupported feature detection
13. User-driven architecture override

Outputs:
- test_matrix.csv
- test_strategy.md
- coverage_gaps.md
```

---

## STEP 10 — Generate Python Automated Tests

```
Generate Python automated tests for the accelerator.

Test categories:
- Parser tests
- Metadata extraction tests
- Dependency graph tests
- SQL conversion tests
- SSIS mapping tests
- Architecture recommendation tests
- Deployment bundle generation tests
- Regression tests for known edge cases

Testing requirements:
- Use pytest
- Include fixtures from the WideWorldImporters sample
- Snapshot test generated outputs where useful
- Validate deterministic outputs for supported objects
- Validate graceful failure for unsupported objects
- Compare lineage before and after conversion
- Assert that all source objects receive a disposition:
  converted / partial / manual

Outputs:
- tests/
- fixtures/
- golden_outputs/
- pytest.ini
- test_report_template.md
```

---

## STEP 11 — Run End-to-End Validation

```
Perform an end-to-end validation of the accelerator against the sample repository.

Validation steps:
1.  Parse source repo
2.  Extract object inventory
3.  Build dependency graph
4.  Produce documentation
5.  Produce impact analysis
6.  Recommend target architecture
7.  Convert SQL objects
8.  Convert SSIS packages
9.  Build deployment artifacts
10. Run automated tests
11. Compare outputs with expected golden results
12. Produce final validation summary

Required outputs:
- validation_summary.md
- validation_results.json
- failed_cases.json
- recommended_backlog.md

In the summary include:
- What passed
- What partially passed
- What failed
- Why it failed
- Whether failure is due to unsupported source semantics, ambiguous intent, or
  an implementation bug
- What must be fixed before accelerator release
```

---

## STEP 12 — Generate Deployment Artifacts

```
Generate deployment artifacts for Databricks.

Include:
- Folder structure
- Databricks Asset Bundle (DAB) configuration
- Environment parameterisation for dev / test / prod
- Secret references
- Cluster or serverless recommendations
- Workflow definitions
- SQL deployment scripts
- Notebook/module packaging
- Unit/integration test hooks

Outputs:
- bundle/
- conf/
- deploy/
- README.md

The deployment design must support:
- Repeatable deployment
- Object-level idempotency
- Promotion across environments
- Rollback notes per object class
```

---

## STEP 13 — Adversarial Review

```
Run an adversarial review of the accelerator design and all conversion outputs.

Look for:
- Hidden dependencies
- Dynamic SQL
- Temp tables
- Table variables
- MERGE semantics
- Cursor-like procedural logic
- Unsupported T-SQL functions
- SSIS expression language edge cases
- Variable scoping issues
- Restartability gaps
- Schema drift risks
- Naming collisions in Unity Catalog
- Mismatched medallion placement
- Warehouse objects that should remain serving-layer SQL
- Objects whose semantics are degraded by naive Spark translation

For each issue:
- Classify severity (critical / high / medium / low)
- Explain impact
- Propose mitigation
- Propose whether automation should: stop / warn / continue

Outputs:
- adversarial_review.md
- remediation_backlog.csv
```

---

## STEP 14 — Architecture Override (Optional / On Demand)

> Run this step ONLY if you want to test or apply a non-medallion architecture.

```
Override the default medallion architecture with a custom target architecture.

User-specified architecture: [REPLACE WITH YOUR CHOICE]

Examples of valid overrides:
- Data Vault 2.0 (Hubs, Satellites, Links)
- Lambda (batch + speed layer)
- Kappa (streaming-first)
- Flat Lakehouse (single curated layer, no medallion tiers)
- Hybrid (medallion Bronze/Silver + Data Vault Gold)

Tasks:
1. Re-map all source objects against the new architecture
2. Update medallion_mapping.csv with the new layer assignments
3. Update target_state_architecture.md to reflect the override
4. Update orchestration_design.md if workflow task order changes
5. Identify any objects whose conversion strategy changes under this architecture
6. Update conversion_manifest.json accordingly
7. Document tradeoffs vs default medallion design

Do not re-run conversion unless I explicitly ask for it.
Only update the design artifacts.
```

---

## Quick Reference — Output File Checklist

| Step | Key Output Files |
|------|------------------|
| 3 – Analyse | inventory.json, dependencies.json, source_summary.md, unsupported_objects.json |
| 4 – Document | current_state_documentation.md, current_state_summary.json |
| 5 – Impact | impact_analysis.md, migration_risk_register.csv, object_complexity_scores.json, manual_intervention_list.md |
| 6 – Architecture | target_state_architecture.md, target_state_mappings.json, medallion_mapping.csv, orchestration_design.md |
| 7 – SQL Convert | output/databricks_sql/, output/pyspark/, output/review_required/, conversion_manifest.json, conversion_decisions.md |
| 8 – SSIS Convert | workflow_spec.json, databricks_job_bundle.yml, ssis_conversion_report.md, unsupported_ssis_features.md |
| 9 – Test Matrix | test_matrix.csv, test_strategy.md, coverage_gaps.md |
| 10 – Tests | tests/, fixtures/, golden_outputs/, pytest.ini |
| 11 – Validate | validation_summary.md, validation_results.json, failed_cases.json, recommended_backlog.md |
| 12 – Deploy | bundle/, conf/, deploy/, README.md |
| 13 – Adversarial | adversarial_review.md, remediation_backlog.csv |

---

## Release Gate Criteria

Before calling the accelerator production-ready, all of the following must be true:

- [ ] 100% of discovered objects classified as converted, partial, or manual-review-required
- [ ] 0 silent failures in parsing
- [ ] Dependency graph generated for all supported objects
- [ ] All SSIS tasks mapped or explicitly flagged as unsupported
- [ ] Medallion placement documented for every target object
- [ ] All generated deployment artifacts build successfully
- [ ] Regression tests pass on the full WideWorldImporters sample corpus
- [ ] Validation report clearly separates implementation bugs from intentional unsupported cases
- [ ] Adversarial review completed with no unmitigated critical issues

---

## Recommended Batch Order

| Batch | Steps | Why |
|-------|-------|-----|
| A | 1 + 2 | Foundation: role + scaffold |
| B | 3 | Analysis only, no conversion yet |
| C | 4 + 5 | Documentation and impact — read-only outputs |
| D | 6 | Architecture design — review before proceeding |
| E | 7 | SQL conversion — largest output, do alone |
| F | 8 | SSIS conversion — separate concern |
| G | 9 + 10 | Test design and test code |
| H | 11 | Validation run |
| I | 12 + 13 | Deploy + adversarial hardening |

---

*Runbook version: 1.0 — June 2026*
