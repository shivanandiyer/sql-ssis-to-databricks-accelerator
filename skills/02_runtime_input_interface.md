<!-- Step 2: Runtime Input Interface — paste this prompt directly into Claude Code -->

<!--
  ╔══════════════════════════════════════════════════════════════════╗
  ║  FILL IN YOUR SOURCE REPO DETAILS BELOW BEFORE PASTING          ║
  ║  Then delete this comment block and paste into Claude Code.      ║
  ╚══════════════════════════════════════════════════════════════════╝

  Repo URL or local path:
    The GitHub/Azure DevOps URL or local filesystem path of the source repo
    containing your SQL Server / Synapse / SSIS codebase.
    Example: https://github.com/your-org/your-repo
    Example: /Users/you/projects/my-sql-repo

  OLTP dir:
    The folder containing your main transactional SQL Server database project.
    This is where the .sqlproj file and the .sql object files (tables, views,
    procedures, functions) live. The accelerator scans this recursively.
    — If you have only one database project (no separate DW), point this at it
      and leave DW dir blank. Everything will be classified using schema/name
      heuristics alone.
    — If you have no .sqlproj (just a folder of .sql files), point here anyway
      — the parser falls back to scanning .sql files directly.
    Example: Database/MyApp.Database
    Example: src/sql/oltp

  DW dir (optional — leave blank if you have only one database project):
    The folder containing a separate data warehouse database project (.sqlproj).
    Only set this if you have a distinct DW project alongside your OLTP project.
    Objects in this project are treated as analytics-oriented and mapped to
    Silver/Gold by default (vs OLTP objects which default to Bronze).
    — Leave blank if your source has a single database project.
    — If you have two projects but neither is formally a "DW", point this at
      the reporting/analytics-oriented one — layer assignment still works via
      schema and naming heuristics (Dimension.*, Fact.*, Integration.*, etc.)
    Example: DataWarehouse/MyApp.DW
    Example: src/sql/dw

  SSIS dir (optional — leave blank if no SSIS packages):
    The folder containing your SSIS ETL project (.dtsx package files and
    .conmgr connection manager files). Leave blank if your ETL is implemented
    in something other than SSIS (SQL Agent jobs, ADF pipelines, etc.).
    Example: ETL/MyApp.SSIS
    Example: src/ssis
-->

## Source repo config

Repo URL or local path : <YOUR_REPO_URL_OR_PATH>

OLTP dir  : <YOUR_OLTP_DIR>    <!-- folder with .sqlproj / .sql files for your transactional DB -->
DW dir    : <YOUR_DW_DIR>      <!-- folder with .sqlproj for your DW project — leave blank if none -->
SSIS dir  : <YOUR_SSIS_DIR>    <!-- folder with .dtsx files — leave blank if no SSIS -->

---

Your task now:
1. Clone or prepare the source repo at the path above locally
2. Inspect the folder structure under each configured directory
3. Confirm the key folders exist and note what's in them
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

When reporting back, confirm:
- Which directories were found and what they contain
- Whether a .sqlproj was found in OLTP dir and DW dir (or if the parser will
  fall back to raw .sql scanning)
- Whether any SSIS .dtsx files were found in SSIS dir
- Any unexpected folder structures worth noting before the next step
