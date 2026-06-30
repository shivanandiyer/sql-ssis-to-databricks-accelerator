# Deployment Guide

This guide covers everything needed to deploy a converted SQL Server/SSIS
solution onto Databricks using this repository's `bundle/`, `conf/`, and
`deploy/` folders (all at the repo root, alongside this `docs/` folder): the
Asset Bundle, environment-specific configuration, and the
deployment/promotion/rollback tooling. It assumes the accelerator's
conversion steps have already run (`run_analysis.py` →
`run_impact_analysis.py` → `run_target_state_design.py` →
`run_conversion.py` → `run_ssis_conversion.py`) and `output/` contains the
converted SQL/PySpark/notebook assets these deployment artifacts reference.

## Folder structure

```
bundle/                          Databricks Asset Bundle
  databricks.yml                 Top-level bundle config: variables, targets (dev/test/prod)
  resources/
    wwi_daily_etl_main.job.yml   Workflow job — generated from output/workflow_spec.json,
                                  never hand-edited (see deploy/generate_deployment_bundle.py)
    sql_warehouse.yml            Serverless SQL warehouse resource
  src/
    wwi_accelerator/             Shared runtime package (secret/catalog/watermark helpers)
      __init__.py
      common.py
    tests/
      test_common.py             Unit tests for the runtime package
    pyproject.toml                Wheel packaging for wwi_accelerator

conf/                             Environment parameterization
  dev.yml / test.yml / prod.yml   Per-environment catalog, schema, secret scope, job settings
  secrets.md                      Secret scope/key documentation and creation commands

deploy/                           Deployment tooling
  deploy.sh                       Full deploy pipeline: test -> validate -> SQL DDL -> bundle deploy -> smoke test
  promote.sh                      Environment promotion (dev->test, test->prod) with a pre-prod checklist gate
  generate_deployment_bundle.py   Regenerates bundle/resources/wwi_daily_etl_main.job.yml from output/workflow_spec.json
  sql_deploy.py                   Idempotent DDL deployment, dependency-ordered
  validate_deployment.py          Post-deploy smoke test (Tier 1 checks from outputs/test_matrix.csv)
  run_tests.sh                    Pre-deploy test gate (accelerator suite + runtime package suite)
  rollback.md                     Code and data rollback runbook

output/                           Converted assets (produced by run_conversion.py / run_ssis_conversion.py)
  databricks_sql/<layer>/*.sql    Converted tables/views/procedures, referenced by sql_task entries
  pyspark/*.py                    Converted procedural logic requiring PySpark
  ssis_tasks/*.py                 Converted SSIS Data Flow / Expression tasks, referenced by notebook_task entries
  review_required/*.md            Objects flagged for manual review (not deployed as-is)
```

## Prerequisites

- Databricks CLI ≥ 0.220 (`databricks bundle` support)
- A Databricks workspace per environment (or one workspace with environment
  isolation via separate catalogs — `bundle/databricks.yml`'s per-target
  `workspace.host` supports either)
- Unity Catalog enabled, with permission to create catalogs `wwi_dev`,
  `wwi_test`, `wwi_prod` (or pre-created catalogs the deploying principal can
  write to)
- Secret scopes created per `conf/secrets.md` before the first deploy
- Python 3.10+ with `pytest` for `deploy/run_tests.sh`

## Cluster / compute recommendation

**Serverless for everything.** Both the SQL warehouse
(`bundle/resources/sql_warehouse.yml`) and the notebook tasks
(`environment_key: wwi_serverless_env` in the job resource) use Databricks
Serverless compute, not classic job clusters. Rationale:

- The workload is a single daily batch window (~30-60 min), not continuous —
  serverless avoids paying for an idle warehouse/cluster between runs.
- WWI reference data volumes (low-millions of rows per table) don't justify
  a dedicated always-on cluster.
- Serverless starts in seconds, which matters across a job with 81 tasks —
  classic cluster cold-start latency would otherwise be paid repeatedly.

**When to reconsider:** if a future source corpus is much larger (tens of
billions of rows) or has stricter customer-managed-networking/VPC
requirements that serverless doesn't yet support in your cloud/region, fall
back to a classic autoscaling job cluster — `bundle/resources/sql_warehouse.yml`
documents this tradeoff inline.

## Deploying

```bash
# First deploy to dev
./deploy/deploy.sh dev

# After dev validation, promote to test
./deploy/promote.sh dev test

# After test sign-off (see conf/test.yml checklist), promote to prod
./deploy/promote.sh test prod
```

