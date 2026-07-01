# MCP Server — SQL / SSIS / Synapse → Databricks Accelerator

## What the MCP server does

This server exposes the accelerator's full conversion pipeline as **6 MCP tools**
that any AI agent (Claude Desktop, Claude Code, or any MCP-compatible client) can
call by name. It also exposes a **resource** listing all available skill prompt
files, and a **prompt** that returns a ready-to-use pipeline invocation sequence.

The tools cover the end-to-end modernisation workflow in order:
1. **parse_source** — crawl any SQL Server / SSIS / Synapse source repo
2. **analyse_inventory** — impact analysis + architecture recommendation
3. **convert_sql** — convert tables, views, procedures, functions
4. **convert_ssis** — convert SSIS packages to Databricks Workflows and PySpark
5. **generate_bundle** — produce a Databricks Asset Bundle ready to deploy
6. **run_validation** — run the full pytest suite against all conversion outputs

The server uses **stdio transport** — it reads JSON-RPC from stdin and writes
responses to stdout. All logging goes to stderr, never stdout.

---

## Run locally

```bash
# Install dependencies
pip install -r requirements.txt

# Start the server (must be run as a plain script, not as a module —
# the folder is named "mcp", same as the SDK package; see the naming-
# collision note in server.py's module docstring)
python mcp/server.py
```

---

## Add to Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "sql-ssis-databricks-accelerator": {
      "command": "python",
      "args": ["/path/to/repo/mcp/server.py"]
    }
  }
}
```

Replace `/path/to/repo` with the absolute path to your local clone of this
repository. Restart Claude Desktop after saving.

---

## Add to Claude Code

Create or update `.claude/mcp.json` in your project root:

```json
{
  "servers": {
    "sql-ssis-databricks-accelerator": {
      "command": "python",
      "args": ["/path/to/repo/mcp/server.py"]
    }
  }
}
```

Replace `/path/to/repo` with the absolute path to your local clone. Claude
Code picks this up automatically when you open the project.

---

## Install via MCPB

```bash
mcpb install shivanandiyer/sql-ssis-databricks-accelerator
```

This fetches the server definition from `mcp/plugin.json` and `mcpb.toml` at
the repo root and wires the server up automatically for your MCP client.

---

## Tool usage examples

### `parse_source`

Parse any SQL Server / SSIS / Synapse source repository and produce an
inventory of all objects and their dependencies.

```json
{
  "tool": "parse_source",
  "arguments": {
    "source_path": "/path/to/your/ssis-sql-repo"
  }
}
```

With an explicit config file (for repos whose folder names aren't auto-detected):

```json
{
  "tool": "parse_source",
  "arguments": {
    "source_path": "/path/to/repo",
    "config_path": "/path/to/parser_config.json"
  }
}
```

`parser_config.json` format:
```json
{ "oltp_dir": "/path/to/oltp-ssdt", "dw_dir": "/path/to/dw-ssdt", "ssis_dir": "/path/to/ssis" }
```

**Returns:** `inventory_path`, `dependency_path`, `object_count`, `unsupported_count`, `summary` (counts by object type)

---

### `analyse_inventory`

Run impact analysis (12-dimension risk scoring) and produce a target-state
architecture recommendation from the parsed inventory.

```json
{
  "tool": "analyse_inventory",
  "arguments": {
    "manifest_path": "/path/to/outputs/inventory.json"
  }
}
```

With a non-default architecture:

```json
{
  "tool": "analyse_inventory",
  "arguments": {
    "manifest_path": "/path/to/outputs/inventory.json",
    "architecture_override": "lakehouse"
  }
}
```

Valid architecture values: `medallion` (default) | `lakehouse` | `lambda` | `kappa`

**Returns:** `impact_path`, `architecture`, `complexity_breakdown`, `manual_intervention_count`

---

### `convert_sql`

Convert all SQL Server / Synapse objects (tables, views, stored procedures,
functions) to Databricks SQL and/or PySpark.

```json
{
  "tool": "convert_sql",
  "arguments": {
    "manifest_path": "/path/to/outputs/inventory.json",
    "output_path": "./output"
  }
}
```

Convert only specific objects by ID:

```json
{
  "tool": "convert_sql",
  "arguments": {
    "manifest_path": "/path/to/outputs/inventory.json",
    "output_path": "./output",
    "object_filter": ["OLTP:Sales.Orders", "DW:Dimension.Customer"]
  }
}
```

**Returns:** `converted_count`, `partial_count`, `manual_count`, `output_paths`
(keys: `databricks_sql`, `pyspark`, `review_required`, `manifest`)

---

### `convert_ssis`

Convert an SSIS package's control flow, data flow, variables, and connection
managers to a Databricks Workflow spec and PySpark task modules.

```json
{
  "tool": "convert_ssis",
  "arguments": {
    "manifest_path": "/path/to/outputs/inventory.json",
    "output_path": "./output"
  }
}
```

**Returns:** `workflow_spec_path`, `bundle_path`, `task_count`, `unsupported_task_count`

---

### `generate_bundle`

Generate a Databricks Asset Bundle (DAB) job resource YAML ready to deploy
with `databricks bundle deploy`.

```json
{
  "tool": "generate_bundle",
  "arguments": {
    "manifest_path": "/path/to/outputs/inventory.json",
    "env": "dev",
    "output_path": "./bundle"
  }
}
```

Valid env values: `dev` (default) | `test` | `prod`

**Returns:** `bundle_path`, `deploy_script_path`, `environment`

---

### `run_validation`

Run the pytest suite against all conversion outputs. Scoped to a specific
area if needed.

```json
{
  "tool": "run_validation",
  "arguments": {
    "manifest_path": "/path/to/outputs/inventory.json"
  }
}
```

Scoped to just converter tests:

```json
{
  "tool": "run_validation",
  "arguments": {
    "manifest_path": "/path/to/outputs/inventory.json",
    "test_scope": "converters"
  }
}
```

Valid test_scope values: `all` (default) | `parsers` | `converters` | `deployment`

**Returns:** `passed`, `failed`, `partial`, `summary_path`, `ready_for_release`

---

## Run the full pipeline via the built-in prompt

Ask your MCP client to invoke the `run_full_pipeline` prompt with your source
path — the server returns a fully composed sequence of tool calls covering all
6 steps:

```json
{
  "prompt": "run_full_pipeline",
  "arguments": {
    "source_path": "/path/to/your/ssis-sql-repo",
    "architecture": "medallion"
  }
}
```
