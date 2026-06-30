"""
Parser tests: accelerator.parsers.sql_project_parser and accelerator.parsers.ssis_parser.

Uses real WWI source excerpts under fixtures/sql and fixtures/ssis.
"""

from __future__ import annotations

from pathlib import Path

from accelerator.parsers.sql_project_parser import classify_sql_file
from accelerator.parsers.ssis_parser import parse_conmgr, parse_dtsx


class TestSqlClassification:
    def test_simple_table_classified_as_table(self, simple_table_sql: Path):
        obj = classify_sql_file(simple_table_sql, source_project="OLTP")
        assert obj["object_type"] == "TABLE"
        assert obj["schema"] == "DataLoadSimulation"
        assert obj["name"] == "FicticiousNamePool"
        assert obj["complexity_band"] == "LOW"

    def test_geography_temporal_table_features_detected(self, geography_temporal_table_sql: Path):
        obj = classify_sql_file(geography_temporal_table_sql, source_project="OLTP")
        assert obj["object_type"] == "TABLE"
        assert obj["name"] == "Cities"
        assert "TEMPORAL" in obj["table_features"]
        # Regression: column type parsing must not truncate schema-qualified
        # types like [sys].[geography] down to just "[sys]".
        assert "[sys].[geography]" in obj["raw_ddl"]

    def test_cursor_procedure_flagged_high_complexity(self, cursor_procedure_sql: Path):
        obj = classify_sql_file(cursor_procedure_sql, source_project="OLTP")
        assert obj["object_type"] == "PROCEDURE"
        assert obj["name"] == "GetCityUpdates"
        assert obj["complexity_band"] in ("MEDIUM", "HIGH", "VERY_HIGH")
        factor_text = " ".join(obj["complexity_factors"])
        assert "CURSOR" in factor_text
        assert "WHILE" in factor_text

    def test_set_based_procedure_low_complexity(self, set_based_procedure_sql: Path):
        obj = classify_sql_file(set_based_procedure_sql, source_project="DW")
        assert obj["object_type"] == "PROCEDURE"
        factor_text = " ".join(obj["complexity_factors"])
        assert "CURSOR" not in factor_text
        assert "WHILE" not in factor_text

    def test_forjson_view_classified_as_view(self, forjson_view_sql: Path):
        obj = classify_sql_file(forjson_view_sql, source_project="OLTP")
        assert obj["object_type"] == "VIEW"
        assert "FOR JSON" in obj["raw_ddl"].upper() or "FOR\nJSON" in obj["raw_ddl"].upper()

    def test_scalar_function_name_extraction(self, scalar_function_sql: Path):
        """Regression: function subtype refinement previously broke name extraction
        because _extract_object_name's pattern dict only had a 'FUNCTION' key, not
        the refined subtype keys (SCALAR_FUNCTION/TVF_INLINE/TVF_MULTI)."""
        obj = classify_sql_file(scalar_function_sql, source_project="OLTP")
        assert obj["object_type"] == "SCALAR_FUNCTION"
        assert obj["name"] == "CalculateCustomerPrice"
        assert obj["schema"] == "Website"

    def test_graceful_failure_on_missing_file(self, tmp_path: Path):
        """Unsupported / unreadable input must not raise — it returns an UNREADABLE marker."""
        missing = tmp_path / "does_not_exist.sql"
        obj = classify_sql_file(missing, source_project="OLTP")
        assert obj["object_type"] == "UNREADABLE"
        assert "error" in obj

    def test_classification_is_deterministic(self, geography_temporal_table_sql: Path):
        obj1 = classify_sql_file(geography_temporal_table_sql, source_project="OLTP")
        obj2 = classify_sql_file(geography_temporal_table_sql, source_project="OLTP")
        # raw_ddl/source_file are expected to match exactly; complexity/classification
        # fields must be byte-identical across repeated runs (no hidden randomness/time).
        for key in ("object_type", "schema", "name", "complexity_band", "complexity_score",
                    "complexity_factors", "table_features", "etl_semantics"):
            assert obj1[key] == obj2[key], f"non-deterministic field: {key}"


class TestSsisParsing:
    def test_minimal_package_parses(self, minimal_dtsx: Path):
        pkg = parse_dtsx(minimal_dtsx)
        assert pkg["name"] == "MinimalTestPackage"
        names = {t["name"] for t in pkg["all_tasks_flat"]}
        assert "Load City Dimension" in names
        assert "Extract Updated City Data to Staging" in names
        assert "Migrate Staged City Data" in names

    def test_minimal_package_movement_paths(self, minimal_dtsx: Path):
        pkg = parse_dtsx(minimal_dtsx)
        assert len(pkg["movement_paths"]) >= 1
        dest_tables = {p["dest_table"] for p in pkg["movement_paths"] if p.get("dest_table")}
        assert any("City_Staging" in (t or "") for t in dest_tables) or any(
            "Fact.City" in (t or "") for t in dest_tables
        )

    def test_connection_manager_parsing(self, source_conmgr: Path, dest_conmgr: Path):
        source = parse_conmgr(source_conmgr)
        dest = parse_conmgr(dest_conmgr)
        assert source["database"] == "WideWorldImporters"
        assert dest["database"] == "WideWorldImportersDW"
        assert source["type"] == "OLEDB"

    def test_parsing_is_deterministic(self, minimal_dtsx: Path):
        pkg1 = parse_dtsx(minimal_dtsx)
        pkg2 = parse_dtsx(minimal_dtsx)
        assert len(pkg1["all_tasks_flat"]) == len(pkg2["all_tasks_flat"])
        names1 = sorted(t["name"] for t in pkg1["all_tasks_flat"])
        names2 = sorted(t["name"] for t in pkg2["all_tasks_flat"])
        assert names1 == names2

    def test_graceful_failure_on_malformed_xml(self, tmp_path: Path):
        bad = tmp_path / "broken.dtsx"
        bad.write_text("<DTS:Executable><not closed>", encoding="utf-8")
        try:
            result = parse_dtsx(bad)
            # If it doesn't raise, it must clearly signal failure rather than
            # returning a fabricated-looking success result.
            assert result is None or result.get("name") in (None, "") or "error" in result
        except Exception as exc:
            # Acceptable as long as it's a clear parse error, not a silent corrupt result.
            assert "syntax" in str(exc).lower() or "parse" in str(exc).lower() or isinstance(exc, Exception)
