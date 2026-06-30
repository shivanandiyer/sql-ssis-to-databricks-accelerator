"""
SSIS mapping tests: accelerator.converters.ssis_converter.

Uses the minimal_dtsx fixture (a real "Load City Dimension" sequence
container re-wrapped as a standalone package) to keep these tests fast while
still exercising real WWI SSIS structure: precedence constraints, a data
flow task, an Execute SQL task, and connection managers/variables.
"""

from __future__ import annotations

from pathlib import Path

from accelerator.analyzers.dependency_graph import build_and_save_graph
from accelerator.analyzers.inventory_builder import build_inventory
from accelerator.converters.ssis_converter import (
    build_job_bundle_yaml,
    build_task_catalog,
    build_workflow_spec,
    map_connection_managers,
    map_variables,
)
from accelerator.parsers.ssis_parser import parse_conmgr, parse_dtsx


def _build_inventory_and_graph(minimal_dtsx: Path, tmp_path: Path):
    pkg = parse_dtsx(minimal_dtsx)
    inventory = build_inventory([], [pkg], tmp_path)
    graph = build_and_save_graph(inventory, tmp_path)
    return inventory, graph, pkg


class TestConnectionManagerMapping:
    def test_source_connection_mapped_to_secret_backed_jdbc(self, source_conmgr: Path):
        cm = parse_conmgr(source_conmgr)
        mapped = map_connection_managers([cm])
        entry = mapped[cm["guid"]]
        assert "secret" in entry["target_type"].lower() or "jdbc" in entry["target_type"].lower()
        assert entry["target_config"]["secret_scope"] == "wwi-source-db-<env>"

    def test_destination_connection_mapped_to_unity_catalog(self, dest_conmgr: Path):
        cm = parse_conmgr(dest_conmgr)
        mapped = map_connection_managers([cm])
        entry = mapped[cm["guid"]]
        assert "Unity Catalog" in entry["target_type"]
        assert "catalog" in entry["target_config"]

    def test_mapping_covers_every_connection_manager(self, source_conmgr: Path, dest_conmgr: Path):
        cms = [parse_conmgr(source_conmgr), parse_conmgr(dest_conmgr)]
        mapped = map_connection_managers(cms)
        assert len(mapped) == 2


class TestVariableMapping:
    def test_cutoff_variables_mapped_to_watermark_table(self):
        variables = [{"name": "LastETLCutoffTime", "namespace": "User", "value": "2016-04-11"}]
        mapped = map_variables(variables)
        assert "watermark" in mapped[0]["target"].lower()

    def test_lineage_key_not_passed_as_job_parameter(self):
        variables = [{"name": "LineageKey", "namespace": "User", "value": "0"}]
        mapped = map_variables(variables)
        assert "not passed as a parameter" in mapped[0]["target"]

    def test_every_variable_receives_a_target(self):
        variables = [
            {"name": "LastETLCutoffTime", "namespace": "User", "value": None},
            {"name": "LineageKey", "namespace": "User", "value": None},
            {"name": "TableName", "namespace": "User", "value": None},
            {"name": "TargetETLCutoffTime", "namespace": "User", "value": None},
        ]
        mapped = map_variables(variables)
        assert len(mapped) == 4
        assert all(m["target"] for m in mapped)


