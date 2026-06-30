"""
Shared pytest fixtures for the WWI Modernisation Accelerator test suite.

Fixture SQL/SSIS files under fixtures/ are real excerpts from the
microsoft/sql-server-samples Wide World Importers corpus (not synthetic),
except fixtures/ssis/minimal_package.dtsx, which is a real "Load City
Dimension" sequence container (byte-for-byte from DailyETLMain.dtsx)
re-wrapped in a minimal valid package envelope so it parses standalone
without needing the full 13,000-line package file for fast unit tests.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

# Fixture paths are kept relative to the current working directory (pytest is
# always invoked from the repo root — see README/CI) rather than absolute.
# classify_sql_file() embeds the path it's given verbatim into generated SQL
# comments, so an absolute path here would bake the local checkout location
# into golden_outputs/*.sql, making the golden-snapshot tests fail on any
# other machine (this broke CI on first push: the golden files were
# generated against a local Mac path that doesn't exist on GitHub runners).
FIXTURES_DIR = Path(os.path.relpath(ROOT / "fixtures"))
GOLDEN_DIR = ROOT / "golden_outputs"
OUTPUTS_DIR = ROOT / "outputs"
OUTPUT_DIR = ROOT / "output"


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES_DIR


@pytest.fixture(scope="session")
def golden_dir() -> Path:
    return GOLDEN_DIR


# ---------------------------------------------------------------------------
# SQL fixture file paths (real WWI source excerpts)
# ---------------------------------------------------------------------------

@pytest.fixture
def simple_table_sql(fixtures_dir: Path) -> Path:
    """DataLoadSimulation.FicticiousNamePool — plain lookup table, no temporal/geography/identity/FK features."""
    return fixtures_dir / "sql" / "simple_table_lift_and_shift.sql"


@pytest.fixture
def geography_temporal_table_sql(fixtures_dir: Path) -> Path:
    """Application.Cities — geography column + SQL Server temporal system-versioning."""
    return fixtures_dir / "sql" / "geography_temporal_table.sql"


@pytest.fixture
def cursor_procedure_sql(fixtures_dir: Path) -> Path:
    """Integration.GetCityUpdates — CURSOR/WHILE-driven change-detection procedure."""
    return fixtures_dir / "sql" / "cursor_procedure.sql"


@pytest.fixture
def set_based_procedure_sql(fixtures_dir: Path) -> Path:
    """Integration.MigrateStagedCityData — pure set-based MERGE/INSERT procedure."""
    return fixtures_dir / "sql" / "set_based_procedure.sql"


@pytest.fixture
def forjson_view_sql(fixtures_dir: Path) -> Path:
    """WebApi.Cities — view using FOR JSON, no Spark SQL equivalent."""
    return fixtures_dir / "sql" / "forjson_view.sql"


@pytest.fixture
def scalar_function_sql(fixtures_dir: Path) -> Path:
    """Website.CalculateCustomerPrice — multi-statement procedural scalar function."""
    return fixtures_dir / "sql" / "scalar_function.sql"


# ---------------------------------------------------------------------------
# SSIS fixture file paths
# ---------------------------------------------------------------------------

@pytest.fixture
def minimal_dtsx(fixtures_dir: Path) -> Path:
    """Real 'Load City Dimension' sequence container re-wrapped as a standalone package."""
    return fixtures_dir / "ssis" / "minimal_package.dtsx"


@pytest.fixture
def source_conmgr(fixtures_dir: Path) -> Path:
    return fixtures_dir / "ssis" / "WWI_Source_DB.conmgr"


@pytest.fixture
def dest_conmgr(fixtures_dir: Path) -> Path:
    return fixtures_dir / "ssis" / "WWI_DW_Destination_DB.conmgr"


# ---------------------------------------------------------------------------
# Real pipeline outputs (for integration-style regression tests).
# Skipped automatically if the upstream pipeline hasn't been run.
# ---------------------------------------------------------------------------

def _load_json_or_skip(path: Path) -> dict:
    if not path.exists():
        pytest.skip(f"{path} not found — run the accelerator pipeline (run_analysis.py etc.) first")
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def real_inventory() -> dict:
    return _load_json_or_skip(OUTPUTS_DIR / "inventory.json")


@pytest.fixture(scope="session")
def real_dependencies() -> dict:
    return _load_json_or_skip(OUTPUTS_DIR / "dependencies.json")


@pytest.fixture(scope="session")
def real_complexity_scores() -> dict:
    return _load_json_or_skip(OUTPUTS_DIR / "object_complexity_scores.json")


@pytest.fixture(scope="session")
def real_conversion_manifest() -> dict:
    return _load_json_or_skip(OUTPUT_DIR / "conversion_manifest.json")


@pytest.fixture(scope="session")
def real_workflow_spec() -> dict:
    return _load_json_or_skip(OUTPUT_DIR / "workflow_spec.json")


# ---------------------------------------------------------------------------
# Small synthetic inventories for deterministic, hand-verifiable unit tests
# ---------------------------------------------------------------------------

@pytest.fixture
def tiny_inventory() -> dict:
    """A 4-object inventory with a known, hand-verifiable dependency chain:
    Bronze staging -> Silver dimension -> Gold fact, plus an isolated table.
    """
    objects = [
        {
            "id": "DW:Integration.City_Staging", "name": "City_Staging", "schema": "Integration",
            "object_type": "TABLE", "source_project": "DW", "medallion_layer": "BRONZE",
            "complexity_band": "LOW", "risk": "NONE", "etl_semantics": ["STAGING_TO_DW"],
            "table_features": [], "references": {"tables": [], "procedures": [], "functions": []},
            "raw_ddl": "CREATE TABLE Integration.City_Staging ([WWI City ID] int, City nvarchar(50))",
        },
        {
            "id": "DW:Dimension.City", "name": "City", "schema": "Dimension",
            "object_type": "TABLE", "source_project": "DW", "medallion_layer": "SILVER",
            "complexity_band": "LOW", "risk": "LOW", "etl_semantics": ["SCD2"],
            "table_features": [],
            "references": {"tables": ["Integration.City_Staging"], "procedures": [], "functions": []},
            "raw_ddl": "CREATE TABLE Dimension.City ([City Key] int, [WWI City ID] int, [Valid From] datetime2(7), [Valid To] datetime2(7))",
        },
        {
            "id": "DW:Fact.Sale", "name": "Sale", "schema": "Fact",
            "object_type": "TABLE", "source_project": "DW", "medallion_layer": "GOLD",
            "complexity_band": "LOW", "risk": "LOW", "etl_semantics": ["FACT_LOAD"],
            "table_features": [],
            "references": {"tables": ["Dimension.City"], "procedures": [], "functions": []},
            "raw_ddl": "CREATE TABLE Fact.Sale ([Sale Key] int, [City Key] int)",
        },
        {
            "id": "DW:dbo.SampleVersion", "name": "SampleVersion", "schema": "dbo",
            "object_type": "TABLE", "source_project": "DW", "medallion_layer": "BRONZE",
            "complexity_band": "LOW", "risk": "NONE", "etl_semantics": [],
            "table_features": [],
            "references": {"tables": [], "procedures": [], "functions": []},
            "raw_ddl": "CREATE TABLE dbo.SampleVersion (Version int)",
        },
    ]
    return {"objects": objects, "total_objects": len(objects)}


@pytest.fixture
def cyclic_inventory() -> dict:
    """Two objects that reference each other — used to verify cycle detection."""
    objects = [
        {
            "id": "DW:dbo.A", "name": "A", "schema": "dbo", "object_type": "VIEW",
            "source_project": "DW", "medallion_layer": "SILVER", "complexity_band": "LOW",
            "risk": "NONE", "etl_semantics": [], "table_features": [],
            "references": {"tables": ["dbo.B"], "procedures": [], "functions": []},
            "raw_ddl": "CREATE VIEW dbo.A AS SELECT * FROM dbo.B",
        },
        {
            "id": "DW:dbo.B", "name": "B", "schema": "dbo", "object_type": "VIEW",
            "source_project": "DW", "medallion_layer": "SILVER", "complexity_band": "LOW",
            "risk": "NONE", "etl_semantics": [], "table_features": [],
            "references": {"tables": ["dbo.A"], "procedures": [], "functions": []},
            "raw_ddl": "CREATE VIEW dbo.B AS SELECT * FROM dbo.A",
        },
    ]
    return {"objects": objects, "total_objects": len(objects)}
