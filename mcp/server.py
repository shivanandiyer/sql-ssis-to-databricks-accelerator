"""
mcp/server.py
MCP server entry point exposing the SQL/SSIS/Synapse -> Databricks
modernisation accelerator as tools, a resource, and a prompt for AI agents.

Built on the official Python MCP SDK (pip package: mcp), using its low-level
Server API (mcp.server.Server, @server.call_tool() etc.) rather than the
high-level FastMCP wrapper, so tool dispatch is explicit in one place.

Run:
    cd mcp && python server.py

IMPORTANT — this folder deliberately has no __init__.py. This directory is
named "mcp", the same name as the third-party SDK package this file imports
(`from mcp.server import Server`). If this directory were turned into an
importable package (via __init__.py) and the repo root ever ended up on
sys.path (e.g. via `python -m mcp.server` run from the repo root, or an
editable install), Python's import resolution would find *this* local folder
before the real site-packages `mcp` SDK, shadowing it and breaking the very
import this file depends on. Running this file as a plain script
(`python server.py` from inside mcp/, or `python mcp/server.py` from the
repo root) avoids the collision because the script's own directory is what
gets added to sys.path, not the repo root — keep it that way. mcp/tools/ has
the same constraint and is likewise not added to sys.path except via the
explicit relative import below.

All logging in this file and in mcp/tools/*.py goes to stderr (via
logging.basicConfig(stream=sys.stderr, ...)), never to stdout — stdio
transport reserves stdout exclusively for JSON-RPC protocol messages, so a
stray print() or stdout log handler would corrupt every client connected to
this server.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    GetPromptResult,
    Prompt,
    PromptArgument,
    PromptMessage,
    Resource,
    TextContent,
    Tool,
)

sys.path.insert(0, str(Path(__file__).resolve().parent))  # make mcp/tools importable as a top-level package

from tools.analyse_inventory import handle_analyse_inventory
from tools.convert_sql import handle_convert_sql
from tools.convert_ssis import handle_convert_ssis
from tools.generate_bundle import handle_generate_bundle
from tools.parse_source import handle_parse_source
from tools.run_validation import handle_run_validation

logging.basicConfig(
    stream=sys.stderr,
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

SERVER_NAME = "sql-ssis-databricks-accelerator"
SERVER_VERSION = "1.0.0"
SERVER_DESCRIPTION = "Modernisation accelerator tools for SQL Server / SSIS / Synapse to Databricks"

server = Server(SERVER_NAME, version=SERVER_VERSION, instructions=SERVER_DESCRIPTION)


# ---------------------------------------------------------------------------
# Tool definitions (schema) and dispatch table
# ---------------------------------------------------------------------------

_TOOLS: list[Tool] = [
    Tool(
        name="parse_source",
        description="Parse a source repository and extract all SQL/SSIS objects",
        inputSchema={
            "type": "object",
            "properties": {
                "source_path": {"type": "string", "description": "Path to the source repository to parse"},
                "config_path": {"type": "string", "description": "Optional path to a parser config JSON file"},
            },
            "required": ["source_path"],
        },
    ),
    Tool(
        name="analyse_inventory",
        description="Run impact analysis and architecture recommendation on parsed inventory",
        inputSchema={
            "type": "object",
            "properties": {
                "manifest_path": {"type": "string", "description": "Path to inventory.json from parse_source"},
                "architecture_override": {
                    "type": "string",
                    "enum": ["medallion", "lakehouse", "lambda", "kappa"],
                    "description": "Optional target architecture override",
                },
            },
            "required": ["manifest_path"],
        },
    ),
    Tool(
        name="convert_sql",
        description="Convert SQL Server / Synapse objects to Databricks SQL and PySpark",
        inputSchema={
            "type": "object",
            "properties": {
                "manifest_path": {"type": "string", "description": "Path to inventory.json from parse_source"},
                "output_path": {"type": "string", "description": "Output directory (default ./output)"},
                "object_filter": {
                    "type": "array", "items": {"type": "string"},
                    "description": "Optional list of object ids to restrict conversion to",
                },
            },
            "required": ["manifest_path"],
        },
    ),
    Tool(
        name="convert_ssis",
        description="Convert SSIS packages to Databricks Workflows and PySpark notebooks",
        inputSchema={
            "type": "object",
            "properties": {
                "manifest_path": {"type": "string", "description": "Path to inventory.json from parse_source"},
                "output_path": {"type": "string", "description": "Output directory (default ./output)"},
            },
            "required": ["manifest_path"],
        },
    ),
    Tool(
        name="generate_bundle",
        description="Generate a Databricks Asset Bundle for deployment",
        inputSchema={
            "type": "object",
            "properties": {
                "manifest_path": {"type": "string", "description": "Path to inventory.json from parse_source"},
                "env": {"type": "string", "enum": ["dev", "test", "prod"], "description": "Target environment (default dev)"},
                "output_path": {"type": "string", "description": "Output directory (default ./bundle)"},
            },
            "required": ["manifest_path"],
        },
    ),
    Tool(
        name="run_validation",
        description="Run end-to-end validation of all conversion outputs",
        inputSchema={
            "type": "object",
            "properties": {
                "manifest_path": {"type": "string", "description": "Path to inventory.json from parse_source"},
                "test_scope": {
                    "type": "string",
                    "enum": ["all", "parsers", "converters", "deployment"],
                    "description": "Which tests to run (default all)",
                },
            },
            "required": ["manifest_path"],
        },
    ),
]

_TOOL_HANDLERS = {
    "parse_source": handle_parse_source,
    "analyse_inventory": handle_analyse_inventory,
    "convert_sql": handle_convert_sql,
    "convert_ssis": handle_convert_ssis,
    "generate_bundle": handle_generate_bundle,
    "run_validation": handle_run_validation,
}


@server.list_tools()
async def list_tools() -> list[Tool]:
    return _TOOLS


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    logger.info("call_tool name=%s arguments=%s", name, json.dumps(arguments, default=str))
    handler = _TOOL_HANDLERS.get(name)
    if handler is None:
        result: dict[str, Any] = {"error": True, "message": f"Unknown tool: {name}"}
    else:
        # Handlers already catch their own exceptions and return
        # {error: True, message: str} — this except is a last-resort
        # safety net so a bug in a handler still can't crash the server.
        try:
            result = await handler(**arguments)
        except Exception as exc:  # noqa: BLE001
            logger.exception("unhandled exception calling tool %s", name)
            result = {"error": True, "message": f"unhandled exception in {name}: {exc}"}
    return [TextContent(type="text", text=json.dumps(result, indent=2, default=str))]


# ---------------------------------------------------------------------------
# Resources
# ---------------------------------------------------------------------------

# Maps each skills/ file to its step number and a short description, kept here
# rather than parsed from disk so the resource has stable output even if a
# skill file's prose changes — update this table when skills/ files change.
_SKILLS_CATALOG: list[dict[str, Any]] = [
    {"filename": "00_overview.md", "step_number": 0, "title": "Overview",
     "description": "Master system prompt: role, rules, output list A-J, medallion defaults."},
    {"filename": "01_set_role_and_rules.md", "step_number": 1, "title": "Set Role and Rules",
     "description": "The same master system prompt, paste first in every new session."},
    {"filename": "02_runtime_input_interface.md", "step_number": 2, "title": "Runtime Input Interface",
     "description": "Point the accelerator at a source repo and scaffold the project workspace."},
    {"filename": "03_implement_parsers.md", "step_number": 3, "title": "Implement Parsers",
     "description": "Crawl source SQL/SSIS files, build the inventory and dependency graph."},
    {"filename": "04_implement_analyzers.md", "step_number": 4, "title": "Implement Analyzers",
     "description": "Run impact analysis: complexity scoring, risk classification, blast radius."},
    {"filename": "05_convert_sql_objects.md", "step_number": 5, "title": "Convert SQL Objects",
     "description": "Convert tables/views/procedures/functions to Databricks SQL or PySpark."},
    {"filename": "06_convert_ssis_packages.md", "step_number": 6, "title": "Convert SSIS Packages",
     "description": "Convert SSIS control flow/data flow to Databricks Workflows and PySpark."},
    {"filename": "07_documentation_generators.md", "step_number": 7, "title": "Documentation Generators",
     "description": "Generate current-state documentation and target-state architecture design."},
    {"filename": "08_deployment_generator.md", "step_number": 8, "title": "Deployment Generator",
     "description": "Generate the Databricks Asset Bundle, env config, and deploy tooling."},
    {"filename": "09_test_matrix_and_fixtures.md", "step_number": 9, "title": "Test Matrix and Fixtures",
     "description": "Build the scenario-driven test matrix covering all migration patterns."},
    {"filename": "10_automated_tests.md", "step_number": 10, "title": "Automated Tests",
     "description": "Generate the pytest suite, fixtures, and golden-output snapshots."},
    {"filename": "11_end_to_end_validation.md", "step_number": 11, "title": "End-to-End Validation",
     "description": "Run the full pipeline against the sample repo and validate outputs."},
    {"filename": "12_adversarial_review.md", "step_number": 12, "title": "Adversarial Review",
     "description": "Hunt for hidden dependencies, naive-translation risks, and scoping bugs."},
    {"filename": "13_github_push.md", "step_number": 13, "title": "GitHub Push",
     "description": "Initialise git, create the GitHub repo, push, tag, and create a release."},
    {"filename": "14_architecture_override.md", "step_number": 14, "title": "Architecture Override",
     "description": "Optional: re-map the design to a non-medallion target architecture."},
]

_SKILLS_RESOURCE_URI = "accelerator://skills"


@server.list_resources()
async def list_resources() -> list[Resource]:
    return [
        Resource(
            uri=_SKILLS_RESOURCE_URI,
            name="skills",
            description="The list of skill files and their descriptions",
            mimeType="application/json",
        )
    ]


@server.read_resource()
async def read_resource(uri: str) -> str:
    if str(uri) == _SKILLS_RESOURCE_URI:
        return json.dumps(_SKILLS_CATALOG, indent=2)
    raise ValueError(f"Unknown resource: {uri}")


# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------

def _run_full_pipeline_text(source_path: str, architecture: str) -> str:
    return f"""Run the full SQL/SSIS/Synapse -> Databricks modernisation accelerator