Each `deploy.sh` run is the full repeatable pipeline: pre-deploy tests →
bundle regeneration from the latest conversion output → `databricks bundle
validate` → idempotent SQL DDL deploy → `databricks bundle deploy` →
post-deploy smoke test. Every step can be re-run safely (see Idempotency below).

## Environment parameterization

`bundle/databricks.yml` defines `catalog`, `sql_warehouse_id`,
`job_pause_status`, and `alert_email` as bundle variables, with per-target
values set in the `targets:` block and mirrored in `conf/<env>.yml` (kept as
the single source of truth for anything `deploy/` scripts need to read
outside of `databricks bundle` itself). Promoting an environment means
deploying the same job/code definition with different variable values —
**never** different code paths per environment.

| Variable | dev | test | prod |
|---|---|---|---|
| `catalog` | `wwi_dev` | `wwi_test` | `wwi_prod` |
| `job_pause_status` | `PAUSED` | `PAUSED` | `UNPAUSED` |
| Secret scope | `wwi-source-db-dev` | `wwi-source-db-test` | `wwi-source-db-prod` |

## Secret references

See `conf/secrets.md` for the full list and creation commands. Summary: one
secret scope per environment (`wwi-source-db-<env>`) holding the source SQL
Server JDBC credentials. The destination (Unity Catalog) needs no secret —
it uses Databricks-native service principal / OAuth identity. Generated
PySpark tasks derive the scope name from the `environment` task parameter
(never hardcoded), so the same code runs unmodified across all three
environments.

## Idempotency

- **Tables**: `CREATE TABLE IF NOT EXISTS` — re-running `sql_deploy.py`
  never fails or duplicates a table.
- **Views**: `CREATE OR REPLACE VIEW` — always reflects the latest
  conversion output.
- **Staging loads**: overwrite-mode Delta writes (`df.write...mode("overwrite")`)
  — re-running an extract task produces the same end state, not duplicate rows.
- **Watermark advance**: a `MERGE` (see `bundle/src/wwi_accelerator/common.py`'s
  `advance_watermark`), not an `INSERT` — re-running the same watermark
  advance is a no-op, not a duplicate watermark row.
- **Bundle deploy**: `databricks bundle deploy` is declarative — redeploying
  identical bundle state changes nothing in the workspace.

The one explicitly **non**-idempotent case: SCD2 MERGE logic in
`output/pyspark`/converted procedures, if a manual-redesign object's MERGE
condition is implemented incorrectly, could insert duplicate "current" rows
on re-run. This is exactly why `manual_intervention_list.md`'s sign-off
checklist requires a reconciliation test before any manual-redesign object
is trusted in production — idempotency for those objects is a property of
the human-reviewed implementation, not guaranteed by the accelerator alone.

## Promotion across environments

`deploy/promote.sh` enforces a one-directional path (`dev -> test -> prod`),
records the promoted git commit SHA for rollback reference, and gates
promotion to prod behind the checklist in `conf/test.yml`
(`required_before_promotion_to_prod`). It does not move data — each
environment's Bronze layer is independently fed by that environment's own
secret-scoped source connection, so promoting code never promotes data.

## Rollback

See `deploy/rollback.md` for the full runbook. Summary: code/job rollback is
a `git checkout` + redeploy (bundle state is fully declarative); data
rollback uses Delta `RESTORE TABLE ... VERSION/TIMESTAMP AS OF`, applied in
**reverse** dependency order (Gold → Silver → Bronze) with the watermark
table restored to match — the most commonly forgotten step.

## Known limitations carried into this deployment design

- 119 SQL objects and several SSIS tasks are flagged `needs_review` (see
  `output/review_required/` and `manual_intervention_list.md`) — these are
  **not** safe to deploy as-is to test/prod. `sql_deploy.py` will still emit
  their DDL skeleton (with conversion-note comments) but a human must
  complete the implementation first; nothing in this deployment tooling
  blocks deploying an incomplete object, by design, so review status must be
  tracked separately (see `outputs/object_complexity_scores.json`'s
  `classification` field) rather than gated automatically.
- `validate_deployment.py`'s smoke test is Tier 1 only (schema existence). A
  full Tier 2/3 reconciliation pass (per `test_strategy.md`) should be run
  manually before promoting to prod, not assumed complete because the smoke
  test passed.
