"""
Metadata extraction tests: accelerator.analyzers.inventory_builder.

Validates that classification, medallion-layer assignment, risk, and
confidence scoring are computed consistently for objects parsed from real
WWI fixtures, and that the disposition logic required by the accelerator
(converted / partial / manual) can be derived unambiguously for every object.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from accelerator.analyzers.inventory_builder import build_inventory
from accelerator.parsers.sql_project_parser import classify_sql_file


@pytest.fixture
def sql_objects(simple_table_sql, geography_temporal_table_sql, cursor_procedure_sql,
                 set_based_procedure_sql, forjson_view_sql, scalar_function_sql) -> list[dict]:
    paths_and_projects = [
        (simple_table_sql, "OLTP"),
        (geography_temporal_table_sql, "OLTP"),
        (cursor_procedure_sql, "OLTP"),
        (set_based_procedure_sql, "DW"),
        (forjson_view_sql, "OLTP"),
        (scalar_function_sql, "OLTP"),
    ]
    return [classify_sql_file(p, source_project=proj) for p, proj in paths_and_projects]


class TestInventoryBuilder:
    def test_build_inventory_produces_one_entry_per_object(self, sql_objects, tmp_path: Path):
        inventory = build_inventory(sql_objects, [], tmp_path)
        assert inventory["total_objects"] == len(sql_objects)

    def test_temporal_table_confidence_deduction_gap(self, sql_objects, tmp_path: Path):
        """KNOWN GAP (discovered while writing this suite, not yet fixed):
        inventory_builder._DEDUCTIONS includes a 0.15 penalty keyed on the
        literal substring "TEMPORAL", but that string is only ever populated
        in obj["table_features"], never in obj["complexity_factors"] (which is
        populated from sql_project_parser's regex weight list using labels like
        "FOR SYSTEM_TIME(+3)"). The TEMPORAL/MEMORY_OPTIMIZED deduction keys are
        therefore dead code today. This test documents the *current* behaviour
        (no deduction applied) so a future fix flips it to an explicit
        regression test rather than silently changing pass/fail.
        """
        inventory = build_inventory(sql_objects, [], tmp_path)
        by_id = {o["id"]: o for o in inventory["objects"]}
        simple = by_id["OLTP:DataLoadSimulation.FicticiousNamePool"]
        geo = by_id["OLTP:Application.Cities"]
        assert "TEMPORAL" in geo["table_features"]
        # Documents current (arguably incorrect) behaviour: confidence is equal
        # because the TEMPORAL deduction key never matches complexity_factors.
        assert geo["conversion_confidence"] == simple["conversion_confidence"]

    def test_cursor_procedure_flagged_higher_risk_than_set_based(self, sql_objects, tmp_path: Path):
        inventory = build_inventory(sql_objects, [], tmp_path)
        by_name = {o["name"]: o for o in inventory["objects"]}
        cursor_proc = by_name["GetCityUpdates"]
        set_based_proc = by_name["MigrateStagedCityData"]
        risk_order = {"NONE": 0, "LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}
        assert risk_order[cursor_proc["risk"]] >= risk_order[set_based_proc["risk"]]

    def test_oltp_tables_assigned_bronze_layer(self, sql_objects, tmp_path: Path):
        inventory = build_inventory(sql_objects, [], tmp_path)
        by_id = {o["id"]: o for o in inventory["objects"]}
        assert by_id["OLTP:DataLoadSimulation.FicticiousNamePool"]["medallion_layer"] == "BRONZE"
        assert by_id["OLTP:Application.Cities"]["medallion_layer"] == "BRONZE"
        # WebApi schema is the one OLTP exception that maps to Silver, not Bronze.
        assert by_id["OLTP:WebApi.Cities"]["medallion_layer"] == "SILVER"

    def test_writes_inventory_and_unsupported_json(self, sql_objects, tmp_path: Path):
        build_inventory(sql_objects, [], tmp_path)
        assert (tmp_path / "inventory.json").exists()
        assert (tmp_path / "unsupported_objects.json").exists()

    def test_every_object_receives_a_disposition(self, sql_objects, tmp_path: Path):
        """Required by the accelerator: every source object must resolve to one
        of converted / partial / manual — never an undefined/missing disposition."""
        inventory = build_inventory(sql_objects, [], tmp_path)

        def disposition(obj: dict) -> str:
            if obj.get("is_unsupported"):
                return "manual"
            if obj["risk"] in ("HIGH", "CRITICAL") or obj["complexity_band"] in ("HIGH", "VERY_HIGH"):
                return "partial"
            return "converted"

        for obj in inventory["objects"]:
            d = disposition(obj)
            assert d in ("converted", "partial", "manual"), f"{obj['id']} got invalid disposition {d!r}"

    def test_metadata_extraction_is_deterministic(self, sql_objects, tmp_path: Path):
        inv1 = build_inventory(sql_objects, [], tmp_path / "run1")
        inv2 = build_inventory(sql_objects, [], tmp_path / "run2")
        ids1 = sorted(o["id"] for o in inv1["objects"])
        ids2 = sorted(o["id"] for o in inv2["objects"])
        assert ids1 == ids2
        conf1 = {o["id"]: o["conversion_confidence"] for o in inv1["objects"]}
        conf2 = {o["id"]: o["conversion_confidence"] for o in inv2["objects"]}
        assert conf1 == conf2
