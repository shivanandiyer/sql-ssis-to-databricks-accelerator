"""
mcp/tools/run_validation.py
Handler for the run_validation MCP tool.

Invokes pytest as a subprocess (never imports pytest's internals directly —
keeps this handler's own failures, if any, clearly separate from test
failures) and writes a validation_summary.md next to the manifest.
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]  # mcp/tools/ -> mcp/ -> repo root

# Maps test_scope to the test file(s) that exercise that part of the pipeline.
_SCOPE_TARGETS = {
    "parsers": ["tests/test_parsers.py", "tests/test_metadata_extraction.py", "tests/test_dependency_graph.py"],
    "converters": ["tests/test_sql_conversion.py", "tests/test_ssis_mapping.py"],
    "deployment": ["tests/test_deployment_bundle.py", "tests/test_architecture_recommendation.py"],
    "all": ["tests/"],
}


async def handle_run_validation(manifest_path: str, test_scope: str = "all") -> dict[str, Any]:
    """Run end-to-end validation of all conversion outputs.

    Args:
        manifest_path: Path to inventory.json produced by parse_source — used
            only to confirm the pipeline has actually been run before
            validating it, and as the directory to write the summary into.
        test_scope: Which tests to run — all | parsers | converters | deployment.

    Returns:
        {passed, failed, partial, summary_path, ready_for_release} on
        success, or {error: True, message: str} on failure.
    """
    logger.info(
        "tool_call timestamp=%s tool=run_validation input=%s",
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        json.dumps({"manifest_path": manifest_path, "test_scope": test_scope}),
    )
    try:
        if test_scope not in _SCOPE_TARGETS:
            return {
                "error": True,
                "message": f"test_scope must be one of {'|'.join(_SCOPE_TARGETS)}, got {test_scope!r}",
            }

        manifest_file = Path(manifest_path)
        if not manifest_file.exists():
            return {"error": True, "message": f"manifest_path does not exist: {manifest_path}"}

        targets = _SCOPE_TARGETS[test_scope]
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "pytest", *targets, "-v",
            cwd=str(_REPO_ROOT),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await proc.communicate()
        stdout = stdout_bytes.decode("utf-8", errors="replace")

        passed = stdout.count(" PASSED")
        failed = stdout.count(" FAILED")
        # "Skipped" tests in this suite are real-pipeline-output checks that
        # auto-skip when the upstream pipeline hasn't produced that output yet
        # (see tests/conftest.py's _load_json_or_skip) — treated as "partial"
        # rather than pass/fail, since they're neither confirmed-good nor broken.
        partial = stdout.count(" SKIPPED")

        summary_path = manifest_file.parent / "validation_summary.md"
        summary_lines = [
            "# Validation Summary",
            "",
            f"- **Scope:** {test_scope} ({', '.join(targets)})",
            f"- **Passed:** {passed}",
            f"- **Failed:** {failed}",
            f"- **Skipped / partial:** {partial}",
            f"- **pytest exit code:** {proc.returncode}",
            "",
            "## pytest output (tail)",
            "",
            "```",
            stdout[-4000:],
            "```",
        ]
        summary_path.write_text("\n".join(summary_lines), encoding="utf-8")

        return {
            "passed": passed,
            "failed": failed,
            "partial": partial,
            "summary_path": str(summary_path),
            "ready_for_release": failed == 0,
        }
    except Exception as exc:  # noqa: BLE001
        logger.exception("run_validation failed")
        return {"error": True, "message": str(exc)}
