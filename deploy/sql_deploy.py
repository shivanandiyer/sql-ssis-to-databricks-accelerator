"""
sql_deploy.py
Applies the converted Databricks SQL DDL (output/databricks_sql/**/*.sql) to
a target environment's Unity Catalog catalog, in dependency order.

Idempotency: every generated table DDL uses `CREATE TABLE IF NOT EXISTS` and
every view uses `CREATE OR REPLACE VIEW` (see accelerator/converters/
sql_converter.py) — re-running this script against an already-deployed
catalog is always safe and a no-op for unchanged objects.

Ordering: reads outputs/dependencies.json's topological_order (dependencies
before dependants — see accelerator/analyzers/dependency_graph.py) so a
Dimension table is never created before the Bronze staging table it depends
on, and a Fact table is never created before its Dimension tables.

Usage:
    python deploy/sql_deploy.py --target dev --plan-only
    python deploy/sql_deploy.py --target dev --apply
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
OUTPUTS_DIR = ROOT / "outputs"
OUTPUT_DIR = ROOT / "output"

ENV_CATALOG = {"dev": "wwi_dev", "test": "wwi_test", "prod": "wwi_prod"}


def _find_sql_file_for_object(obj_id: str, inventory_by_id: dict[str, Any]) -> Path | None:
    obj = inventory_by_id.get(obj_id)
    if not obj or obj.get("object_type") not in ("TABLE", "VIEW"):
        return None
    layer = obj.get("medallion_layer", "BRONZE").lower()
    schema_slug = obj.get("schema", "default").lower().replace(" ", "_")
    name_slug = obj.get("name", "unknown").lower().replace(" ", "_")
    proj = obj.get("source_project", "")
    table_name = f"{schema_slug}__{name_slug}" if proj == "OLTP" else name_slug
    candidate = OUTPUT_DIR / "databricks_sql" / layer / f"{table_name}.sql"
    return candidate if candidate.exists() else None


def build_deploy_plan() -> list[dict[str, Any]]:
    inventory = json.loads((OUTPUTS_DIR / "inventory.json").read_text(encoding="utf-8"))
    dependencies = json.loads((OUTPUTS_DIR / "dependencies.json").read_text(encoding="utf-8"))
    inventory_by_id = {o["id"]: o for o in inventory["objects"]}

    plan: list[dict[str, Any]] = []
    seen: set[str] = set()
    for obj_id in dependencies["topological_order"]:
        sql_file = _find_sql_file_for_object(obj_id, inventory_by_id)
        if sql_file and obj_id not in seen:
            seen.add(obj_id)
            plan.append({"object_id": obj_id, "sql_file": str(sql_file.relative_to(ROOT))})
    return plan


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", required=True, choices=["dev", "test", "prod"])
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--plan-only", action="store_true", help="Print the deploy plan, apply nothing.")
    group.add_argument("--apply", action="store_true", help="Apply the deploy plan via Databricks SQL.")
    args = parser.parse_args()

    catalog = ENV_CATALOG[args.target]
    plan = build_deploy_plan()

    print(f"Deploy plan for target '{args.target}' (catalog: {catalog}): {len(plan)} objects")
    print(f"{'#':>4}  {'Object':<45} {'SQL File'}")
    for i, item in enumerate(plan, 1):
        print(f"{i:>4}  {item['object_id']:<45} {item['sql_file']}")

    if args.plan_only:
        return

    try:
        from databricks import sql as databricks_sql  # type: ignore
    except ImportError:
        print("\nERROR: databricks-sql-connector not installed. Install it (or run this step via a "
              "Databricks SQL task instead of locally) before using --apply.", file=sys.stderr)
        sys.exit(1)

    print(f"\nApplying {len(plan)} DDL statements to catalog '{catalog}'...")
    # Connection details are environment-specific — sourced from the same
    # secret scope documented in conf/secrets.md, not hardcoded here.
    import os
    connection = databricks_sql.connect(
        server_hostname=os.environ["DATABRICKS_HOST"],
        http_path=os.environ["DATABRICKS_HTTP_PATH"],
        access_token=os.environ["DATABRICKS_TOKEN"],
    )
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"CREATE CATALOG IF NOT EXISTS {catalog}")
            for schema in ("bronze", "silver", "gold", "ops"):
                cursor.execute(f"CREATE SCHEMA IF NOT EXISTS {catalog}.{schema}")
            for item in plan:
                sql_text = (ROOT / item["sql_file"]).read_text(encoding="utf-8")
                sql_text = sql_text.replace("wwi_<env>", catalog)
                # Skip pure comment blocks (review-flagged objects with no
                # executable DDL above the "-- Conversion notes:" marker).
                executable = sql_text.split("-- Conversion notes:")[0].strip()
                if executable:
                    cursor.execute(executable)
                    print(f"  applied: {item['object_id']}")
    finally:
        connection.close()

    print("Done.")


if __name__ == "__main__":
    main()
