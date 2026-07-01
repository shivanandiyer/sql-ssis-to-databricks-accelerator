# Usage Guide — SQL / SSIS / Synapse → Databricks Accelerator

This guide covers how to run the accelerator against **any** SQL Server,
Azure Synapse, or SSIS source repository. The Wide World Importers (WWI)
sample that ships with this repo is the reference corpus used to build the
tool — your repo takes its place.

---

## Prerequisites

```bash
git clone https://github.com/shivanandiyer/sql-ssis-to-databricks-accelerator
cd sql-ssis-to-databricks-accelerator
pip install -r requirements.txt
```

Python 3.10 or later is required.

---

## Quick start — one command

```bash
python accelerator/cli.py --source-path /path/to/your/repo
```

The accelerator auto-detects your OLTP/DW/SSIS project directories,
runs all pipeline steps in order, and writes everything to `./outputs/`
(analysis) and `./output/` (converted assets).

---

## If auto-detection fails

Auto-detection finds OLTP and DW projects by scanning for `.sqlproj` files
and treating any directory whose name contains `dw` as the DW project.
SSIS is found by scanning for `.dtsx` files.

If your folder names don't match those patterns, specify the paths explicitly:

```bash
python accelerator/cli.py \
    --oltp-dir  /path/to/repo/OLTP_Project \
    --dw-dir    /path/to/repo/DataWarehouse \
    --ssis-dir  /path/to/repo/ETL_Packages
```

You can mix auto-detection and explicit paths — supply `--source-path` plus
any overrides you need:

```bash
python accelerator/cli.py \
    --source-path /path/to/repo \
    --dw-dir /path/to/repo/NonStandardDWFolder
```

---

## Custom output directories

```bash
python accelerator/cli.py \
    --source-path   /path/to/repo \
    --analysis-path /my-project/analysis \
    --conversion-path /my-project/converted \
    --bundle-path   /my-project/bundle
```

---

## Architecture override

By default the accelerator recommends and maps to a **medallion** (Bronze/Silver/Gold)
architecture. To use a different pattern:

```bash
python accelerator/cli.py --source-path /path/to/repo --architecture lakehouse
# Other options: medallion (default) | lakehouse | lambda | kappa
```

---

## Target environment

Affects the Databricks catalog name in the generated Asset Bundle:

```bash
python accelerator/cli.py --source-path /path/to/repo --env prod
# dev → <name>_dev  |  test → <name>_test  |  prod → <name>_prod
```

---

## Skip steps (resuming after partial completion)

If you've already run the analysis and just want to re-run the conversion:

```bash
python accelerator/cli.py \
    --source-path /path/to/repo \
    --skip-analysis
```

Or skip the SSIS step if your repo has no SSIS packages:

```bash
python accelerator/cli.py \
    --source-path /path/to/repo \
    --skip-ssis
```

Available skip flags: `--skip-analysis`, `--skip-sql`, `--skip-ssis`, `--skip-bundle`

---

## Running steps individually

Each pipeline step is also a standalone script with its own `--help`:

```bash
# Step 1: Parse source repo and build inventory
python run_analysis.py --source-path /path/to/repo --output-path ./outputs

# Step 2: Impact analysis and risk scoring
python run_impact_analysis.py --input-path ./outputs

# Step 3: Target-state architecture and medallion mapping
python run_target_state_design.py --input-path ./outputs
python run_target_state_design.py --input-path ./outputs --architecture lakehouse

# Step 4: Convert SQL objects (tables, views, procedures, functions)
python run_conversion.py --input-path ./outputs --output-path ./output

# Step 5: Convert SSIS packages to Databricks Workflows + PySpark
python run_ssis_conversion.py --input-path ./outputs --output-path ./output

# Step 6: Generate Databricks Asset Bundle
python deploy/generate_deployment_bundle.py \
    --input-path ./output \
    --output-path ./bundle \
    --env dev
```

---

## Understanding the outputs

### Analysis outputs (`./outputs/` by default)

