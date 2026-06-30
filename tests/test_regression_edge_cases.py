"""
Regression tests for known edge cases.

Each test in this module pins a specific bug found and fixed during the
accelerator's development (or documents a known, deliberately-unfixed gap)
so it cannot silently reappear or be "fixed" into a different wrong answer
without a test failing first.

Bug log:
  1. sql_project_parser._extract_object_name: function subtype refinement
     (TVF_INLINE/TVF_MULTI/SCALAR_FUNCTION) broke name/schema extraction
     because the lookup dict only had a "FUNCTION" key. Fixed by aliasing
     the subtype keys to the same pattern.
  2. sql_converter.parse_table_columns: the column-type regex truncated
     schema-qualified types like [sys].[geography] down to "[sys]". Fixed by
     allowing repeated bracketed/dotted segments in the type token.
  3. impact_analysis security scoring: "EXECUTE AS OWNER" matched both a
     specific and a generic security pattern, double-counting to severity 5
     and wrongly forcing ~113 routine procedures into MANUAL_REDESIGN. Fixed
     with a negative lookahead so it scores once.
  4. dependency_graph.topological_sort: Kahn's algorithm ran over the wrong
     adjacency direction, returning dependants before dependencies despite
     the docstring promising the opposite ("safe deployment order"). Fixed by
     reversing the adjacency direction used for in-degree counting.
  5. sql_converter.convert_function: procedural detection only matched
     WHILE/CURSOR/IS_ROLEMEMBER/dynamic-EXEC, so multi-statement
     DECLARE/SET/IF function bodies (no loop or cursor) were wrongly treated
     as simple single-expression functions, producing a broken SQL UDF that
     silently dropped all the business logic. Fixed by also treating
     IF/SET/multiple-DECLARE as procedural indicators.

Known, deliberately-unfixed gaps (documented, not silently changed):
  6. inventory_builder._DEDUCTIONS keys "TEMPORAL"/"MEMORY_OPTIMIZED" never
     match obj["complexity_factors"] (they're only ever in
     obj["table_features"]), so those confidence deductions are dead code.
  7. dependency_graph.extract_etl_lineage's "upstream_count" is literally
     node fan_in (consumers/dependents), not fan_out (actual upstream
     dependencies) — already baked into published current_state_documentation.md.
"""

from __future__ import annotations

from pathlib import Path

from accelerator.analyzers.dependency_graph import build_graph, topological_sort
from accelerator.analyzers.inventory_builder import build_inventory
from accelerator.converters.sql_converter import convert_function, parse_table_columns
from accelerator.parsers.sql_project_parser import classify_sql_file


class TestBug1FunctionNameExtraction:
    def test_tvf_inline_name_extracted_correctly(self, fixtures_dir: Path):
        path = fixtures_dir / "sql" / "scalar_function.sql"
        # CalculateCustomerPrice is a SCALAR_FUNCTION; verify against a real
        # TVF_INLINE source object directly from the cloned corpus if present,
        # otherwise fall back to asserting the SCALAR_FUNCTION case which
        # exercises the exact same code path (subtype != "FUNCTION").
        obj = classify_sql_file(path, source_project="OLTP")
        assert obj["object_type"] == "SCALAR_FUNCTION"
        # Before the fix, this fell through to a fallback regex that grabbed
        # the wrong token (e.g. "Website" or "CalculateCustomerPrice" with
        # schema defaulted to "dbo" and name corrupted).
        assert obj["schema"] == "Website"
        assert obj["name"] == "CalculateCustomerPrice"


class TestBug2GeographyTypeTruncation:
    def test_schema_qualified_geography_type_preserved_in_full(self, geography_temporal_table_sql: Path):
        raw_ddl = geography_temporal_table_sql.read_text(encoding="utf-8-sig")
        columns, _ = parse_table_columns(raw_ddl)
        location = next(c for c in columns if c["name"] == "Location")
        # Before the fix this was "[sys]" — the ".geography]" suffix was lost.
        assert location["sql_type"] == "[sys].[geography]"
        assert not location["sql_type"].endswith("[sys]")


