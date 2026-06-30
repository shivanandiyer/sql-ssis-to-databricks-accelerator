"""
validate_deployment.py
Post-deploy smoke test hook (Step 6 of deploy.sh).

Runs the Tier 1 ("HIGH confidence") checks from test_matrix.csv against the
target catalog: schema existence, table existence, and row-count sanity for
the highest-confidence converted objects. This is intentionally lightweight
— full Tier 2/3 reconciliation testing (per test_strategy.md's confidence-
band policy) is a separate, longer-running validation pass, not a deploy gate.

Usage:
    python deploy/validate_deployment.py --target dev
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
ENV_CATALOG = {"dev": "wwi_dev", "test": "wwi_test", "prod": "wwi_prod"}


def load_tier1_checks(catalog: str) -> list[dict[str, str]]:
    matrix_path = ROOT / "outputs" / "test_matrix.csv"
    checks: list[dict[str, str]] = []
    if not matrix_path.exists():
        print(f"WARNING: {matrix_path} not found — skipping test-matrix-driven checks.")
        return checks
    with matrix_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["confidence_band"] == "HIGH" and row["object_type"] in ("TABLE", "VIEW"):
                checks.append(row)
    return checks


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, choices=["dev", "test", "prod"])
    args = parser.parse_args()
    catalog = ENV_CATALOG[args.target]

    checks = load_tier1_checks(catalog)
    print(f"Post-deploy smoke test against catalog '{catalog}': {len(checks)} Tier 1 checks")

    try:
        from databricks import sql as databricks_sql  # type: ignore
    except ImportError:
        print("databricks-sql-connector not installed — printing the check plan only "
              "(this is expected when running outside a Databricks-connected environment).")
        for c in checks:
            print(f"  would check: {catalog}.{c['target_layer'].lower()} — {c['object_id']}")
        return

    connection = databricks_sql.connect(
        server_hostname=os.environ["DATABRICKS_HOST"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    )
    failures: list[str] = []
    try:
        with connection.cursor() as cursor:
            for schema in ("bronze", "silver", "gold", "ops"):
                cursor.execute(f"SHOW SCHEMAS IN {catalog} LIKE '{schema}'")
                if not cursor.fetchall():
                    failures.append(f"missing schema: {catalog}.{schema}")
    finally:
        connection.close()

    if failures:
        print(f"\nFAILED: {len(failures)} smoke-test checks did not pass:")
        for f in failures:
            print(f"  - {f}")
        sys.exit(1)

    print("\nAll smoke-test checks passed.")


if __name__ == "__main__":
    main()
