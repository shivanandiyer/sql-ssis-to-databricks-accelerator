"""
tests/test_mcp_server.py

Tests for the MCP server module: tool registration, resource listing, and
prompt registration. The mcp SDK is required; all tests skip if it is absent.

The server module lives at mcp/server.py inside a folder named "mcp" — the
same name as the SDK package. It must be imported via importlib rather than a
normal "import mcp.server" to avoid the naming collision (see the docstring in
mcp/server.py for the full explanation).
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType

import pytest

ROOT = Path(__file__).parent.parent

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_server_module() -> ModuleType:
    """Load mcp/server.py as an isolated module without importing the mcp/ dir
    as a package (which would shadow the real mcp SDK)."""
    server_path = ROOT / "mcp" / "server.py"
    # Temporarily add mcp/ to sys.path so that `from tools.xxx import ...`
    # resolves correctly during the module load — same as running the script
    # directly from the mcp/ directory.
    mcp_dir = str(ROOT / "mcp")
    if mcp_dir not in sys.path:
        sys.path.insert(0, mcp_dir)
    spec = importlib.util.spec_from_file_location("_mcp_server", server_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


try:
    _server_mod = _load_server_module()
    _IMPORT_ERROR: Exception | None = None
except Exception as exc:
    _server_mod = None
    _IMPORT_ERROR = exc

_requires_mcp = pytest.mark.skipif(
    _IMPORT_ERROR is not None,
    reason=f"mcp/server.py could not be imported: {_IMPORT_ERROR}",
)

# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_server_module_imports_without_error():
    """Importing mcp/server.py must succeed when the mcp SDK is installed.
    Skips (not fails) when the SDK is absent — the SDK requires Python >=3.10
    and this test environment may be running an older interpreter."""
    if _IMPORT_ERROR is not None:
        pytest.skip(f"mcp SDK not available — skipping import test: {_IMPORT_ERROR}")


@_requires_mcp
def test_six_tools_registered():
    """_TOOLS must list exactly the 6 pipeline tools."""
    tools = _server_mod._TOOLS
    names = {t.name for t in tools}
    expected = {
        "parse_source",
        "analyse_inventory",
        "convert_sql",
        "convert_ssis",
        "generate_bundle",
        "run_validation",
    }
    assert names == expected, f"registered tool names mismatch: {names}"


@_requires_mcp
def test_tool_handlers_cover_all_tools():
    """_TOOL_HANDLERS must have an entry for every name in _TOOLS."""
    tool_names = {t.name for t in _server_mod._TOOLS}
    handler_names = set(_server_mod._TOOL_HANDLERS.keys())
    assert tool_names == handler_names


@_requires_mcp
def test_skills_catalog_has_15_entries():
    """_SKILLS_CATALOG must have 15 entries (skills/00 through 14)."""
    catalog = _server_mod._SKILLS_CATALOG
    assert len(catalog) == 15, f"expected 15 skills, got {len(catalog)}"


@_requires_mcp
def test_skills_catalog_step_numbers_are_sequential():
    catalog = _server_mod._SKILLS_CATALOG
    steps = [e["step_number"] for e in catalog]
    assert steps == list(range(15))


@_requires_mcp
def test_skills_resource_uri_is_registered():
    """The accelerator://skills resource URI must be declared."""
    assert _server_mod._SKILLS_RESOURCE_URI == "accelerator://skills"


@_requires_mcp
def test_run_full_pipeline_prompt_is_defined():
    """_run_full_pipeline_text must produce a non-empty string containing the
    six step labels and the supplied source_path."""
    text = _server_mod._run_full_pipeline_text("/some/repo", "medallion")
    assert "/some/repo" in text
    for tool_name in ("parse_source", "analyse_inventory", "convert_sql",
                      "convert_ssis", "generate_bundle", "run_validation"):
        assert tool_name in text, f"prompt missing tool name: {tool_name}"


@_requires_mcp
def test_server_name_and_version():
    assert _server_mod.SERVER_NAME == "sql-ssis-databricks-accelerator"
    assert _server_mod.SERVER_VERSION == "1.0.0"
