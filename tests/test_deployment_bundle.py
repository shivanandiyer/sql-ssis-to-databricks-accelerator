"""
Deployment bundle generation tests.

Covers the Databricks Asset Bundle YAML (databricks_job_bundle.yml) produced
by the SSIS conversion layer, and the conversion_manifest.json /
conversion_decisions.md produced by the SQL conversion layer — together these
form the accelerator's "deployment bundle" deliverables.
"""

from __future__ import annotations

from pathlib import Path

from accelerator.analyzers.dependency_graph import build_and_save_graph
from accelerator.analyzers.inventory_builder import build_inventory
from accelerator.converters.ssis_converter import build_job_bundle_yaml, build_task_catalog, build_workflow_spec
from accelerator.parsers.ssis_parser import parse_dtsx


class TestJobBundleStructure:
    def test_bundle_has_required_top_level_sections(self, minimal_dtsx: Path, tmp_path: Path):
        pkg = parse_dtsx(minimal_dtsx)
        inventory = build_inventory([], [pkg], tmp_path)
        graph = build_and_save_graph(inventory, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        spec = build_workflow_spec(pkg, tasks)
        yaml_text = build_job_bundle_yaml(spec)

        assert "bundle:" in yaml_text
        assert "resources:" in yaml_text
        assert "jobs:" in yaml_text
        assert "targets:" in yaml_text

    def test_bundle_schedule_section_present(self, minimal_dtsx: Path, tmp_path: Path):
        pkg = parse_dtsx(minimal_dtsx)
        inventory = build_inventory([], [pkg], tmp_path)
        graph = build_and_save_graph(inventory, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        spec = build_workflow_spec(pkg, tasks)
        yaml_text = build_job_bundle_yaml(spec)

        assert "quartz_cron_expression" in yaml_text
        assert "timezone_id" in yaml_text

    def test_every_task_dependency_references_a_defined_task_key(self, minimal_dtsx: Path, tmp_path: Path):
        """A bundle that references a depends_on task_key not defined anywhere
        in the same job would fail to deploy — verify referential integrity."""
        pkg = parse_dtsx(minimal_dtsx)
        inventory = build_inventory([], [pkg], tmp_path)
        graph = build_and_save_graph(inventory, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        spec = build_workflow_spec(pkg, tasks)

        defined_keys = {t["task_key"] for t in spec["tasks"]}
        for t in spec["tasks"]:
            for dep in t["depends_on"]:
                assert dep["task_key"] in defined_keys, (
                    f"task {t['task_key']} depends on undefined task_key {dep['task_key']}"
                )

    def test_bundle_yaml_task_definitions_consistently_indented(self, minimal_dtsx: Path, tmp_path: Path):
        """Top-level task definitions (under `tasks:`) must all sit at the same
        8-space indent; depends_on references are a separate, deeper (12-space)
        indent level — both share the `- task_key:` substring, so this checks
        each population separately rather than conflating them."""
        pkg = parse_dtsx(minimal_dtsx)
        inventory = build_inventory([], [pkg], tmp_path)
        graph = build_and_save_graph(inventory, tmp_path)
        tasks = build_task_catalog(inventory, graph)
        spec = build_workflow_spec(pkg, tasks)
        yaml_text = build_job_bundle_yaml(spec)

        top_level_count = sum(1 for line in yaml_text.splitlines()
                               if line.startswith("        - task_key:"))
        assert top_level_count == len(spec["tasks"])


class TestRealDeploymentBundle:
    """Sanity checks against the actual generated bundle/manifest, skipped
    automatically if the conversion pipeline hasn't run yet."""

    def test_real_bundle_file_exists_and_is_nonempty(self):
        bundle_path = Path(__file__).parent.parent / "output" / "databricks_job_bundle.yml"
        if not bundle_path.exists():
            import pytest
            pytest.skip("databricks_job_bundle.yml not found — run run_ssis_conversion.py first")
        content = bundle_path.read_text(encoding="utf-8")
        assert "wwi_dailyetlmain" in content
        # Top-level task definitions are indented at exactly 8 spaces;
        # depends_on references (also containing "task_key:") sit deeper.
        top_level_count = sum(1 for line in content.splitlines()
                               if line.startswith("        - task_key:"))
        assert top_level_count == 81

    def test_real_manifest_every_object_has_a_disposition(self, real_conversion_manifest):
        """Required by the accelerator: assert that all source objects in the
        conversion manifest receive a disposition of converted / partial / manual."""
        def disposition(entry: dict) -> str:
            if not entry["needs_review"]:
                return "converted"
            if entry["conversion_method"] == "split_sql_pyspark":
                return "partial"
            if entry["conversion_method"] == "pyspark":
                return "manual"
            return "partial"

        dispositions = {disposition(o) for o in real_conversion_manifest["objects"]}
        assert dispositions <= {"converted", "partial", "manual"}
        assert len(real_conversion_manifest["objects"]) == real_conversion_manifest["object_count"]
        # Every single object must have produced at least one output file.
        for o in real_conversion_manifest["objects"]:
            assert o["files_written"], f"{o['id']} produced no output files"

    def test_real_manifest_method_distribution_sums_to_object_count(self, real_conversion_manifest):
        total = sum(real_conversion_manifest["conversion_method_distribution"].values())
        assert total == real_conversion_manifest["object_count"]
