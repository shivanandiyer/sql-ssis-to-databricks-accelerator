"""
Unit test hook for the wwi_accelerator runtime package.

Run via:
    cd bundle/src && pytest tests/

Also wired as a pre-deploy gate in deploy/run_tests.sh — a deploy must not
proceed if these fail, since every generated task imports this module.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from wwi_accelerator.common import get_catalog, get_secret_scope


def test_secret_scope_naming_per_environment():
    assert get_secret_scope("dev") == "wwi-source-db-dev"
    assert get_secret_scope("test") == "wwi-source-db-test"
    assert get_secret_scope("prod") == "wwi-source-db-prod"


def test_catalog_naming_per_environment():
    assert get_catalog("dev") == "wwi_dev"
    assert get_catalog("prod") == "wwi_prod"


def test_secret_scope_and_catalog_never_collide_across_environments():
    envs = ["dev", "test", "prod"]
    scopes = {get_secret_scope(e) for e in envs}
    catalogs = {get_catalog(e) for e in envs}
    assert len(scopes) == 3
    assert len(catalogs) == 3
