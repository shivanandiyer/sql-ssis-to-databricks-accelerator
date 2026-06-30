"""
Architecture recommendation tests: accelerator.docs.target_state_design.

Covers the default medallion recommendation, the user-driven architecture
override mechanism, medallion layer mapping, and Unity Catalog naming.
"""

from __future__ import annotations

from pathlib import Path

from accelerator.docs.target_state_design import (
    build_medallion_mapping,
    build_unity_catalog_design,
    decide_architecture,
    generate_target_state_design,
)


class TestArchitectureDecision:
    def test_medallion_is_strong_fit_when_scd2_and_staging_present(self, tiny_inventory):
        decision = decide_architecture(tiny_inventory, override=None)
        assert decision["chosen_architecture"] == "medallion"
        assert decision["is_default"] is True
        assert decision["evaluated_alternatives"]["medallion"]["fit"] == "STRONG"
        assert decision["signals_observed"]["has_scd2_dimensions"] is True
        assert decision["signals_observed"]["has_staging_layer"] is True

    def test_user_driven_override_is_recorded_and_not_silently_ignored(self, tiny_inventory):
        decision = decide_architecture(tiny_inventory, override="data_vault")
        assert decision["chosen_architecture"] == "data_vault"
        assert decision["is_default"] is False
        # Medallion's evaluation must still be documented even when overridden.
        assert "medallion" in decision["evaluated_alternatives"]
        assert decision["evaluated_alternatives"]["medallion"]["fit"] == "STRONG"

    def test_all_three_architectures_always_evaluated_regardless_of_choice(self, tiny_inventory):
        for override in (None, "medallion", "data_vault", "one_big_table"):
            decision = decide_architecture(tiny_inventory, override=override)
            assert set(decision["evaluated_alternatives"].keys()) == {
                "medallion", "data_vault", "one_big_table"
            }

    def test_decision_is_deterministic(self, tiny_inventory):
        d1 = decide_architecture(tiny_inventory, override=None)
        d2 = decide_architecture(tiny_inventory, override=None)
        assert d1 == d2


class TestMedallionMapping:
    def test_only_data_bearing_objects_included(self, tiny_inventory):
        rows = build_medallion_mapping(tiny_inventory)
        assert len(rows) == 4  # all 4 tiny_inventory fixtures are TABLE objects
        assert all(r["source_object_type"] == "TABLE" for r in rows)

    def test_layer_matches_source_medallion_layer(self, tiny_inventory):
        rows = build_medallion_mapping(tiny_inventory)
        by_id = {r["source_id"]: r for r in rows}
        assert by_id["DW:Integration.City_Staging"]["layer"] == "BRONZE"
        assert by_id["DW:Dimension.City"]["layer"] == "SILVER"
        assert by_id["DW:Fact.Sale"]["layer"] == "GOLD"

    def test_target_fqn_uses_layer_as_schema(self, tiny_inventory):
        rows = build_medallion_mapping(tiny_inventory)
        by_id = {r["source_id"]: r for r in rows}
        assert by_id["DW:Dimension.City"]["target_fqn"] == "wwi_<env>.silver.city"
        assert by_id["DW:Fact.Sale"]["target_fqn"] == "wwi_<env>.gold.sale"

    def test_dw_table_names_do_not_carry_redundant_schema_prefix(self, tiny_inventory):
        """Dimension.City -> silver.city, not silver.dimension__city — the DW
        schema is already implied by the target layer schema."""
        rows = build_medallion_mapping(tiny_inventory)
        by_id = {r["source_id"]: r for r in rows}
        assert by_id["DW:Dimension.City"]["target_table"] == "city"

    def test_mapping_is_deterministic(self, tiny_inventory):
        rows1 = build_medallion_mapping(tiny_inventory)
        rows2 = build_medallion_mapping(tiny_inventory)
        assert rows1 == rows2


class TestUnityCatalogDesign:
    def test_three_environments_defined(self):
        design = build_unity_catalog_design()
        assert design["environments"] == ["dev", "test", "prod"]

    def test_every_section_has_rationale_tradeoffs_and_assumptions(self):
        design = build_unity_catalog_design()
        for key, detail in design.items():
            if key == "environments":
                continue
            assert detail["rationale"]
            assert detail["tradeoffs"]
            assert detail["assumptions"]


class TestEndToEndGeneration:
    def test_generate_target_state_design_writes_all_four_outputs(self, tiny_inventory, tmp_path: Path):
        graph = {"nodes": {}, "edges": []}
        complexity_scores = {"objects": []}
        paths = generate_target_state_design(tiny_inventory, graph, complexity_scores, tmp_path)
        assert paths["medallion_mapping_csv"].exists()
        assert paths["target_state_mappings_json"].exists()
        assert paths["target_state_architecture_md"].exists()
        assert paths["orchestration_design_md"].exists()

    def test_override_propagates_into_written_json(self, tiny_inventory, tmp_path: Path):
        import json
        graph = {"nodes": {}, "edges": []}
        complexity_scores = {"objects": []}
        paths = generate_target_state_design(
            tiny_inventory, graph, complexity_scores, tmp_path, architecture_override="data_vault"
        )
        written = json.loads(paths["target_state_mappings_json"].read_text(encoding="utf-8"))
        assert written["architecture_decision"]["chosen_architecture"] == "data_vault"
        assert written["architecture_decision"]["is_default"] is False
