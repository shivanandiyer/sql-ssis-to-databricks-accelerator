"""
Dependency graph tests: accelerator.analyzers.dependency_graph.

Uses small, hand-verifiable synthetic inventories (tiny_inventory,
cyclic_inventory from conftest.py) so expected edge counts and topological
order are known exactly, plus the real pipeline graph for scale checks.
"""

from __future__ import annotations

from pathlib import Path

from accelerator.analyzers.dependency_graph import (
    build_and_save_graph,
    build_graph,
    detect_cycles,
    export_dot,
    export_mermaid,
    extract_etl_lineage,
    topological_sort,
)


class TestGraphConstruction:
    def test_builds_one_node_per_object(self, tiny_inventory):
        graph = build_graph(tiny_inventory)
        assert graph["node_count"] == 4

    def test_resolves_known_dependency_chain(self, tiny_inventory):
        graph = build_graph(tiny_inventory)
        edges = {(e["from"], e["to"]) for e in graph["edges"]}
        assert ("DW:Dimension.City", "DW:Integration.City_Staging") in edges
        assert ("DW:Fact.Sale", "DW:Dimension.City") in edges

    def test_isolated_object_has_no_edges(self, tiny_inventory):
        graph = build_graph(tiny_inventory)
        sample_version_edges = [
            e for e in graph["edges"]
            if e["from"] == "DW:dbo.SampleVersion" or e["to"] == "DW:dbo.SampleVersion"
        ]
        assert sample_version_edges == []

    def test_fan_in_fan_out_computed_correctly(self, tiny_inventory):
        graph = build_graph(tiny_inventory)
        assert graph["nodes"]["DW:Integration.City_Staging"]["fan_in"] == 1
        assert graph["nodes"]["DW:Dimension.City"]["fan_out"] == 1
        assert graph["nodes"]["DW:Dimension.City"]["fan_in"] == 1
        assert graph["nodes"]["DW:Fact.Sale"]["fan_out"] == 1

    def test_self_reference_does_not_create_self_loop(self):
        inventory = {"objects": [{
            "id": "DW:dbo.X", "name": "X", "schema": "dbo", "object_type": "VIEW",
            "source_project": "DW", "medallion_layer": "SILVER", "complexity_band": "LOW",
            "risk": "NONE", "etl_semantics": [], "table_features": [],
            "references": {"tables": ["dbo.X"], "procedures": [], "functions": []},
            "raw_ddl": "CREATE VIEW dbo.X AS SELECT 1",
        }]}
        graph = build_graph(inventory)
        assert graph["edge_count"] == 0


class TestTopologicalSort:
    def test_dependencies_precede_dependants(self, tiny_inventory):
        graph = build_graph(tiny_inventory)
        order = topological_sort(graph)
        idx = {nid: i for i, nid in enumerate(order)}
        assert idx["DW:Integration.City_Staging"] < idx["DW:Dimension.City"]
        assert idx["DW:Dimension.City"] < idx["DW:Fact.Sale"]

    def test_includes_every_node_exactly_once(self, tiny_inventory):
        graph = build_graph(tiny_inventory)
        order = topological_sort(graph)
        assert len(order) == graph["node_count"]
        assert len(set(order)) == len(order)

    def test_cyclic_graph_still_returns_all_nodes(self, cyclic_inventory):
        graph = build_graph(cyclic_inventory)
        order = topological_sort(graph)
        assert set(order) == set(graph["nodes"].keys())


class TestCycleDetection:
    def test_acyclic_graph_reports_no_cycles(self, tiny_inventory):
        graph = build_graph(tiny_inventory)
        assert detect_cycles(graph) == []

    def test_two_node_cycle_detected(self, cyclic_inventory):
        graph = build_graph(cyclic_inventory)
        cycles = detect_cycles(graph)
        assert len(cycles) >= 1
        flat = {nid for cycle in cycles for nid in cycle}
        assert "DW:dbo.A" in flat
        assert "DW:dbo.B" in flat


