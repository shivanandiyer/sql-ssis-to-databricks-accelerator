<!-- Step 6: Convert SSIS Packages — paste this prompt directly into Claude Code -->

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
