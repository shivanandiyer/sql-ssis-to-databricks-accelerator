# SQL / SSIS / Synapse → Databricks Modernisation Accelerator

## What this project is
A reusable Python accelerator that converts any SQL Server / Azure Synapse + SSIS
codebase into Databricks assets. Input is any source repo supplied via --source-path.

## How this repo is organised

| Folder        | Purpose                                                |
|---------------|--------------------------------------------------------|
| accelerator/  | Core Python pipeline: parsers, analyzers, converters   |
| mcp/          | MCP server exposing accelerator tools to AI agents     |
| skills/       | Step-by-step prompt guides for each pipeline stage     |
| bundle/       | Generated Databricks Asset Bundle output               |
| output/       | All generated conversion artefacts                     |
| outputs/      | All generated analysis artefacts                       |
| tests/        | Pytest suite                                           |
| deploy/       | Deployment scripts                                     |
| conf/         | Environment configs (dev/test/prod)                    |
| docs/         | Usage guide, runbook, deployment docs                  |

## How to run the full pipeline (single command)

```bash
python accelerator/cli.py --source-path /path/to/any/ssis-sql-repo
```

All outputs default to `./outputs/` (analysis) and `./output/` (converted assets).

## How to run individual steps

```bash
python run_analysis.py        --source-path /path/to/repo
python run_impact_analysis.py --input-path ./outputs
python run_target_state_design.py --input-path ./outputs
python run_conversion.py      --input-path ./outputs --output-path ./output
python run_ssis_conversion.py --input-path ./outputs --output-path ./output
python deploy/generate_deployment_bundle.py --input-path ./output --env dev
```

## How to run the MCP server

```bash
python mcp/server.py
```

## Pipeline stages

1. Parse source assets        → accelerator/parsers/
2. Analyse and classify       → accelerator/analyzers/
3. Convert SQL objects        → accelerator/converters/sql_converter.py
4. Convert SSIS packages      → accelerator/converters/ssis_converter.py
5. Generate documentation     → accelerator/docs/
6. Generate deployment bundle → deploy/generate_deployment_bundle.py
7. Validate outputs           → tests/

## Skills (prompt guides)

skills/00_overview.md through skills/14_architecture_override.md
Use these as Claude Code prompts when building or extending any stage.

## Rules for Claude when working in this repo

- Never modify output/ or bundle/ directly — these are generated artefacts
- Always update conversion_manifest.json when changing converter behaviour
- Always run pytest after modifying any file in accelerator/ or mcp/
- Treat output/review_required/ items as manual — do not attempt to auto-fix them
- Never hard-code source paths — always read from CLI args or config
- When in doubt about a conversion decision, write it to conversion_decisions.md

## Architecture default

Medallion: Bronze / Silver / Gold
Override via --architecture flag: medallion | lakehouse | lambda | kappa