class TestEtlLineage:
    def test_gold_and_silver_tables_are_lineage_terminals(self, tiny_inventory):
        graph = build_graph(tiny_inventory)
        lineage = extract_etl_lineage(graph, tiny_inventory)
        targets = {lin["target"] for lin in lineage}
        assert "DW:Dimension.City" in targets
        assert "DW:Fact.Sale" in targets
        # Bronze staging table is not a lineage terminal.
        assert "DW:Integration.City_Staging" not in targets

    def test_lineage_upstream_count_is_fan_in_not_fan_out(self, tiny_inventory):
        """Documents existing (Step 2) semantics: extract_etl_lineage's
        'upstream_count' field is literally node['fan_in'] — i.e. the number of
        *other objects that reference this target*, not the number of objects
        this target itself depends on. For Fact.Sale (which references
        Dimension.City but is referenced by nothing) that means upstream_count
        is 0, even though Fact.Sale clearly has one real upstream dependency.
        This labeling has been consistent since Step 2 and is already baked
        into current_state_documentation.md's published "Upstream Dependency
        Count" column — flagging here rather than silently changing it, since
        a fix would alter previously-delivered documentation output."""
        graph = build_graph(tiny_inventory)
        lineage = extract_etl_lineage(graph, tiny_inventory)
        fact = next(lin for lin in lineage if lin["target"] == "DW:Fact.Sale")
        assert fact["upstream_count"] == graph["nodes"]["DW:Fact.Sale"]["fan_in"] == 0
        dimension = next(lin for lin in lineage if lin["target"] == "DW:Dimension.City")
        assert dimension["upstream_count"] == graph["nodes"]["DW:Dimension.City"]["fan_in"] == 1


class TestExportsAndPersistence:
    def test_export_dot_writes_valid_looking_file(self, tiny_inventory, tmp_path: Path):
        graph = build_graph(tiny_inventory)
        out = tmp_path / "graph.dot"
        export_dot(graph, out)
        content = out.read_text(encoding="utf-8")
        assert content.startswith("digraph")
        assert "DW:Fact.Sale" in content

    def test_export_mermaid_writes_valid_looking_file(self, tiny_inventory, tmp_path: Path):
        graph = build_graph(tiny_inventory)
        out = tmp_path / "graph.md"
        export_mermaid(graph, out)
        content = out.read_text(encoding="utf-8")
        assert "flowchart TD" in content

    def test_build_and_save_graph_writes_dependencies_json(self, tiny_inventory, tmp_path: Path):
        result = build_and_save_graph(tiny_inventory, tmp_path)
        assert (tmp_path / "dependencies.json").exists()
        assert result["has_cycles"] is False
        assert result["node_count"] == 4

    def test_graph_construction_is_deterministic(self, tiny_inventory):
        graph1 = build_graph(tiny_inventory)
        graph2 = build_graph(tiny_inventory)
        assert graph1["edge_count"] == graph2["edge_count"]
        edges1 = sorted((e["from"], e["to"], e["edge_type"]) for e in graph1["edges"])
        edges2 = sorted((e["from"], e["to"], e["edge_type"]) for e in graph2["edges"])
        assert edges1 == edges2


class TestRealPipelineGraph:
    """Scale/sanity checks against the actual generated dependencies.json,
    skipped automatically if the pipeline hasn't been run yet."""

    def test_real_graph_has_no_cycles(self, real_dependencies):
        assert real_dependencies["has_cycles"] is False
        assert real_dependencies["cycles"] == []

    def test_real_graph_topological_order_covers_all_nodes(self, real_dependencies):
        assert len(real_dependencies["topological_order"]) == real_dependencies["node_count"]

    def test_real_lineage_includes_known_dimension_and_fact(self, real_dependencies):
        targets = {lin["target_name"] for lin in real_dependencies["etl_lineage"]}
        assert "Dimension.City" in targets
        assert "Fact.Sale" in targets
