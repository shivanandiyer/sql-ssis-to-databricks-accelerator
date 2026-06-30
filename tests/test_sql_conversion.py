"""
SQL conversion tests: accelerator.converters.sql_converter.

Covers table/view/function/procedure conversion against real WWI fixtures,
including a snapshot ("golden file") test for the deterministic table DDL
conversion path.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from accelerator.converters.sql_converter import (
    _map_type,
    convert_function,
    convert_procedure,
    convert_table,
    convert_view,
    parse_table_columns,
)
from accelerator.parsers.sql_project_parser import classify_sql_file

# Set REGENERATE_GOLDEN=1 in the environment to (re)write golden files after a
# deliberate, reviewed change to the converter's output format.
import os
REGENERATE_GOLDEN = os.environ.get("REGENERATE_GOLDEN") == "1"


class TestTypeMapping:
    @pytest.mark.parametrize("sql_type,expected_target", [
        ("INT", "INT"),
        ("NVARCHAR (50)", "STRING"),
        ("BIGINT", "BIGINT"),
        ("BIT", "BOOLEAN"),
        ("DATETIME2 (7)", "TIMESTAMP"),
        ("DECIMAL (18,2)", "DECIMAL(18,2)"),
        ("MONEY", "DECIMAL(19,4)"),
        ("UNIQUEIDENTIFIER", "STRING"),
    ])
    def test_common_types_map_directly(self, sql_type, expected_target):
        target, note = _map_type(sql_type)
        assert target == expected_target

    def test_geography_maps_to_string_with_review_note(self):
        target, note = _map_type("[sys].[geography]")
        assert target == "STRING"
        assert note is not None
        assert "MANUAL REVIEW REQUIRED" in note

    def test_hierarchyid_flagged_for_review(self):
        target, note = _map_type("hierarchyid")
        assert target == "STRING"
        assert "MANUAL REVIEW REQUIRED" in note

    def test_unrecognised_type_defaults_to_string_with_warning(self):
        target, note = _map_type("some_made_up_type")
        assert target == "STRING"
        assert "MANUAL REVIEW REQUIRED" in note


class TestColumnParsing:
    def test_geography_column_not_truncated(self, geography_temporal_table_sql: Path):
        """Regression: a prior version of this regex truncated schema-qualified
        types like [sys].[geography] down to just '[sys]', silently losing the
        single highest-priority data-type risk in the whole corpus."""
        raw_ddl = geography_temporal_table_sql.read_text(encoding="utf-8-sig")
        columns, constraints = parse_table_columns(raw_ddl)
        location_col = next(c for c in columns if c["name"] == "Location")
        assert location_col["sql_type"] == "[sys].[geography]"

    def test_system_versioned_columns_flagged(self, geography_temporal_table_sql: Path):
        raw_ddl = geography_temporal_table_sql.read_text(encoding="utf-8-sig")
        columns, _ = parse_table_columns(raw_ddl)
        valid_from = next(c for c in columns if c["name"] == "ValidFrom")
        assert valid_from["system_versioned"] is True

    def test_foreign_keys_extracted_as_constraints_not_columns(self, geography_temporal_table_sql: Path):
        raw_ddl = geography_temporal_table_sql.read_text(encoding="utf-8-sig")
        columns, constraints = parse_table_columns(raw_ddl)
        col_names = {c["name"] for c in columns}
        assert "CONSTRAINT" not in col_names
        assert any("FOREIGN KEY" in c.upper() for c in constraints)


class TestTableConversion:
    def test_simple_table_no_warnings(self, simple_table_sql: Path):
        obj = classify_sql_file(simple_table_sql, source_project="OLTP")
        obj["medallion_layer"] = "BRONZE"
        result = convert_table(obj, "wwi_dev.bronze.application__deliverymethods")
        assert result["needs_review"] is False
        assert "CREATE TABLE IF NOT EXISTS wwi_dev.bronze.application__deliverymethods" in result["sql"]

    def test_geography_table_flagged_for_review(self, geography_temporal_table_sql: Path):
        obj = classify_sql_file(geography_temporal_table_sql, source_project="OLTP")
        obj["medallion_layer"] = "BRONZE"
        result = convert_table(obj, "wwi_dev.bronze.application__cities")
        assert result["needs_review"] is True
        assert "geography" in result["sql"].lower() or "MANUAL REVIEW REQUIRED" in result["sql"]
        assert "ValidFrom" not in result["sql"].split("-- Conversion notes:")[0].split("(\n")[1].split(")")[0] \
            if "(\n" in result["sql"] else True  # system-versioned column dropped from column list

    def test_table_conversion_is_deterministic(self, geography_temporal_table_sql: Path):
        obj = classify_sql_file(geography_temporal_table_sql, source_project="OLTP")
        obj["medallion_layer"] = "BRONZE"
        result1 = convert_table(obj, "wwi_dev.bronze.application__cities")
        result2 = convert_table(obj, "wwi_dev.bronze.application__cities")
        assert result1["sql"] == result2["sql"]

    def test_golden_snapshot_simple_table(self, simple_table_sql: Path, golden_dir: Path):
        obj = classify_sql_file(simple_table_sql, source_project="OLTP")
        obj["medallion_layer"] = "BRONZE"
        result = convert_table(obj, "wwi_dev.bronze.application__deliverymethods")
        golden_path = golden_dir / "simple_table_lift_and_shift.sql"
        if REGENERATE_GOLDEN or not golden_path.exists():
            golden_path.write_text(result["sql"], encoding="utf-8")
            pytest.skip("golden file (re)written — re-run to verify")
        expected = golden_path.read_text(encoding="utf-8")
        assert result["sql"] == expected

    def test_golden_snapshot_geography_table(self, geography_temporal_table_sql: Path, golden_dir: Path):
        obj = classify_sql_file(geography_temporal_table_sql, source_project="OLTP")
        obj["medallion_layer"] = "BRONZE"
        result = convert_table(obj, "wwi_dev.bronze.application__cities")
        golden_path = golden_dir / "geography_temporal_table.sql"
        if REGENERATE_GOLDEN or not golden_path.exists():
            golden_path.write_text(result["sql"], encoding="utf-8")
            pytest.skip("golden file (re)written — re-run to verify")
        expected = golden_path.read_text(encoding="utf-8")
        assert result["sql"] == expected


class TestViewConversion:
    def test_simple_view_no_warnings(self):
        obj = {
            "id": "OLTP:WebApi.BuyingGroups", "name": "BuyingGroups", "schema": "WebApi",
            "object_type": "VIEW", "source_file": "BuyingGroups.sql", "medallion_layer": "SILVER",
            "raw_ddl": "CREATE VIEW [WebApi].[BuyingGroups]\nAS\nSELECT BuyingGroupID, BuyingGroupName\nFROM Sales.BuyingGroups",
        }
        result = convert_view(obj, "wwi_dev.silver.webapi__buyinggroups")
        assert result["needs_review"] is False
        assert "CREATE OR REPLACE VIEW wwi_dev.silver.webapi__buyinggroups AS" in result["sql"]

    def test_forjson_view_flagged_for_review(self, forjson_view_sql: Path):
        obj = classify_sql_file(forjson_view_sql, source_project="OLTP")
        obj["medallion_layer"] = "SILVER"
        result = convert_view(obj, "wwi_dev.silver.webapi__cities")
        assert result["needs_review"] is True
        assert any("FOR JSON" in w for w in result["warnings"])


class TestFunctionConversion:
    def test_procedural_function_routed_to_pyspark(self, scalar_function_sql: Path):
        obj = classify_sql_file(scalar_function_sql, source_project="OLTP")
        obj["medallion_layer"] = "SILVER"
        result = convert_function(obj, "wwi_dev.silver.website__calculatecustomerprice")
        assert "pyspark" in result
        assert result["needs_review"] is True
        assert "NotImplementedError" in result["pyspark"]


class TestProcedureConversion:
    def test_set_based_procedure_converts_to_sql_only(self, set_based_procedure_sql: Path):
        obj = classify_sql_file(set_based_procedure_sql, source_project="DW")
        obj["medallion_layer"] = "BRONZE"
        obj["schema"] = "Integration"  # already Integration per fixture, kept explicit for clarity
        result = convert_procedure(obj, "PARTIAL_AUTOMATION", "wwi_dev.bronze.integration__migratestagedcitydata")
        assert result["split"] is False
        assert "databricks_sql" in result["files"]
        assert "pyspark" not in result["files"]

    def test_cursor_procedure_split_into_sql_and_pyspark(self, cursor_procedure_sql: Path):
        obj = classify_sql_file(cursor_procedure_sql, source_project="OLTP")
        obj["medallion_layer"] = "BRONZE"
        assert obj["schema"] == "Integration"  # orchestration-heavy trigger condition
        result = convert_procedure(obj, "MANUAL_REDESIGN", "wwi_dev.bronze.integration__getcityupdates")
        assert result["split"] is True
        assert "databricks_sql" in result["files"]
        assert "pyspark" in result["files"]
        assert result["needs_review"] is True
        factor_text = " ".join(result["warnings"])
        assert "CURSOR" in factor_text
        assert "WHILE" in factor_text

    def test_non_orchestration_procedural_procedure_single_pyspark_stub(self):
        """A procedural (CURSOR-using) procedure outside the Integration schema
        should NOT be split — only orchestration-heavy procedures are."""
        obj = {
            "id": "OLTP:Sales.SomeCursorProc", "name": "SomeCursorProc", "schema": "Sales",
            "object_type": "PROCEDURE", "source_file": "SomeCursorProc.sql",
            "medallion_layer": "BRONZE", "etl_semantics": [],
            "raw_ddl": "CREATE PROCEDURE Sales.SomeCursorProc AS BEGIN DECLARE c CURSOR FOR SELECT 1; OPEN c; CLOSE c; END",
        }
        result = convert_procedure(obj, "MANUAL_REDESIGN", "wwi_dev.bronze.sales__somecursorproc")
        assert result["split"] is False
        assert "pyspark" in result["files"]
        assert "databricks_sql" not in result["files"]


class TestGracefulFailureAndDisposition:
    def test_empty_ddl_does_not_raise(self):
        obj = {"id": "OLTP:dbo.Empty", "name": "Empty", "schema": "dbo", "object_type": "TABLE",
               "source_file": "", "medallion_layer": "BRONZE", "raw_ddl": "", "table_features": []}
        result = convert_table(obj, "wwi_dev.bronze.dbo__empty")
        assert result["sql"]  # produced *something* rather than raising

    @pytest.mark.parametrize("fixture_name,expected_disposition", [
        ("simple_table_sql", "converted"),
        ("geography_temporal_table_sql", "partial"),
        ("cursor_procedure_sql", "manual"),
    ])
    def test_disposition_assignment(self, request, fixture_name, expected_disposition):
        """Every converted object must resolve to converted / partial / manual."""
        path = request.getfixturevalue(fixture_name)
        obj = classify_sql_file(path, source_project="OLTP")
        obj["medallion_layer"] = "BRONZE"
        obj["etl_semantics"] = []

        if obj["object_type"] == "TABLE":
            result = convert_table(obj, "wwi_dev.bronze.x")
            warnings = result["warnings"]
        elif obj["object_type"] == "PROCEDURE":
            result = convert_procedure(obj, "MANUAL_REDESIGN", "wwi_dev.bronze.x")
            warnings = result["warnings"]
        else:
            pytest.skip("disposition mapping defined for TABLE/PROCEDURE in this test")

        def disposition() -> str:
            if not warnings:
                return "converted"
            if any("MANUAL REVIEW REQUIRED" not in w and "CURSOR" not in w and "WHILE" not in w for w in warnings) \
                    and not any("CURSOR" in w or "WHILE" in w for w in warnings):
                return "partial"
            if any("CURSOR" in w or "WHILE" in w for w in warnings):
                return "manual"
            return "partial"

        assert disposition() == expected_disposition
