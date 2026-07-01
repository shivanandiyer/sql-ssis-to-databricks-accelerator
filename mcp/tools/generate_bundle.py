"""
mcp/tools/generate_bundle.py
Handler for the generate_bundle MCP tool.

NOTE ON IMPLEMENTATION: the original spec named bundle_generator.py and
env_config_generator.py under accelerator/deploy/, which never existed as
real modules (accelerator/deploy/ was an empty stub package, since removed).
The real implementation lives in deploy/generate_deployment_bundle.py at the
repo root — this handler dynamically loads its render_job_yaml() function
(deploy/ has no __init__.py and isn't importable as a package, by design —
see deploy/generate_deployment_bundle.py's own docstring) rather than
reimplementing bundle YAML rendering a second time.
"""

from __future__ import annotations

import importlib.util
import json
import logging
import time
from pathlib import Path
from types import ModuleType
from typing import Any

logger = logging.getLogger(__name__)

_ENV_CATALOG = {"dev": "wwi_dev", "test": "wwi_test", "prod": "wwi_prod"}
_REPO_ROOT = Path(__file__).resolve().parents[2]  # mcp/tools/ -> mcp/ -> repo root


def _load_bundle_generator_module() -> ModuleType:
    script_path = _REPO_ROOT / "deploy" / "generate_deployment_bundle.py"
    spec = importlib.util.spec_from_file_location("generate_deployment_bundle", script_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"could not load {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


async def handle_generate_bundle(
    manifest_path: str,
    env: str = "dev",
    output_path: str = "./bundle",
) -> dict[str, Any]:
    """Generate a Databricks Asset Bundle job resource for deployment.

    Args:
        manifest_path: Path to inventory.json produced by parse_source (used
            to locate workflow_spec.json, expected alongside it or in the
            sibling output/ directory).
        env: Target environment — dev | test | prod.
        output_path: Directory to write the bundle resource YAML to.

    Returns:
        {bundle_path, deploy_script_path, environment} on success, or
        {error: True, message: str} on failure.
    """
    logger.info(
        "tool_call timestamp=%s tool=generate_bundle input=%s",
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        json.dumps({"manifest_path": manifest_path, "env": env, "output_path": output_path}),
    )
    try:
        if env not in _ENV_CATALOG:
            return {"error": True, "message": f"env must be one of dev|test|prod, got {env!r}"}

        manifest_file = Path(manifest_path)
        if not manifest_file.exists():
            return {"error": True, "message": f"manifest_path does not exist: {manifest_path}"}

        # workflow_spec.json is produced by convert_ssis into its own
        # output_path, which may differ from manifest_path's directory —
        # check both the manifest's directory and the conventional ./output/.
        candidates = [
            manifest_file.parent / "workflow_spec.json",
            _REPO_ROOT / "output" / "workflow_spec.json",
        ]
        workflow_spec_file = next((c for c in candidates if c.exists()), None)
        if workflow_spec_file is None:
            return {
                "error": True,
                "message": (
                    f"workflow_spec.json not found (looked at {', '.join(str(c) for c in candidates)}) "
                    "— run convert_ssis first"
                ),
            }

        spec = json.loads(workflow_spec_file.read_text(encoding="utf-8"))
        bundle_module = _load_bundle_generator_module()
        yaml_text = bundle_module.render_job_yaml(spec)
        yaml_text = yaml_text.replace("${var.catalog}", _ENV_CATALOG[env])

        out_dir = Path(output_path) / "resources"
        out_dir.mkdir(parents=True, exist_ok=True)
        job_name = spec.get("name", "job")
        bundle_file = out_dir / f"{job_name}.job.yml"
        bundle_file.write_text(yaml_text, encoding="utf-8")

        deploy_script = _REPO_ROOT / "deploy" / "deploy.sh"

        return {
            "bundle_path": str(bundle_file),
            "deploy_script_path": str(deploy_script),
            "environment": env,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("generate_bundle failed")
        return {"error": True, "message": str(exc)}
