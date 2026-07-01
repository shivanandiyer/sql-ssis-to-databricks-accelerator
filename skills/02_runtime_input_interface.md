<!-- Step 2: Runtime Input Interface — paste this prompt directly into Claude Code -->

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

Note for reuse against a different source repo: replace the GitHub URL and the
three folder names above (OLTP project / DW project / SSIS project) with the
equivalent paths in your own source repository before pasting this prompt. The
accelerator itself takes the source location as input — this step only
establishes which local paths to point it at and prepares the workspace.