pipeline against the source repository at: {source_path}

Target architecture: {architecture}

Execute in order, waiting for confirmation between steps:
1. parse_source({source_path!r}) — build the inventory and dependency graph
2. analyse_inventory(<manifest_path from step 1>, architecture_override={architecture!r}) — impact analysis + architecture design
3. convert_sql(<manifest_path>) — convert tables, views, procedures, functions
4. convert_ssis(<manifest_path>) — convert SSIS packages to Workflows
5. generate_bundle(<manifest_path>, env="dev") — produce the deployable Asset Bundle
6. run_validation(<manifest_path>, test_scope="all") — validate every output

At the end of each step, summarise what was produced, list output file paths,
and list any open issues before moving to the next step.
"""


@server.list_prompts()
async def list_prompts() -> list[Prompt]:
    return [
        Prompt(
            name="run_full_pipeline",
            description="Returns a ready-to-use prompt to run the full accelerator pipeline",
            arguments=[
                PromptArgument(name="source_path", description="Path to the source repository", required=True),
                PromptArgument(name="architecture", description="Target architecture (default medallion)", required=False),
            ],
        )
    ]


@server.get_prompt()
async def get_prompt(name: str, arguments: dict[str, str] | None) -> GetPromptResult:
    if name != "run_full_pipeline":
        raise ValueError(f"Unknown prompt: {name}")
    args = arguments or {}
    source_path = args.get("source_path", "<source_path>")
    architecture = args.get("architecture", "medallion")
    text = _run_full_pipeline_text(source_path, architecture)
    return GetPromptResult(
        description="Run the full accelerator pipeline",
        messages=[PromptMessage(role="user", content=TextContent(type="text", text=text))],
    )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

async def main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