class TestTaskCatalogAndConfidence:
    def test_task_catalog_includes_all_ssis_object_types(self, minimal_dtsx: Path, tmp_path: Path):
        inventory, graph, pkg = _build_inventory_and_graph(minimal_dtsx, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        types = {t["object_type"] for t in tasks}
        assert "SSIS_SEQUENCE_CONTAINER" in types
        assert "SSIS_EXECUTE_SQL" in types
        assert "SSIS_DATA_FLOW" in types

    def test_sequence_container_inherits_precedence_dependencies(self, minimal_dtsx: Path, tmp_path: Path):
        inventory, graph, pkg = _build_inventory_and_graph(minimal_dtsx, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        # Every leaf Execute SQL / Data Flow task within the City Dimension
        # container should have at least one control-flow dependency, since
        # the source has a 4-step precedence chain (Truncate -> Cutoff ->
        # Extract -> Migrate, with a parallel TableName -> Lineage Key edge).
        leaf_tasks = [t for t in tasks if t["object_type"] in ("SSIS_EXECUTE_SQL", "SSIS_DATA_FLOW")]
        with_deps = [t for t in leaf_tasks if t["depends_on"]]
        assert len(with_deps) >= 3

    def test_simple_data_flow_gets_high_confidence(self, minimal_dtsx: Path, tmp_path: Path):
        inventory, graph, pkg = _build_inventory_and_graph(minimal_dtsx, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        data_flow_tasks = [t for t in tasks if t["object_type"] == "SSIS_DATA_FLOW"]
        assert data_flow_tasks
        assert all(t["confidence"] >= 0.7 for t in data_flow_tasks)

    def test_truncate_task_gets_test_recommendation_about_emptiness(self, minimal_dtsx: Path, tmp_path: Path):
        inventory, graph, pkg = _build_inventory_and_graph(minimal_dtsx, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        truncate_task = next(t for t in tasks if "Truncate" in (t["name"] or ""))
        assert "empty" in truncate_task["test_recommendation"].lower()

    def test_every_task_gets_a_confidence_and_test_recommendation(self, minimal_dtsx: Path, tmp_path: Path):
        inventory, graph, pkg = _build_inventory_and_graph(minimal_dtsx, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        for t in tasks:
            assert 0.0 <= t["confidence"] <= 1.0
            assert t["test_recommendation"]
            assert t["target_construct"]


class TestWorkflowSpecGeneration:
    def test_workflow_spec_has_one_task_per_leaf_ssis_task(self, minimal_dtsx: Path, tmp_path: Path):
        inventory, graph, pkg = _build_inventory_and_graph(minimal_dtsx, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        spec = build_workflow_spec(pkg, tasks)
        leaf_count = sum(1 for t in tasks if t["object_type"] in
                          ("SSIS_EXECUTE_SQL", "SSIS_DATA_FLOW", "SSIS_EXPRESSION"))
        assert len(spec["tasks"]) == leaf_count

    def test_workflow_spec_preserves_dependency_order(self, minimal_dtsx: Path, tmp_path: Path):
        inventory, graph, pkg = _build_inventory_and_graph(minimal_dtsx, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        spec = build_workflow_spec(pkg, tasks)
        migrate_task = next(t for t in spec["tasks"] if "migrate" in t["task_key"])
        # Migrate Staged City Data depends on Extract Updated City Data to Staging.
        dep_keys = {d["task_key"] for d in migrate_task["depends_on"]}
        assert any("extract" in k for k in dep_keys)

    def test_workflow_spec_is_deterministic(self, minimal_dtsx: Path, tmp_path: Path):
        inventory, graph, pkg = _build_inventory_and_graph(minimal_dtsx, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        spec1 = build_workflow_spec(pkg, tasks)
        spec2 = build_workflow_spec(pkg, tasks)
        keys1 = sorted(t["task_key"] for t in spec1["tasks"])
        keys2 = sorted(t["task_key"] for t in spec2["tasks"])
        assert keys1 == keys2


class TestJobBundleYaml:
    def test_bundle_yaml_contains_job_name_and_all_tasks(self, minimal_dtsx: Path, tmp_path: Path):
        inventory, graph, pkg = _build_inventory_and_graph(minimal_dtsx, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        spec = build_workflow_spec(pkg, tasks)
        yaml_text = build_job_bundle_yaml(spec)
        assert spec["name"] in yaml_text
        for t in spec["tasks"]:
            assert t["task_key"] in yaml_text

    def test_bundle_yaml_has_three_environment_targets(self, minimal_dtsx: Path, tmp_path: Path):
        inventory, graph, pkg = _build_inventory_and_graph(minimal_dtsx, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        spec = build_workflow_spec(pkg, tasks)
        yaml_text = build_job_bundle_yaml(spec)
        for env in ("dev", "test", "prod"):
            assert f"wwi_{env}" in yaml_text


class TestRealPipelineSsisOutputs:
    """Sanity checks against the actual generated SSIS conversion outputs."""

    def test_real_workflow_spec_has_81_leaf_tasks(self, real_workflow_spec):
        assert len(real_workflow_spec["tasks"]) == 81

    def test_real_workflow_spec_includes_both_connection_managers(self, real_workflow_spec):
        assert len(real_workflow_spec["connection_managers"]) == 2

    def test_real_workflow_spec_includes_all_four_variables(self, real_workflow_spec):
        assert len(real_workflow_spec["variables"]) == 4