| File | What it contains |
|------|-----------------|
| `inventory.json` | Every SQL/SSIS object found: type, schema, name, dependencies, complexity band |
| `unsupported_objects.json` | Objects the parser couldn't classify (security scripts, unsupported DDL) |
| `dependencies.json` | Directed dependency graph with topological order and cycle detection |
| `current_state_documentation.md` | Human-readable inventory summary |
| `impact_analysis.md` | 12-dimension risk assessment for each object |
| `object_complexity_scores.json` | Per-object complexity score and classification |
| `medallion_mapping.csv` | Source object → target Unity Catalog FQN mapping |
| `manual_intervention_list.md` | Objects requiring manual work before deployment |

### Conversion outputs (`./output/` by default)

| Path | What it contains |
|------|-----------------|
| `databricks_sql/` | Databricks SQL DDL for tables, views, functions |
| `pyspark/` | PySpark modules for procedures and orchestration logic |
| `review_required/` | One `.md` per object that needs manual review before deployment |
| `conversion_manifest.json` | Machine-readable record of every object's conversion outcome |
| `conversion_decisions.md` | Human-readable rationale for type mappings and conversion choices |
| `workflow_spec.json` | Databricks Workflow job spec (produced by SSIS conversion) |

### Bundle outputs (`./bundle/` by default)

| Path | What it contains |
|------|-----------------|
| `resources/*.job.yml` | Databricks Asset Bundle job resource YAML |

---

## What needs manual review

The accelerator produces a `review_required/` directory containing one Markdown
file per object it couldn't fully convert automatically. Common causes:

| Construct | Why it needs review |
|-----------|---------------------|
| `CURSOR` / `WHILE` loops | Procedural row-by-row logic — rewrite as set-based DataFrame operation |
| `FOR JSON` / `FOR XML` | No direct Spark SQL equivalent |
| `geography` / `geometry` columns | No native geospatial type in Databricks SQL |
| `EXEC` / dynamic SQL | Rewrite as parameterised PySpark string templating |
| Temporal tables (`SYSTEM_TIME`) | Rewrite using Delta time-travel or SCD Type 2 |
| Linked server references | Replace with Unity Catalog cross-catalog queries or External Location |
| `OPENROWSET` | Replace with Databricks External Table or COPY INTO |

For each item in `review_required/`, the `.md` file includes:
- Why the object was flagged
- The original source DDL
- A suggested approach

---

## Deploying the converted assets

### Configure your workspace

Edit `conf/dev.yml` with your Databricks workspace details:

```yaml
workspace:
  host: https://your-workspace.azuredatabricks.net
catalog: your_project_dev
cluster_id: your-cluster-id
sql_warehouse_id: your-warehouse-id
alert_email: your-team@example.com
```

Store credentials in Databricks Secrets (see `conf/secrets.md`).

### Deploy

```bash
# Validate the bundle first
databricks bundle validate --target dev

# Deploy to dev
databricks bundle deploy --target dev

# Promote to test
bash deploy/promote.sh dev test

# Promote to prod
bash deploy/promote.sh test prod
```

### Rollback

See `deploy/rollback.md` for step-by-step rollback instructions per environment.

---

## Using the MCP server

The accelerator exposes all pipeline steps as MCP tools for use with Claude
Desktop, Claude Code, or any MCP-compatible agent.

```bash
python mcp/server.py
```

See `mcp/README.md` for configuration snippets and tool usage examples.

---

## Repo-specific naming collisions

If two objects across your OLTP and DW projects share the same `schema.name`
(e.g., both have a `dbo.Config` table), the medallion mapping will raise an
error before writing any output. Fix by editing `outputs/medallion_mapping.csv`
to give each object a unique `target_fqn` before re-running `run_conversion.py`.

---

## Running the test suite

```bash
pytest tests/ -v
```

The test suite runs against the bundled fixture files (not your source repo),
so it works without any external dependencies. Tests that check real pipeline
outputs auto-skip when `outputs/` hasn't been populated.

---

## Getting help

- **Skills prompts**: `skills/00_overview.md` through `skills/14_architecture_override.md` —
  paste any of these directly into Claude Code to continue or extend the pipeline.
- **Runbook**: `docs/runbook/RUNBOOK.md` — the 14-step prompt sequence used to build
  this entire accelerator, reusable on a fresh repo.
- **Issues**: https://github.com/shivanandiyer/sql-ssis-to-databricks-accelerator/issues
