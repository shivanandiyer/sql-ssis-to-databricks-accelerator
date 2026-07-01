"""
tests/test_mcp_tools.py

Integration tests for the six MCP tool handlers in mcp/tools/.

Each test uses an isolated temporary directory so tests never interfere with
real pipeline outputs under output/ or outputs/. Fixtures are synthetic (built
inline) or drawn from the real SQL/SSIS fixture files under fixtures/ — no
network access or full-corpus parse is needed.

The handlers are imported directly (not via the server module) so the tests
are runnable even without the mcp SDK installed.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
MCP_TOOLS = ROOT / "mcp"
if str(MCP_TOOLS) not in sys.path:
    sys.path.insert(0, str(MCP_TOOLS))

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def run(coro):
    """Run an async handler synchronously."""
    return asyncio.run(coro)


def _tiny_inventory(tmp: Path) -> Path:
    """Write a 3-object inventory.json + dependencies.json to tmp/ and return
    the inventory path. Objects are chosen so they have unique schema.name
    combinations (no target-FQN collision in medallion mapping)."""
    objects = [
        {
            "id": "DW:Integration.City_Staging",
            "name": "City_Staging",
            "schema": "Integration",
            "object_type": "TABLE",
            "source_project": "DW",
            "medallion_layer": "BRONZE",
            "complexity_band": "LOW",
            "risk": "NONE",
            "etl_semantics": ["STAGING_TO_DW"],
            "table_features": [],
            "references": {"tables": [], "procedures": [], "functions": []},
            "raw_ddl": "CREATE TABLE Integration.City_Staging ([WWI City ID] int, City nvarchar(50))",
        },
        {
            "id": "DW:Dimension.City",
            "name": "City",
            "schema": "Dimension",
            "object_type": "TABLE",
            "source_project": "DW",
            "medallion_layer": "SILVER",
            "complexity_band": "LOW",
            "risk": "LOW",
            "etl_semantics": ["SCD2"],
            "table_features": [],
            "references": {"tables": ["Integration.City_Staging"], "procedures": [], "functions": []},
            "raw_ddl": "CREATE TABLE Dimension.City ([City Key] int, [Valid From] datetime2(7))",
        },
        {
            "id": "DW:Fact.Sale",
            "name": "Sale",
            "schema": "Fact",
            "object_type": "TABLE",
            "source_project": "DW",
            "medallion_layer": "GOLD",
            "complexity_band": "LOW",
            "risk": "LOW",
            "etl_semantics": ["FACT_LOAD"],
            "table_features": [],
            "references": {"tables": ["Dimension.City"], "procedures": [], "functions": []},
            "raw_ddl": "CREATE TABLE Fact.Sale ([Sale Key] int, [City Key] int)",
        },
    ]
    inv = {"version": "1.0", "total_objects": 3, "unsupported_count": 0, "summary": {}, "objects": objects}
    inv_path = tmp / "inventory.json"
    inv_path.write_text(json.dumps(inv, indent=2), encoding="utf-8")

    # Build dependencies.json using the real graph builder so it's in the
    # correct format (the handlers read this file directly).
    from accelerator.analyzers.dependency_graph import build_and_save_graph
    build_and_save_graph(inv, tmp)

    return inv_path


def _ssis_inventory(tmp: Path) -> Path:
    """Write an inventory.json + dependencies.json that includes one SSIS_PACKAGE
    object (parsed from the real fixtures/ssis/minimal_package.dtsx)."""
    from accelerator.parsers.ssis_parser import parse_project
    from accelerator.analyzers.inventory_builder import build_inventory
    from accelerator.analyzers.dependency_graph import build_and_save_graph

    sql_obj = [
        {
            "id": "DW:Integration.City_Staging",
            "name": "City_Staging",
            "schema": "Integration",
            "object_type": "TABLE",
            "source_project": "DW",
            "medallion_layer": "BRONZE",
            "complexity_band": "LOW",
            "risk": "NONE",
            "etl_semantics": [],
            "table_features": [],
            "references": {"tables": [], "procedures": [], "functions": []},
            "raw_ddl": "CREATE TABLE Integration.City_Staging ([WWI City ID] int)",
        }
    ]
    pkgs = parse_project(ROOT / "fixtures" / "ssis")
    inv = build_inventory(sql_obj, pkgs, tmp)
    build_and_save_graph(inv, tmp)
    return tmp / "inventory.json"


# ---------------------------------------------------------------------------
# handle_parse_source
# ---------------------------------------------------------------------------

def _sql_fixture_config(tmp_path: Path) -> str:
    """Write a parser_config.json that points oltp_dir at fixtures/sql (no
    .sqlproj required) and return its path as a string."""
    cfg = {"oltp_dir": str(ROOT / "fixtures" / "sql")}
    cfg_path = tmp_path / "parser_config.json"
    cfg_path.write_text(json.dumps(cfg), encoding="utf-8")
    return str(cfg_path)


class TestHandleParseSource:

    def test_inventory_json_is_written(self, tmp_path):
        from tools.parse_source import handle_parse_source
        cfg = _sql_fixture_config(tmp_path)
        result = run(handle_parse_source(str(ROOT / "fixtures"), config_path=cfg))
        assert "error" not in result, result.get("message")
        inv_path = Path(result["inventory_path"])
        assert inv_path.exists(), f"inventory.json not found at {inv_path}"
        inv = json.loads(inv_path.read_text())
        assert inv["total_objects"] > 0

    def test_return_dict_has_required_keys(self, tmp_path):
        from tools.parse_source import handle_parse_source
        cfg = _sql_fixture_config(tmp_path)
        result = run(handle_parse_source(str(ROOT / "fixtures"), config_path=cfg))
        assert "error" not in result, result.get("message")
        for key in ("inventory_path", "object_count", "summary"):
            assert key in result, f"missing key: {key}"

    def test_object_count_matches_summary_total(self, tmp_path):
        from tools.parse_source import handle_parse_source
        cfg = _sql_fixture_config(tmp_path)
        result = run(handle_parse_source(str(ROOT / "fixtures"), config_path=cfg))
        assert "error" not in result
        assert result["object_count"] == sum(result["summary"].values())

    def test_missing_source_path_returns_error(self):
        from tools.parse_source import handle_parse_source
        result = run(handle_parse_source("/nonexistent/path/does/not/exist"))
        assert result.get("error") is True
        assert isinstance(result.get("message"), str)

    def test_path_with_no_sql_files_returns_error(self, tmp_path):
        from tools.parse_source import handle_parse_source
        result = run(handle_parse_source(str(tmp_path)))
        assert result.get("error") is True
        assert isinstance(result.get("message"), str)


# ---------------------------------------------------------------------------
# handle_analyse_inventory
# ---------------------------------------------------------------------------

class TestHandleAnalyseInventory:

    def test_medallion_mapping_csv_is_written(self, tmp_path):
        from tools.analyse_inventory import handle_analyse_inventory
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_analyse_inventory(str(inv_path)))
        assert "error" not in result, result.get("message")
        assert (tmp_path / "medallion_mapping.csv").exists()

    def test_complexity_breakdown_has_required_keys(self, tmp_path):
        from tools.analyse_inventory import handle_analyse_inventory
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_analyse_inventory(str(inv_path)))
        assert "error" not in result, result.get("message")
        breakdown = result["complexity_breakdown"]
        for key in ("Lift-and-shift friendly", "Partial automation possible"):
            assert key in breakdown, f"complexity_breakdown missing key: {key!r}"

    def test_architecture_is_returned(self, tmp_path):
        from tools.analyse_inventory import handle_analyse_inventory
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_analyse_inventory(str(inv_path)))
        assert "error" not in result
        assert isinstance(result["architecture"], str)
        assert len(result["architecture"]) > 0

    def test_architecture_override_lakehouse(self, tmp_path):
        from tools.analyse_inventory import handle_analyse_inventory
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_analyse_inventory(str(inv_path), architecture_override="lakehouse"))
        assert "error" not in result, result.get("message")

    def test_invalid_architecture_returns_error(self, tmp_path):
        from tools.analyse_inventory import handle_analyse_inventory
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_analyse_inventory(str(inv_path), architecture_override="bogus"))
        assert result.get("error") is True
        assert isinstance(result.get("message"), str)

    def test_missing_manifest_returns_error(self):
        from tools.analyse_inventory import handle_analyse_inventory
        result = run(handle_analyse_inventory("/nonexistent/inventory.json"))
        assert result.get("error") is True

    def test_missing_dependencies_returns_error(self, tmp_path):
        from tools.analyse_inventory import handle_analyse_inventory
        inv_path = tmp_path / "inventory.json"
        inv_path.write_text(json.dumps({"objects": [], "total_objects": 0}))
        # no dependencies.json written alongside it
        result = run(handle_analyse_inventory(str(inv_path)))
        assert result.get("error") is True


# ---------------------------------------------------------------------------
# handle_convert_sql
# ---------------------------------------------------------------------------

class TestHandleConvertSql:

    def test_at_least_one_file_written_to_databricks_sql(self, tmp_path):
        from tools.convert_sql import handle_convert_sql
        inv_path = _tiny_inventory(tmp_path)
        out = tmp_path / "out"
        result = run(handle_convert_sql(str(inv_path), output_path=str(out)))
        assert "error" not in result, result.get("message")
        sql_files = list((out / "databricks_sql").glob("*.sql"))
        assert len(sql_files) >= 1, "no .sql files written to databricks_sql/"

    def test_converted_plus_partial_plus_manual_equals_total(self, tmp_path):
        from tools.convert_sql import handle_convert_sql
        inv_path = _tiny_inventory(tmp_path)
        out = tmp_path / "out"
        result = run(handle_convert_sql(str(inv_path), output_path=str(out)))
        assert "error" not in result, result.get("message")
        inv = json.loads(inv_path.read_text())
        total = sum(1 for o in inv["objects"] if o["object_type"] in
                    {"TABLE", "VIEW", "PROCEDURE", "SCALAR_FUNCTION", "TVF_INLINE", "TVF_MULTI"})
        assert result["converted_count"] + result["partial_count"] + result["manual_count"] == total

    def test_conversion_manifest_is_written(self, tmp_path):
        from tools.convert_sql import handle_convert_sql
        inv_path = _tiny_inventory(tmp_path)
        out = tmp_path / "out"
        result = run(handle_convert_sql(str(inv_path), output_path=str(out)))
        assert "error" not in result
        assert Path(result["output_paths"]["manifest"]).exists()

    def test_object_filter_restricts_output(self, tmp_path):
        from tools.convert_sql import handle_convert_sql
        inv_path = _tiny_inventory(tmp_path)
        out = tmp_path / "out"
        result = run(handle_convert_sql(
            str(inv_path),
            output_path=str(out),
            object_filter=["DW:Integration.City_Staging"],
        ))
        assert "error" not in result
        assert result["converted_count"] + result["partial_count"] + result["manual_count"] == 1

    def test_missing_manifest_returns_error(self, tmp_path):
        from tools.convert_sql import handle_convert_sql
        result = run(handle_convert_sql("/nonexistent/inventory.json", output_path=str(tmp_path)))
        assert result.get("error") is True
        assert isinstance(result.get("message"), str)


# ---------------------------------------------------------------------------
# handle_convert_ssis
# ---------------------------------------------------------------------------

class TestHandleConvertSsis:

    def test_workflow_spec_json_is_written(self, tmp_path):
        from tools.convert_ssis import handle_convert_ssis
        inv_path = _ssis_inventory(tmp_path)
        out = tmp_path / "out"
        result = run(handle_convert_ssis(str(inv_path), output_path=str(out)))
        assert "error" not in result, result.get("message")
        assert Path(result["workflow_spec_path"]).exists()

    def test_task_count_is_positive(self, tmp_path):
        from tools.convert_ssis import handle_convert_ssis
        inv_path = _ssis_inventory(tmp_path)
        out = tmp_path / "out"
        result = run(handle_convert_ssis(str(inv_path), output_path=str(out)))
        assert "error" not in result, result.get("message")
        assert result["task_count"] > 0

    def test_no_ssis_package_in_inventory_returns_error(self, tmp_path):
        from tools.convert_ssis import handle_convert_ssis
        # Use the SQL-only tiny inventory (no SSIS_PACKAGE object)
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_convert_ssis(str(inv_path), output_path=str(tmp_path / "out")))
        assert result.get("error") is True
        assert isinstance(result.get("message"), str)

    def test_missing_manifest_returns_error(self, tmp_path):
        from tools.convert_ssis import handle_convert_ssis
        result = run(handle_convert_ssis("/nonexistent/inventory.json"))
        assert result.get("error") is True


# ---------------------------------------------------------------------------
# handle_generate_bundle
# ---------------------------------------------------------------------------

class TestHandleGenerateBundle:

    def _prepare(self, tmp_path: Path) -> tuple[Path, Path]:
        """Build inventory + workflow_spec.json in tmp_path; return (inv_path, out_dir)."""
        inv_path = _ssis_inventory(tmp_path)
        from accelerator.converters.ssis_converter import convert_ssis_package
        inv = json.loads(inv_path.read_text())
        graph = json.loads((tmp_path / "dependencies.json").read_text())
        convert_ssis_package(inv, graph, tmp_path / "ssis_out")
        # workflow_spec.json is in ssis_out/; handler also checks REPO_ROOT/output/
        # — move it alongside the inventory so the first candidate path matches.
        import shutil
        ws = tmp_path / "ssis_out" / "workflow_spec.json"
        shutil.copy(ws, tmp_path / "workflow_spec.json")
        return inv_path, tmp_path / "bundle"

    def test_job_yml_is_written_in_bundle_resources(self, tmp_path):
        from tools.generate_bundle import handle_generate_bundle
        inv_path, out = self._prepare(tmp_path)
        result = run(handle_generate_bundle(str(inv_path), env="dev", output_path=str(out)))
        assert "error" not in result, result.get("message")
        bundle_file = Path(result["bundle_path"])
        assert bundle_file.exists()
        assert bundle_file.suffix == ".yml"

    def test_environment_is_returned(self, tmp_path):
        from tools.generate_bundle import handle_generate_bundle
        inv_path, out = self._prepare(tmp_path)
        result = run(handle_generate_bundle(str(inv_path), env="test", output_path=str(out)))
        assert "error" not in result
        assert result["environment"] == "test"

    def test_invalid_env_returns_error(self, tmp_path):
        from tools.generate_bundle import handle_generate_bundle
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_generate_bundle(str(inv_path), env="staging"))
        assert result.get("error") is True
        assert isinstance(result.get("message"), str)

    def test_missing_manifest_returns_error(self, tmp_path):
        from tools.generate_bundle import handle_generate_bundle
        result = run(handle_generate_bundle("/nonexistent/inventory.json"))
        assert result.get("error") is True

    def test_missing_workflow_spec_returns_error(self, tmp_path, monkeypatch):
        import tools.generate_bundle as gb_module
        from tools.generate_bundle import handle_generate_bundle
        # Redirect _REPO_ROOT so the handler's fallback path (REPO_ROOT/output/workflow_spec.json)
        # also resolves to a directory with no workflow_spec.json.
        monkeypatch.setattr(gb_module, "_REPO_ROOT", tmp_path)
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_generate_bundle(str(inv_path), output_path=str(tmp_path / "bundle")))
        assert result.get("error") is True


# ---------------------------------------------------------------------------
# handle_run_validation
# ---------------------------------------------------------------------------

class TestHandleRunValidation:

    def test_summary_path_is_written(self, tmp_path):
        from tools.run_validation import handle_run_validation
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_run_validation(str(inv_path), test_scope="parsers"))
        assert "error" not in result, result.get("message")
        assert Path(result["summary_path"]).exists()

    def test_passed_plus_failed_plus_partial_is_positive(self, tmp_path):
        from tools.run_validation import handle_run_validation
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_run_validation(str(inv_path), test_scope="parsers"))
        assert "error" not in result
        assert result["passed"] + result["failed"] + result["partial"] > 0

    def test_ready_for_release_is_bool(self, tmp_path):
        from tools.run_validation import handle_run_validation
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_run_validation(str(inv_path), test_scope="parsers"))
        assert "error" not in result
        assert isinstance(result["ready_for_release"], bool)

    def test_invalid_test_scope_returns_error(self, tmp_path):
        from tools.run_validation import handle_run_validation
        inv_path = _tiny_inventory(tmp_path)
        result = run(handle_run_validation(str(inv_path), test_scope="bogus_scope"))
        assert result.get("error") is True
        assert isinstance(result.get("message"), str)

    def test_missing_manifest_returns_error(self):
        from tools.run_validation import handle_run_validation
        result = run(handle_run_validation("/nonexistent/inventory.json"))
        assert result.get("error") is True


# ---------------------------------------------------------------------------
# Cross-cutting: no handler ever raises to the caller
# ---------------------------------------------------------------------------

class TestHandlersNeverRaise:
    """Every handler must catch all exceptions internally and return
    {error: True, message: str} rather than propagating them."""

    @pytest.mark.parametrize("coro", [
        lambda: __import__("tools.parse_source", fromlist=["handle_parse_source"]).handle_parse_source(
            "/does/not/exist"
        ),
        lambda: __import__("tools.analyse_inventory", fromlist=["handle_analyse_inventory"]).handle_analyse_inventory(
            "/does/not/exist"
        ),
        lambda: __import__("tools.convert_sql", fromlist=["handle_convert_sql"]).handle_convert_sql(
            "/does/not/exist"
        ),
        lambda: __import__("tools.convert_ssis", fromlist=["handle_convert_ssis"]).handle_convert_ssis(
            "/does/not/exist"
        ),
        lambda: __import__("tools.generate_bundle", fromlist=["handle_generate_bundle"]).handle_generate_bundle(
            "/does/not/exist"
        ),
        lambda: __import__("tools.run_validation", fromlist=["handle_run_validation"]).handle_run_validation(
            "/does/not/exist"
        ),
    ], ids=["parse_source", "analyse_inventory", "convert_sql", "convert_ssis", "generate_bundle", "run_validation"])
    def test_bad_input_returns_error_dict_not_exception(self, coro):
        result = run(coro())
        assert isinstance(result, dict), f"handler returned {type(result)}, expected dict"
        assert result.get("error") is True, f"expected error=True, got {result}"
        assert isinstance(result.get("message"), str), f"expected message str, got {result}"