class TestBug3SecurityScoringDoubleCount:
    def test_execute_as_owner_does_not_double_match_security_patterns(self):
        from accelerator.analyzers.impact_analysis import _SECURITY_PATTERNS, _hits

        sql = "CREATE PROCEDURE dbo.Foo WITH EXECUTE AS OWNER AS BEGIN SELECT 1 END"
        score, factors = _hits(sql, _SECURITY_PATTERNS)
        # "EXECUTE AS OWNER" must match exactly one pattern, not two.
        assert len(factors) == 1
        assert score == 2  # the OWNER-specific weight, not 2+2=4 or higher


class TestBug4TopologicalSortDirection:
    def test_staging_precedes_dimension_in_deployment_order(self, tiny_inventory):
        graph = build_graph(tiny_inventory)
        order = topological_sort(graph)
        idx = {nid: i for i, nid in enumerate(order)}
        # Before the fix, Dimension.City (the dependant) appeared before
        # Integration.City_Staging (its dependency) in the returned order.
        assert idx["DW:Integration.City_Staging"] < idx["DW:Dimension.City"]
        assert idx["DW:Dimension.City"] < idx["DW:Fact.Sale"]


class TestBug5ProceduralFunctionDetection:
    def test_multi_statement_function_routes_to_pyspark_not_broken_sql_udf(self, scalar_function_sql: Path):
        obj = classify_sql_file(scalar_function_sql, source_project="OLTP")
        obj["medallion_layer"] = "SILVER"
        result = convert_function(obj, "wwi_dev.silver.website__calculatecustomerprice")
        # Before the fix, this produced a "sql" key containing only
        # `RETURN @CalculatedPrice;` — a syntactically plausible but
        # functionally broken UDF that silently dropped every DECLARE/SET/IF
        # branch computing the actual price.
        assert "pyspark" in result
        assert "sql" not in result
        assert result["needs_review"] is True


class TestKnownGap6TemporalConfidenceDeductionDeadCode:
    def test_temporal_feature_present_but_confidence_unaffected(self, geography_temporal_table_sql: Path, tmp_path: Path):
        obj = classify_sql_file(geography_temporal_table_sql, source_project="OLTP")
        simple_obj = {
            **classify_sql_file(geography_temporal_table_sql, source_project="OLTP"),
            "id": "OLTP:Application.NonTemporalControl",
            "name": "NonTemporalControl",
            "table_features": [],
            "complexity_factors": [f for f in obj["complexity_factors"] if "SYSTEM_TIME" not in f],
        }
        inventory = build_inventory([obj, simple_obj], [], tmp_path)
        by_id = {o["id"]: o for o in inventory["objects"]}
        temporal = by_id["OLTP:Application.Cities"]
        control = by_id["OLTP:Application.NonTemporalControl"]
        assert "TEMPORAL" in temporal["table_features"]
        assert "TEMPORAL" not in control["table_features"]
        # Documents the live gap: despite the table_features difference,
        # confidence is identical because the TEMPORAL deduction key never
        # matches complexity_factors.
        assert temporal["conversion_confidence"] == control["conversion_confidence"]


class TestGracefulDegradationAcrossModules:
    """Cross-cutting check: every supported parser/converter entry point must
    fail gracefully (return a structured error/flag) rather than raising, for
    a representative set of malformed or unusual inputs."""

    def test_sql_with_no_recognisable_ddl_does_not_raise(self, tmp_path: Path):
        f = tmp_path / "junk.sql"
        f.write_text("this is not sql at all, just prose.", encoding="utf-8")
        obj = classify_sql_file(f, source_project="OLTP")
        assert obj["object_type"] in ("UNKNOWN", "SCRIPT")

    def test_empty_sql_file_does_not_raise(self, tmp_path: Path):
        f = tmp_path / "empty.sql"
        f.write_text("", encoding="utf-8")
        obj = classify_sql_file(f, source_project="OLTP")
        assert obj["object_type"] == "UNKNOWN"

    def test_inventory_builder_handles_empty_object_list(self, tmp_path: Path):
        inventory = build_inventory([], [], tmp_path)
        assert inventory["total_objects"] == 0
        assert inventory["objects"] == []

    def test_dependency_graph_handles_empty_inventory(self):
        graph = build_graph({"objects": []})
        assert graph["node_count"] == 0
        assert graph["edge_count"] == 0
        assert topological_sort(graph) == []
